import os, sys, types, cPickle, stat, re, itertools, time, hashlib, math

##################################################
## Syntax extensions
##################################################

class BracketAccessMixin:
    """Allow access to attributes via dictionary syntax.  

    The name Mixin comes from the old CLOS (Common Lisp Object System)
    notion of an object that's not itself a fully specified, useful
    object, but is something that's added to other objects to given
    them specific functionality.  So here we have:

    class Foo (object, BraketAccessMixin):
        def __init__(self):
            self.bar = 42

        ... some implementation ...

    and then you can do
    >>> ff = Foo()
    >>> ff.bar = 53
    >>> ff['bar'] = 65

    or, more likely, something where the names are variables like:
    for name in ('bar', 'baz'):
        ff[name] = 53

    """
    def __getitem__(self, name):
        return getattr(self, name)

    def __setitem__(self, name, value):
        return setattr(self, name, value)

class SnooperMixin(object):
    """Snoop on how an object is being used.

    Suppose you pass an object into some function and want to know
    what properties of your object the function is using/depending on.
    Normally you do this:

    >>> obj = SomeObject() 
    >>> opaque_function(obj)
    
    Instead you do the following.  Note that there's no body to the
    definition of SnoopedObject.

    >>> class SnoopedObject(SnooperMixin, SomeObject): pass
    >>> obj = SnoopedObject()
    >>> opaque_function(obj)
    >>> obj.snoop
    set(['readlines', 'next'])

    So you know that opaque_function accessed/used the methods/data
    called readlines and next.

    This knowledge, of course, exposes the implementation details of
    opaque_function() and you probably shouldn't write code that
    depends on those details...  On the other hand, such knowledge can
    be very illuminating.

    The name Mixin comes from the old CLOS (Common Lisp Object System)
    notion of an object that's not itself a fully specified, useful
    object, but is something that's added to other objects to given
    them specific functionality.

    """
    # I think this __init__would work fine, but I don't want to mess
    # up initialization if the class you're snooping on is making
    # clever use of super()
    # 
    # def __init__(self, *a, **kw):
    #     self.snoop = set()
    #     super(SnooperMixin, self).__init__(*a, **kw)

    def __getattribute__(self, name):
        def safe_getattr(the_name):
            return super(SnooperMixin, self).__getattribute__(the_name)
        # Create an place to store results if necessary.  Could do
        # this with the modified __init__ commented above, but want to
        # isolate my changes to a single function.
        try:
            snoop = safe_getattr('snoop')
        except AttributeError:
            snoop = set()
            self.snoop = snoop
        # Do whatever you want here, making sure not to do anything
        # that explicitly or implicitly calls self.__getattribute__().
        # In this case just build up a list of accessed attributes.
        if name is not 'snoop': 
            snoop.add(name)
        # Return the actual requested attribute here.
        return safe_getattr(name)

class Container (object):
    """Simple object that has a nice syntax for filling in a few
    attributes:
    >>> c = Container(a=1, b=2)"""
    def __init__(self, **kw):
        for k in kw: self.__setattr__(k, kw[k])

class DotDict(dict):
    """Behaves like a dictionary, but allows dot access to read
    attributes.
    
    I use this to hold simulation data.  If my simulation has a field
    called "density", I'm sure not going to type sim['density'] every
    time I want to do anything.  This object allows me to refer to it
    as sim.density.

    >>> foo = DotDict()
    >>> foo.density = read_from_file()
    >>> plot(foo.density)

    >>> for kk in foo.keys(): ensure_no_nans(foo[kk])
    
    "But that's not very object oriented, you should define a
    SimulationData object that has density as an attribute," you may
    say.  Well.... that's what I've done.  I want the SimulationData
    object to have the same things that dict objects have, the keys()
    function, for example.  As long as you don't have a simulation
    data field that conflicts with the name of one of the dict
    methods, this causes no problem.

    """
    def __getattribute__(self, name):
        # If there's an attribute of this name, return it
        try: return dict.__getattribute__(self, name)
        except AttributeError:
            pass
        
        # If not, check if there's a dict entry with this name
        try: return self[name]
        except KeyError:
            pass
        
        # Finally, signal an error
        raise AttributeError
                    
    def __setattr__(self, name, val):
        # Assume that you aren't going to "stuff" attributes into this object
        # Therefore attribute assignments should be put into the dict
        self[name] = val
        
    def __delattr__(self, name):
        # Assume that you aren't going to delete attributes.
        # Therefore attribute deletions should be pulled out of the dict
        del self[name]

class LogDict(dict):
    """Write-only dictionary for logging.  

    Raises exceptions if you try to modify or delete a key

    """
    def __setitem__(self, k, v):
        if k in self: raise ValueError
        dict.__setitem__(self, k, v)

    def update(self, d):
        for k in d.keys():
            if k in self: raise ValueError
        dict.update(self, d)
    
    def __delitem__(self, k): raise ValueError
    def clear(self): raise ValueError
    def pop(self, k): raise ValueError
    def popitem(self): raise ValueError
        
class sstr(object):
    """Simple String.  Used for pretty output in IPython (no quotes)."""
    def __init__(self, name): self._name = name        
    def __repr__(self): return str(self._name)
    def __str__(self): return str(self._name)

##################################################
## Functions that enhance functions
def string_key(*a, **kw):
    """Turn function arguments into a unique key using repr() (for memoize
    function)"""
    return repr(a) + repr(kw)

def pickle_key(*a, **kw):
    """Turn function arguments into a unique key by pickling them (for
    memoize function)"""
    return cPickle.dumps((a, kw), protocol=-1)

def hash_key(*a, **kw):
    """Turn function arguments into a unique key by hashing them (for
    memoize function)"""
    return hashlib.sha256(cPickle.dumps((a, kw), protocol=-1)).digest()
        
def memoize(f, with_file=True, keyf=hash_key):
    """Return a caching version of long-running function f.

    >>> result = long_running_function(1.1) # takes a long time
    >>> f = memoize(log_running_function)
    >>> f(2.2)  # takes a long time, too
    >>> f(3.3)  # Also takes a long time
    >>> f(2.2)  # Instantaneous (using the previously cached result)

    If called with the same arguments, it just returns the previous
    return-value instead of recomputing.  It does this by converting
    all positional and keyword arguments to strings and indexing into
    a dictionary.  A different method of generating keys can be used
    if you specify the keyf funciton.  If with_file is true, pickle
    the resulting dictionary to a file with name 
    f.func_name + '.memo'.  Be careful of using this feature with
    several instances of Python running... they will each overwrite
    the file.  It should not lead to corruption, though since the dict
    is only loaded from the file when memoize itself is called.

    """
    def g(*args, **kw):
        key = keyf(*args, **kw)
        if not key in results:
            results[key] = f(*args, **kw)            
            if with_file: can(results, fname)
        return results[key]
    
    fname = f.func_name + '.dat'
    if with_file and os.path.isfile(fname): results = uncan(fname)
    else: results = {}
    
    g.func_doc, g.func_name = f.func_doc, f.func_name
    return g

def logize(f,with_file=True, with_args=False):
    """Capture log of return values of a function.

    Sometimes I want to build up statistics of calls to a long-running
    function.  I don't want to try to substitute previously computed
    values (ie, not memoization), and accordingly I'm not necssarily
    as worried about making sure that every possible set of arguments
    generates a unique key.  Therefore I return a new function that
    captures calls to the original function and logs them.  A second
    function is necessary to get a hold of the resulting dict.  The
    function keyf generates keys from the arguments of the call.

    A more conventional object-based implementation of the same thing
    is below, but frankly that doesn't read any better than this to me.

    def square(xx): 
        return x**2        
    >>> fn, fn_results = logize(square)
    >>> fn(2); fn(3); fn(2);
    >>> fn_results() 
    [4, 9, 4]
    """
    
    def g(*ar, **kw):
        value = f(*ar, **kw)        
        if with_args: results.append((ar, kw, value))
        else: results.append(value)
        
        if with_file: can(results, fname)
        return value

    def getResults():        
        return results

    fname = f.func_name + '.dat'    
    if with_file and os.path.isfile(fname): results = uncan(fname)
    else: results = []
    
    g.func_doc, g.func_name = f.func_doc, f.func_name
    return g, getResults

class FunctionLogger:
    """Capture log of return values of a function.
    
    'Conventional' implementation of logize() using objects.

    def square(xx): 
        return x**2        
    >>> flogger = FunctionLogger(square)
    >>> flogger.run(2); flogger.run(3); flogger.run(2); 
    >>> flogger.results
    [4, 9, 4]
    """
    def __init__(self, f, with_file=True, with_args=False):
        fname = f.func_name + '.dat'

        if with_file and os.path.isfile(fname): self.results = uncan(fname)
        else: self.results = []

        self.f = f
        self.with_args = with_args
        
    def run(self, *a, **kw):
        value = self.f(*a, **kw)
        if self.with_args: self.results.append((a, kw, value))
        else: self.results.append(value)
        return value
    
def forking_call(f, *args, **kwds):
    """Fork a separate process in which to run f.  

    Exceptions raised in the child process are caught and re-raised in
    the parent process.
    
    >>> result = func(arg, kwarg=value)
    becomes:
    >>> result = forking_call(func, arg, kwarg=value)

    Source:
    http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/511474

    """
    SUCCESS, EXCEPTION, UNPICKLABLE = (0,1,2)

    pread, pwrite = os.pipe()
    pid = os.fork()
    if pid > 0:
        os.close(pwrite)
        # GSN -- moved this up from below the with statement
        os.waitpid(pid, 0)
        with os.fdopen(pread, 'rb') as f: status, result = cPickle.load(f)
        if status == SUCCESS: return result
        else: raise result
    else: 
        try: 
            try:
                result = f(*args, **kwds)
                status = SUCCESS
            except Exception, exc:
                result = exc
                status = EXCEPTION
            try:
                os.close(pread)
                with os.fdopen(pwrite, 'wb') as f:            
                    cPickle.dump((status,result), f, protocol=-1)
            except Exception, exc:
                cPickle.dump((UNPICKLABLE,exc), f, protocol=-1)
        # Make sure that this thread exits to avoid the parent waiting
        # indefinitely or getting unexpectedly popped into the child
        # process.  On the other hand, maybe that'd be nice for
        # exception handling...
        finally: os._exit(0)

def forkify(f):
    """Return a function that forks and calls f in separate process.

    I found this useful for long-running Python processes that handle
    a lot of data and eventually run out of memory.  In spite of my
    best efforts at making sure no dangling references were hanging
    around, the most robust solution was to just fork and let the
    operating system handle de-allocation.

    So if memory_intensive_function() uses a lot of memory but
    produces small results, then this will prevent out-of-memory
    problems:
    >>> f = forkify(memory_intensive_function)
    >>> [f(ii) for ii in huge_list]

    Exceptions raised in the child process are caught and re-raised in
    the parent process.

    """
    def g(*a, **kw): return forking_call(f, *a, **kw)    
    g.func_doc, g.func_name = f.func_doc, f.func_name    
    return g

##################################################
## Generic convenient Functions
##################################################
    
def wrap(x, min, max):
    """Wrap x periodically into the range [min, max)"""
    return ((x - min) % (max - min)) + min
    range = float(max-min)
    return x - range*floor(x/range) 

def primep(n):
    """Test if a number if prime, using a simple-minded algorithm."""
    # Given any two factors a,b such that a*b = n, take a > b, then it
    # must be the case that a >= sqrt(n) and b <= sqrt(n).  Therefore
    # we only need to test factors from 2 to sqrt(n)
    # 
    # Should only need +1 in the limits, but use +2 since we're
    # dealing with floating point numbers, in case, 
    # e.g. sqrt(100) = 9.99998
    if n<=1: return False
    the_max = min(n-1, int(math.sqrt(n))+2)
    for div in range(2,the_max):
        if n % div == 0:
            return False
    return True

def primes(n):
    """Return all primes less than or equal to n"""
    return [i for i in range(2,n+1) if primep(i)]

def prime_factors(n):
    """Return all prime factors of n"""
    ps = primes(n)
    return [p for p in ps if n % p == 0]

def prime_factorize(n):
    """Return prime factorization of n"""
    pfs = prime_factors(n)
    if pfs == []:         
        # happens when n <= 1
        return pfs
    elif pfs[0] == n:
        return pfs
    else:
        return [pfs[0]] + prime_factorize(n/pfs[0])

##################################################
## Functions for manipulating lists
##################################################

def flatten(L):
    """Return a flat list with the same elements as arbitrarily nested
    list L"""
    if type(L) is not list: return [L]
    if L == []: return L
    return flatten(L[0]) + flatten(L[1:])

# Less concise version of flatten should recursion become a problem.
# def flatten(L):
#    """Return a flat list with the same elements as arbitrarily nested
#    list L"""
#     result = []
#     stack = [L]
#     while stack:
#         print stack
#         current = stack.pop()
#         if type(current) is list:
#             if current[1:]:
#                 stack.append(current[1:])
#             stack.append(current[0])
#         else:
#             result.append(current)
#     return result

def group(L, n):
    """Split L into groups of n elements, where the last group has
    possibly less than n if len(L) is not divisible by n"""
    idx = range(0, len(L)+n, n)
    return [L[l:h] for l, h in zip(idx[:-1], idx[1:])]

def ggroup(it, n):
    """group() implemented using generators"""
    result = []
    ii = 1
    for el in it:
        result.append(el)
        if ii % n == 0:
            yield tuple(result)
            result = []
        ii += 1

    # return the dregs if necessary
    if len(result) > 0:
        yield tuple(result)

def iterable(obj):
    """Test if you can iterate over an object"""
    try: len(obj)
    except TypeError: return False
    return True

def cross_set(*sets):
    """Given lists, generate all possibilities with the first element
    chosen from the first list, the second element chosen from the
    second, etc.  Note that this handles an arbitrary number of sets
    from which to draw.
    
    >>> cross_set([1], [2,3]) 
    [[1,2], [1,3]]

    """
    if len(sets) == 1:
        return [ [el] for el in sets[0] ]
    result = []
    for el in sets[0]:
        result += [ [el] + sub_prod for sub_prod in cross_set(*sets[1:])]
    return result

def combinations(lst, n):
    """Generate all combinations of n items of lst
    
    >>> combinations([1,2,3], 2)
    [[1,2], [1,3], [2,3]]
    """
    # First two are degenerate base cases
    # Second two are non-degenerate base cases
    # else clause is recursive case
    if n <= 0: 
        return []
    elif len(lst)==0: 
        return []
    elif len(lst) == n: 
        return [list(lst)]
    elif n == 1: 
        return [[el] for el in lst]
    else:
        c_without = combinations(lst[1:], n)
        c_small = combinations(lst[1:], n-1)
        c_with = [[lst[0]] + el for el in c_small]
        return c_with + c_without

def zip_list(*lst):
    """Same as zip, but returns a list of lists instead of a list of tuples"""
    return [list(el) for el in zip(*lst)]

def same(x,y):
    """Determine if two objects are the same, recursing over their tree structure.

    >>> same([1, [2, 3]], [1, [2, 3]])
    True
    >>> same([1, [2, 3]], [1, 4])
    False

    This is the same as if you just test with the equality operator,
    except that same() treats lists and tuples as the same

    >>> [1, [2, 3]] == [1, (2, 3)]]
    False
    >>> same([1, [2, 3]] == [1, (2, 3)]])
    True
    """
    if iterable(x):
        if len(x) != len(y): return False
        return every([same(xx,yy) for xx, yy in zip(x,y)])
    return x==y

def merge_comp(l1, l2):
    """Make a comparison function for merge_sorted"""
    def comp(x,y):
        if   x in l1 and y in l1:
            return cmp(l1.index(x), l1.index(y))
        elif x in l2 and y in l2:
            return cmp(l2.index(x), l2.index(y))
        elif x not in l1 and x not in l2 or \
             y not in l1 and y not in l2:
            # This should never happen
            raise RuntimeError, "This should never happen"
        else:
            # Find a third element with the same relation to x and y,
            # meaning it's between the two
            for pivot in common:
                if comp(x, pivot) == comp(pivot, y) and comp(x, pivot) != 0:
                    return comp(x, pivot)
            # This may happen
            raise RuntimeError, "Cannot find relation for %s and %s" % (x, y)
                    
    common = [el for el in l1 if el in l2]
    return comp

def merge_sorted(l1, l2, check=True):
    """Merge two sorted lists that contain some, but not all, of the
    same elements.  

    Do not assume the existence of any particular comparison function
    that can be applied to any two elements in either list.  Assume
    only that l1 and l2 are each sorted, and try to use the implied
    ordering and common elements between the two lists to create a
    merged list that is also sorted and contains only unique elements.

    This works:
    >>> merge_sorted(['!','#','@'], ['!','@','%'])
    ['!', '#', '@', '%']

    But this fails because neither list defines the relation between '#' and '$'
    >>> merge_sorted(['!','#','@'], ['!','$','@'])
    RuntimeError: Cannot find relation for # and $

    check=True means checks that the lists define a self-consistent
    ordering (which makes the sorting N^2 instead of N log N.
    
    """
    all = list(set(l1).union(l2))
    if check:
        cmp1 = merge_comp(l1, l2)
        cmp2 = merge_comp(l2, l1)
        for e1 in all:
            for e2 in all:
                assert cmp1(e1, e2) ==  cmp2(e1, e2)
                assert cmp1(e1, e2) == -cmp1(e2, e1)
                assert cmp2(e1, e2) == -cmp2(e2, e1)
    return sorted(all, cmp=merge_comp(l1, l2))

def grab_list(lst, pred):
    """Return a list of elements of lst that satisfy predicate.  The
    elements are removed from lst.
    >>> ll = [1,2,3,4]
    >>> even = grab_list(ll, lambda x: x % 2 == 0)
    >>> ll
    [1,3]
    >>> even
    [2,4]
    """
    result = [el for el in lst if pred(el)]
    for el in result:
        lst.remove(el)
    return result

def list_printer(lst, fmt='%.3f', sep=',  '):
    """Print elements of a list with given formatting"""
    def add(x,y): return x + sep + y
    return '[  ' + reduce(add, [fmt % el for el in lst]) + ']'

##################################################
## Functions for manipulating dicts
##################################################

def map_dict(f, d):
    """Like map(f, lst), but iterates over the values of a dict and
    returns a dict 
    >>> map_dict(lambda x: 2*x, dict(a=1, b=2))
    {'a': 2, 'b': 4}
    """
    return dict([(k, f(v)) for k,v in d.items()])

def double_map_dict(f, d1):
    """Like map_dict, but iterates over a dict of dicts.  Not very
    general purpose but this handles a common case for me."""
    return map_dict(lambda d2: map_dict(f, d2), d1)

def map_dict_tree(f, d):
    """Map an arbitrarily nested dict of dicts of dicts...  The
    recursion stops when a non-dict value is encountered."""
    return dict([ (k, map_dict_tree(f, v) if type(v) is types.DictType else f(v))
                  for k,v in d.items()])

def dict_transpose(d):
    """Make a dict of tuples into a tuple of dicts
    >>> dict_transpose(dict(a=(1,2), b=(3,4)))
    ({'a': 1, 'b': 3}, {'a': 2, 'b': 4})
    """
    N = len( d.values()[0] )
    return tuple([dict( [ (k, d[k][i]) for k in d.keys()] ) 
                  for i in range(N)])

def dict_keys(d):
    """Given a dict, return a list of keys that are also dicts"""
    return [k for k,v in d.iteritems() if type(v) is dict]

###################################################
## Functions to conveniently manipulate function keyword argument
## dicts.
###################################################
def dict_union(*ds, **kw):
    """Combine several dicts and keywords into one dict.  I use this
    for argument processing where I want to set defaults in several
    places, sometimes overriding values.  The common case is something
    like:
    
    values = dictUntion(global_defaults, local_defaults, key1=val1,
    key2=val2)

    where global_defaults and local_defaults are dicts where
    local_defaults overrides global_defaults, and key1 and key2
    override anything in either of the values."""
    # Last one wins.  For sense is something like:    
    # dictUntion(system_defaults, user_defaults, override1=blah, ...)
    iters = [d.iteritems() for d in ds] + [dict(**kw).iteritems()]
    return dict(itertools.chain(*iters))

def pop_keys(d, *names):
    """Pull some keywords from dict d if they exist.
    
    I use this to help with argument processing when I have lots of
    keyword arguments floating around.  The typical use is something like:

    def foo(**kw):
        kw1 = pop_keys('args', 'for', 'bar')
        bar(**kw1)
        other_function(**kw)  # kw doens't contain the popped keywords anymore
        
    Thus neither bar() nor other_function() get keyword arguments that
    they don't expect.  In addition, if the caller _doesn't_ specify
    an argument, it doesn't show up in the arg list for the calls to
    bar or other_function, so that the default values are used.

    """
    return dict([(k, d.pop(k)) for k in names if k in d])

def given(*args):
    """Return True if all of the arguments are not None.  

    Intended for use in argument lists where you can reasonably
    specify different combinations of parameters.  Then you can write

    def foo(a=None, b=None, c=None):
        if given(a,b): 
            do something
        elif given(a,c): 
            do something else
    """

    return all( [arg is not None for arg in args] )

###################################################
## Functions for composing predicates
###################################################
#
# The idea is to compose functions using logical operators to make
# compound predicates.  Ie, you have functions blue(obj) and
# green(obj) that return True or False depening on whether the object
# is blue or green.  You should be able to write:
# 
# blue_or_green = f_or(blue, green)
# if blue_or_green(obj): 
#     do something
#
# Think for a moment about the nicest way to define the argument list:
#
# This definition allows these uses
# def every(*args): return reduce(and2, args)
# every(True, True, False) => False
# every(*[True, True, False]) => False
# every([True, True, False]) => [True, True, False]
#
# The last is very bad and an easy mistake.

# This definition allows these:
# def every(args): return reduce(and2, args)
# every([True, True, False]) => False
# every(*[True, True, False]) => Error
# every(True, True, False) => Error
#
# This is mostly for programmatic use anyway, so the first use case is
# the most common one.  It's not a lot of skin off of your nose to put
# in the brackets when you have a few values and are writing them
# explicitly in the source code.  Finally, you'd be using explicit
# ands in that case anyway.

def all_same(args): return every([arg is args[0] for arg in args])
def every(args): return reduce(lambda x,y: x and y, args, True)
def some(args): return reduce(lambda x,y: x or y, args, False)
def none(args): return not some(args)

# def f_and(*fs) allows:
# g = f_and(f1, f2)   and  g = f_and(*foo(bar))
# g = f_and( f_or(f1, f2), f_or(f3, f4))
#
# def f_and(fs), allows:
# g = f_and((f1, f2))  and  g = f_and(f_or(bar))
# g = f_and( (f_or((f1, f2)), f_or((f3, f4))) )

# Since the intent is to make composable function predicates, I think
# that the third use case is the decisive one.
# Could make it handle either case by looking for callable objects

def f_and(*fs):
    """Return a function that ands together the result of every
    function given as an argument"""
    if len(fs) == 1 and not callable(fs): return f_and(*fs[0])
    return lambda *a, **kw: every([f(*a, **kw) for f in fs])

def f_or(*fs):
    """Return a function that ors together the result of every
    function given as an argument"""
    if len(fs) == 1 and not callable(fs): return f_or(*fs[0])
    return lambda *a, **kw: some([f(*a, **kw) for f in fs])

def f_not(f):
    """Return a function that's the logical not of the argument."""
    return lambda *a, **kw: not f(*a, **kw)

def if_exp(cond, true, false):
    """An if statment expression.  Doens't conditionally execute code,
    but does conditionally return a value"""
    if cond: return true
    return false

def constantly(val):
    """Return a function that returns val regardless of its arguments"""
    def constant(*a, **kw):
        return val
    return constant

##################################################
## Functions having to do with the filesystem
##################################################
def to_filename(str):
    """Ensures that a candidate filename has only one dot, to avoid
    confusing certain filesystems/tools.  Extra dots are changed to
    'p'

    >>> to_filename('foo')
    'foo'
    >>> to_filename('foo.bar')
    'foo.bar'
    >>> to_filename('foo.bar.baz')
    'foopbar.baz'
    """
    parts = str.split('.')
    if len(parts) <= 2: return str
    return 'p'.join(parts[:-1]) + '.' + parts[-1]

def can(obj, file, protocol=2):
    """More convenient syntax for pickle, intended for interactive use

    Most likely:
    >>> can([1,2,3], 'file.dat')
    But can also do:
    >>> with open('file.dat', 'w') as f: can([1,2,3], f); can((3,4,5), f)

    """
    if type(file) is str: f=open(file,'wb')
    else: f=file

    cPickle.dump(obj, f, protocol=protocol)

    if type(file) is str: f.close()

def uncan(file):
    """More convenient syntax for pickle, intended for interactive use

    Most likely:
    >>> obj = uncan('file.dat')
    But can also do:
    >>> with open('file.dat') as f: foo = uncan(f); bar = uncan(f)

    """
    # If filename, should this read until all exhausted?
    if type(file) is str: f=open(file, 'rb')
    else: f=file    

    obj = cPickle.load(f)

    if type(file) is str: f.close()

    return obj

def file_size(path, human=False):
    """Return the size of a file in bytes"""
    bytes = os.lstat(path)[stat.ST_SIZE] 
    if not human:
        return bytes    
    if bytes < 1024: result = int(bytes), 'B'
    elif bytes < 1024**2: result = int(bytes/1024), 'K'
    elif bytes < 1024**3: result = int(bytes/1024**2), 'M'
    elif bytes < 1024**4: result = int(bytes/1024**3), 'G'
    else: result = int(bytes/1024**4), 'T'
    return sstr('%d %c' % result)

def find(pred, dir='.', with_directories=True, with_files=True):
    """Similar to the shell command find"""
    result = []
    for root, dirs, files in os.walk(dir):
        if with_directories:
            for d in dirs:
                if pred(root, d): result.append(os.path.join(root, d))
        if with_files:
            for f in files:
                if pred(root, f): result.append(os.path.join(root, f))
    return result

##################################################
## Functions having to do with the operating system
##################################################
def memory_usage(pid=None, unit='MB'):
    """On linux systems, get info about memory use from the /proc filesystem"""
    if pid is None: pid = os.getpid()    
    result = {}
    #with open('/proc/%d/status' % pid) as f:
    f = open('/proc/%d/status' % pid)
    for line in f:
        for name, regexp in (("size", "VmData:\s*([0-9]+)\s([A-z]B)"),
                             ("resident", "VmRSS:\s*([0-9]+)\s([A-z]B)")):
            match = re.match(regexp, line)
            if match:
                num, givenUnit = match.groups()
                if   givenUnit == 'kB': num = 1000*int(num)
                else: raise RuntimeError, "Unknown Unit!"
                result[name] = num
    f.close()
    
    for k,v in result.iteritems():
        if unit == 'B': pass
        elif unit == 'kB': result[k] = result[k] / 10**3
        elif unit == 'MB': result[k] = result[k] / 10**6
        elif unit == 'GB': result[k] = result[k] / 10**9
        elif unit == 'kiB': result[k] = result[k] / 2**10
        elif unit == 'MiB': result[k] = result[k] / 2**20
        elif unit == 'GiB': result[k] = result[k] / 2**30
        # These are for completeness so I can remind myself of this one day...
        elif unit == 'b': result[k] = 8*result[k]
        elif unit == 'kb': result[k] = 8*result[k] / 10**3
        elif unit == 'Mb': result[k] = 8*result[k] / 10**6
        elif unit == 'Gb': result[k] = 8*result[k] / 10**9
        elif unit == 'kib': result[k] = 8*result[k] / 2**10
        elif unit == 'Mib': result[k] = 8*result[k] / 2**20
        elif unit == 'Gib': result[k] = 8*result[k] / 2**30        
        else: raise RuntimeError, "Unknown Unit!"
    return result
    
def timer(f, *a, **kw):
    """Provide reasonably reliable time estimates for a function.

    Runs the function once.  If the run time is less than timer_tmin,
    run the function timer_factor more times.  Repeat until timer_tmin
    is surpassed.  If timer_verbose, print what's going on to stdout.

    >>> square = lambda x: x**2
    >>> timer(f, 5, timer_tmin=2.0, timer_factor=3, timer_verbose=True)

    """
    tmin = kw.pop('timer_tmin', 1.0)
    factor = kw.pop('timer_factor', 2)
    verbose = kw.pop('timer_verbose', False)

    reps, dt = 1, 0
    while dt < tmin:
        if verbose: print "Trying", reps, 
        t = time.time()
        for i in xrange(reps):
            f(*a, **kw)
        dt = time.time() - t
        if verbose: print "ran in", dt
        reps *= factor

    # reps was multipled one too many times
    reps /= factor
    return dt / reps, reps

##################################################
## Functions having to do with Python
##################################################

def import_graph(with_system=True, out_file=sys.stdout,
                excludes=None, exclude_regexps=None):
    """Construct a graph of which python modules import which others,
    suitable for consumption by graphviz (http://www.graphviz.org).  

    This just works on python files in the current directory.  It's
    intended to be helpful if you want to reduce dependencies among
    python files in the current directory.

    >>> import_graph(out_file='imports.dot')
    # At the Unix shell prompt: 
    [novak@thalia ~]$ dot -Tpng imports.dot > imports.png

    """
    def include(module):
        return not module in excludes \
               and none([re.match(regexp, module) for regexp in exclude_regexps])
        
    excludes = excludes or []
    exclude_regexps = exclude_regexps or []    
    
    pyfiles = [fn for fn in os.listdir('.') if fn.endswith('.py')]
    localSources = [fn.replace('.py', '') for fn in pyfiles]
    localSources = [mod for mod in localSources if include(mod)]
    output = []
    output.append('digraph gr {\n')
    if with_system:
        for node in localSources:
            output.append('%s color=red;' % node)
            
    for fn, src in zip(pyfiles, localSources):
        #with open(fn) as f:
        f = open(fn)
        for line in f:
            fromMatch = re.match(r"from ([A-z]+) import", line)
            importMatch = re.match(r"import " + 10*"(?:([A-z]+),? *)?", line)

            if fromMatch: dests = fromMatch.groups()
            elif importMatch:
                dests = [gp for gp in importMatch.groups() if gp]
                if len(dests) >= 3 and dests[-2] == 'as':
                    dests = dests[:-2]
            else: dests = []

            for dest in dests:
                if include(dest) and (dest in localSources or with_system):
                    output.append("%s -> %s;\n" % (src, dest))
        f.close()
        
    output.append('}\n')
    if type(out_file) is str:
        #with open(out_file, "w") as outf:
        outf = open(out_file, "w")
        outf.writelines(output)
        outf.close()
    else:
        out_file.writelines(output)
