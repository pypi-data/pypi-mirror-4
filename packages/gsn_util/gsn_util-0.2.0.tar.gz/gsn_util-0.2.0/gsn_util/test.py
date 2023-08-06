import unittest, tempfile

try: import numpy
except ImportError: numpy = False

from gsn_util import *

class DotDictTest(unittest.TestCase):
    # This object is in every respect a dict, it just allows you to
    # type foo.a = 5 instead of foo['a'] = 5.  This means it can be
    # compared like dicts, so take advantage of that.

    def test_DotDict(self):
        zz = DotDict(a=1)
        zz['b']=2
        zz.c=3
        self.assertEqual(zz, dict(a=1,b=2,c=3))
        del zz['c']
        self.assertEqual(zz, dict(a=1,b=2))
        del zz['b']
        self.assertEqual(zz, dict(a=1))

class SnooperMixinTest(unittest.TestCase):
    def test_SnooperMixin(self):
        class SnoopedDict(SnooperMixin, dict): pass
        dd = SnoopedDict(a=1, b=2)
        dd.keys()
        self.assertEqual(dd.snoop, set(['keys']))

class DictTest(unittest.TestCase):
    def testLogDict(self):
        def add_a(d):
            d['a'] = 3
        def del_a(d):
            del d['a']
            
        # These constructors are legal
        LogDict(dict(a=1,b=2))
        LogDict((('a', 1), ('b',2)))
        LogDict.fromkeys(('a', 'b'), 1)

        # these constructors are illegal        
        # This doesn't raise the error, but it's a pathological case...
        #self.assertRaises(ValueError, LogDict, (('a', 1), ('b',2), ('a', 3)))

        # These operations are legal
        d = LogDict()        
        d['a'] = 1
        d['b'] = 2
        d.update(dict(c=3))

        # These operations should generate exceptions
        self.assertRaises(ValueError, del_a, d)
        self.assertRaises(ValueError, add_a, d)
        self.assertRaises(ValueError, d.__delitem__, 'b')
        self.assertRaises(ValueError, d.__setitem__, 'a', 3)
        self.assertRaises(ValueError, d.clear)
        self.assertRaises(ValueError, d.pop, 'a')
        self.assertRaises(ValueError, d.popitem)        
        self.assertRaises(ValueError, d.update, dict(a=3))
    
class SyntaxTest(unittest.TestCase):
    def bracketAccessTest(self, obj):
        obj.a = 1
        obj['b'] = 2
        self.assertEqual(obj['a'], 1)
        self.assertEqual(obj.b, 2)
                    
    def test_BracketAccess(self):
        class testNewObj (object, BracketAccessMixin): pass
        class testOldObj (BracketAccessMixin): pass
        self.bracketAccessTest(testNewObj())
        self.bracketAccessTest(testOldObj())

    def test_Container(self):
        c = Container(a=1,b=2)
        self.assertEqual(c.a, 1)
        self.assertEqual(c.b, 2)

    def test_sstr(self):
        s = sstr("one")
        self.assertEqual(s.__str__(), "one")
        self.assertEqual(s.__repr__(), "one")

class FunctionTest(unittest.TestCase):    
    def test_wrap(self):
        self.assertEqual(wrap(0.25, 1.0, 2.0), 1.25)
        self.assertEqual(wrap(1.25, 1.0, 2.0), 1.25)
        self.assertEqual(wrap(3.25, 1.0, 2.0), 1.25)
        self.assertEqual(wrap(0.0, 1.0, 2.0), 1.0) 
        self.assertEqual(wrap(1.0, 1.0, 2.0), 1.0)
        self.assertEqual(wrap(2.0, 1.0, 2.0), 1.0)
        self.assertEqual(wrap(3.0, 1.0, 2.0), 1.0)

    def test_primep(self):
        # Postiive ints
        self.assertEqual(primep(2), True)
        self.assertEqual(primep(3), True)
        self.assertEqual(primep(4), False)
        self.assertEqual(primep(5), True)
        self.assertEqual(primep(6), False)
        
        # sort of edge case
        self.assertEqual(primep(1), False)
        
        # Make sure the code doesn't barf
        self.assertEqual(primep(0), False)
        self.assertEqual(primep(-1), False)
        self.assertEqual(primep(-2), False)
        self.assertEqual(primep(-3), False)
        self.assertEqual(primep(-4), False)
        self.assertEqual(primep(-5), False)
        self.assertEqual(primep(-6), False)

    def test_primes(self):
        self.assertEqual(primes(11), [2, 3, 5, 7, 11])
        self.assertEqual(primes(0), [])
        self.assertEqual(primes(-11), [])

    def test_prime_factors(self):
        self.assertEqual(prime_factors(11), [11])
        self.assertEqual(prime_factors(60), [2,3,5])
        self.assertEqual(prime_factors(1), [])
        self.assertEqual(prime_factors(0), [])
        # Not sure, maybe I should include these as [-1, 11], e.g.
        self.assertEqual(prime_factors(-1), [])
        self.assertEqual(prime_factors(-60), [])

    def test_prime_factorize(self):
        self.assertEqual(prime_factorize(11), [11])
        self.assertEqual(prime_factorize(60), [2,2,3,5])
        self.assertEqual(prime_factorize(1), [])
        self.assertEqual(prime_factorize(0), [])
        # Not sure, maybe I should include these as [-1, 11], e.g.
        self.assertEqual(prime_factorize(-1), [])
        self.assertEqual(prime_factorize(-60), [])

    def test_zip_list(self):
        result = zip_list((1,2,3), (4,5,6))
        self.assertTrue(type(result) is types.ListType)
        self.assertEqual(result, [[1,4], [2,5], [3,6]])

    def test_same(self):
        # scalar args
        self.assertTrue(same(1,1))
        self.assertFalse(same(1,0))

        # list args
        self.assertTrue(same([1,2,3], [1,2,3]))
        self.assertFalse(same([1,2,3], [1,4,3]))
        self.assertFalse(same([1,2], [1,2,3]))
        self.assertFalse(same([1,2,3], [1,2]))

        # tree args
        self.assertTrue(same([[[1,2],3],4], [[[1,2],3],4]))
        # leaf different
        self.assertFalse(same([[[1,2],3],4], [[[1,2],5],4]))
        # extra leaf
        self.assertFalse(same([[[1,2],3],4], [[[1,2],3, 5],4]))
        # extra tree
        self.assertFalse(same([[[1,2],3],4], [[[1,2],[3,5]],4]))
        # missing tree
        self.assertFalse(same([[[1,2],3],4], [[[1,2]],4]))

    def test_list_printer(self):
        self.assertEqual(list_printer([1.0,2.0,3.0], '%d'), 
                         '[  1,  2,  3]')
        self.assertEqual(list_printer([1.0,2.0,3.0], '%d', sep='; '), 
                         '[  1; 2; 3]')

    def test_flatten(self):
        self.assertEqual(flatten([[[(1,2)],3],4]), [(1,2), 3, 4])

    def test_group(self): 
        self.assertEqual(group([1,2,3,4], 2), [[1,2], [3,4]])
        self.assertEqual(group([1,2,3,4,5], 2), [[1,2], [3,4], [5]])

    def test_ggroup(self): 
        # with lists
        self.assertEqual([el for el in ggroup([1,2,3,4], 2)], 
                         [(1,2), (3,4)])
        self.assertEqual([el for el in ggroup([1,2,3,4,5], 2)], 
                         [(1,2), (3,4),(5,)])

        # with iterators
        def f(n): 
            for i in range(n): 
                yield i

        self.assertEqual([el for el in ggroup(f(4), 2)], 
                         [(0,1), (2,3)])
        self.assertEqual([el for el in ggroup(f(5), 2)], 
                          [(0,1), (2,3),(4,)])
                
    def test_combinations(self): 
        self.assertEqual(combinations([1,2,3], 0), [])
        self.assertEqual(combinations([1,2,3], 1), [[1],[2],[3]])
        self.assertEqual(combinations([1,2,3], 2), [[1,2],[1,3],[2,3]])
        self.assertEqual(combinations([1,2,3], 3), [[1,2,3]])
        self.assertEqual(combinations([1,2,3], 4), [])

        self.assertEqual(combinations([], 0), [])
        self.assertEqual(combinations([], 1), [])
        self.assertEqual(combinations([], 2), [])

    def test_iterable(self):
        self.assertTrue(iterable([1,2]))
        self.assertTrue(iterable((1,2)))
        self.assertFalse(iterable(1))

    def test_dict_keys(self):
        self.assertEqual(dict_keys(dict(a=1, b=[1,2], c=dict(d=1,e=2))), ['c'])

    def test_sorted(self):
        l = [3,1,2]
        self.assertEqual(sorted(l), [1,2,3])
        self.assertEqual(sorted(l, reverse=True), [3,2,1])
        self.assertEqual(l, [3,1,2])

    def test_all_same(self):
        l1 = [1,2]
        l2 = [1,2]
        self.assertTrue(all_same([l1, l1]))
        self.assertFalse(all_same([l1, l2]))
        
    def test_every(self):
        self.assertTrue(every([True, True]))
        self.assertFalse(every([True, False]))
        
    def test_some(self):
        self.assertTrue(some([True, False]))
        self.assertFalse(some([False, False]))

    def test_none(self):
        self.assertTrue(none([False, False]))
        self.assertFalse(none([True, False]))

    def test_if_exp(self):
        self.assertTrue( if_exp(True, True, False) )
        self.assertFalse( if_exp(False, True, False) )

    def test_f_and(self):        
        self.assertTrue (f_and(constantly(True ), constantly(True ))())
        self.assertFalse(f_and(constantly(False), constantly(True ))())
        self.assertFalse(f_and(constantly(False), constantly(False))())

    def test_f_or(self):
        self.assertTrue (f_or(constantly(True ), constantly(True ))())
        self.assertTrue (f_or(constantly(False), constantly(True ))())
        self.assertFalse(f_or(constantly(False), constantly(False))())

    def test_f_not(self):                
        self.assertTrue (f_not(constantly(False))())
        self.assertFalse(f_not(constantly(True))())

    def test_grab_list(self):
        l = [1,2,3,4]
        result = grab_list(l, lambda x: x % 2 == 0)
        self.assertEqual(l, [1,3])
        self.assertEqual(result, [2,4])

    def test_outer_product(self):
        # one arg
        self.assertEqual(cross_set([1]), [[1]])
        self.assertEqual(cross_set([1,2]), [[1], [2]])

        # two args
        self.assertEqual(cross_set([1,2], [3,4]),
                         [[1,3], [1,4], [2,3], [2,4]])
        self.assertEqual(cross_set([1,2], [3,4,5]), 
                         [[1,3], [1,4], [1,5],
                          [2,3], [2,4], [2,5]])
        # degenerate cases
        self.assertEqual(cross_set([]), [])
        self.assertEqual(cross_set([1,2], []), [])
        self.assertEqual(cross_set([], [3,4,5]), [])

    def test_merge_sorted(self):
        l1 = [ 1, 2, 3, 4,    6, 7]
        l2 = [    2,    4, 5, 6]
        self.assertEqual(merge_sorted(l1, l2),  [1, 2, 3, 4, 5, 6, 7])
        self.assertEqual(merge_sorted(l2, l1),  [1, 2, 3, 4, 5, 6, 7])

    def test_merge_sorted_cmp(self):
        l1 = [ 1, 2, 3, 4,    6, 7,    9, 10]
        l2 = [    2,    4, 5, 6,    8, 9]
        comp = merge_comp(l1, l2)

        self.assertEqual(comp(1, 5), -1)
        self.assertEqual(comp(5, 1),  1)
        self.assertEqual(comp(1, 8), -1)
        self.assertEqual(comp(8, 1),  1)

        self.assertEqual(comp(3, 5), -1)
        self.assertEqual(comp(5, 3),  1)
        self.assertEqual(comp(3, 8), -1)
        self.assertEqual(comp(8, 3),  1)

        self.assertEqual(comp(5, 7), -1)
        self.assertEqual(comp(7, 5),  1)
        self.assertEqual(comp(5, 10), -1)
        self.assertEqual(comp(10, 5),  1)

        self.assertEqual(comp(8, 10), -1)
        self.assertEqual(comp(10, 8),  1)

        self.assertRaises(RuntimeError, comp, 7, 8)
        self.assertRaises(RuntimeError, comp, 8, 7)

    def test_map_dict(self): 
        self.assertEqual(map_dict(lambda x: x+2, dict(a=1, b=2)),
                         dict(a=3,b=4))

    def test_double_map_dict(self):
        ff = lambda x: x+2
        input  = dict(a=dict(c=1,d=2), b=dict(e=3,f=4))
        output = dict(a=dict(c=3,d=4), b=dict(e=5,f=6))
        self.assertEqual(double_map_dict(ff, input), output)
        
    def test_map_dict_tree(self):
        ff = lambda x: x+2
        input  = dict(a=1, b=dict(c=2,d=dict(e=3,f=dict(g=4,h=5))))
        output = dict(a=3, b=dict(c=4,d=dict(e=5,f=dict(g=6,h=7))))
        self.assertEqual(map_dict_tree(ff, input), output)

    def test_dict_transpose(self):
        input = dict(a=(1,2), b=(3,4))
        output = dict(a=1, b=3), dict(a=2, b=4)
        self.assertEqual(dict_transpose(input), output)

    def test_dict_union(self):
        result = dict_union(dict(a=1, b=2, c=3, d=4),
                           dict(a=5, b=6, e=7, f=8),
                           a=9, c=10, e=11, g=12)
        desired = dict(a=9, c=10, e=11, g=12, b=6, f=8, d=4)

        self.assertEqual(result, desired)

    def test_timer(self):
        # Check that it runs, not correct behavior
        timer(prime_factorize, 400, timer_tmin=0.2)
        timer(prime_factorize, 400, timer_tmin=0.2, timer_factor=3)
        timer(prime_factorize, 400, timer_tmin=0.2, timer_verbose=False)

class FunctionArgTest(unittest.TestCase):
    def test_pop_keys(self):
        d = dict(a=1, b=2, c=3, d=4)
        result = pop_keys(d, 'a', 'b', 'e')
        self.assertEqual(d, dict(c=3, d=4))
        self.assertEqual(result, dict(a=1, b=2))

    def test_given(self):
        self.assertTrue(given(True, True))
        self.assertFalse(given(True, None))
        self.assertFalse(given(None, None))
        
class FileTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def tearDown(self):
        os.rmdir(self.dir)
        
    def test_import_graph(self):
        # This just checks for exceptions, not correct behavior
        with tempfile.TemporaryFile() as outf:
            import_graph(out_file=outf)
            import_graph(out_file=outf, with_system=False)
            import_graph(out_file=outf, excludes=['sys'])
            import_graph(out_file=outf, exclude_regexps=['sys.pa.*'])
            
        
    def test_can(self):
        tfn = os.path.join(self.dir, "tmpCan.dat")

        # filename
        can([1,2,3], tfn)
        self.assertEqual(uncan(tfn), [1,2,3])
        os.remove(tfn)

        # file object
        f = open(tfn, 'w')
        can([1,2,3], f)
        f.close()
        f = open(tfn)
        self.assertEqual(uncan(f), [1,2,3])
        f.close()
        os.remove(tfn)

        # protocol
        can([1,2,3], tfn, protocol=0)
        self.assertEqual(uncan(tfn), [1,2,3])
        os.remove(tfn)
        
    def test_file_size(self):
        tf = tempfile.NamedTemporaryFile()
        tf.file.write('abcd')
        tf.file.flush()
        self.assertEqual(file_size(tf.name), 4)

        # Don't worry about output, just make sure this call succeeds
        file_size(tf.name, human=True)
        tf.close()

    def test_to_filename(self):
        self.assertEqual(to_filename('foo'), 'foo')
        self.assertEqual(to_filename('foo.bar'), 'foo.bar')
        self.assertEqual(to_filename('foo.bar.baz'), 'foopbar.baz')
        
    def test_memory_usage(self):
        # This only works on linux machines -- check for existance of
        # proc filesystem before proceeding with the test
        if os.path.exists('/proc'):
            # Should return a dict of two items        
            self.assertEqual(len(memory_usage()), 2)
            self.assertEqual(len(memory_usage(pid=os.getpid())), 2)
            self.assertEqual(len(memory_usage(unit='GB')), 2)
        else:
            print "Warning, memory_usage() doesn't work on non-linux machines."

    def test_find(self):
        # This just exercises code to check for exceptions, doesn't
        # verify correct results
        find(constantly(True), with_files=False)
        find(constantly(True), with_directories=False)
        find(constantly(True), dir='../')
        find(constantly(True))

class FunctionalTest(unittest.TestCase):

    def test_memoize(self):        
        def g(x):
            """return the number of times that this function has been
            called with the current argument"""
            key = repr(x)
            if not key in gDict: gDict[key] = 1
            else: gDict[key] += 1
            return gDict[key]

        # maks sure the function does what I think it will
        gDict = {}
        self.assertEqual(g(0), 1)
        self.assertEqual(g(0), 2)

        for keyf in (string_key, pickle_key, hash_key):
            gDict = {}
            
            # Memoization blocks the actual calling of the function
            f = memoize(g, with_file=False, keyf=keyf)
            self.assertEqual(f(1), 1)
            self.assertEqual(f(1), 1)

            # Make sure that changes to a list lead to new calls to g
            list_ar = [3]
            g(list_ar)
            self.assertEqual(f(list_ar), 2)
            list_ar[0] = 4
            self.assertEqual(f(list_ar), 1)

            # Make sure that changes to the array lead to new calls to g
            if numpy:
                ar = numpy.array([1])
                g(ar)
                self.assertEqual(f(ar), 2)
                ar[0] = 2
                self.assertEqual(f(ar), 1)
        
        
    def test_logize(self):
        def f(x): return 2*x
        g, getResults = logize(f, with_file=False)

        self.assertEqual(g(1), 2)
        self.assertEqual(getResults(), [2])
        self.assertEqual(g(2), 4)
        self.assertEqual(getResults(), [2,4])

        g, getResults = logize(f, with_file=False, with_args=True)
        self.assertEqual(g(1), 2)
        self.assertEqual(getResults(), [((1,), {}, 2)])
        self.assertEqual(g(2), 4)
        self.assertEqual(getResults(), [((1,), {}, 2), ((2,), {}, 4)])

    def test_function_logger(self):
        def f(x): return 2*x
        g = FunctionLogger(f, with_file=False)
        gArgs = FunctionLogger(f, with_file=False, with_args=True)

        self.assertEqual(g.run(1), 2)
        self.assertEqual(g.results, [2])
        self.assertEqual(g.run(2), 4)
        self.assertEqual(g.results, [2,4])

        self.assertEqual(gArgs.run(1), 2)
        self.assertEqual(gArgs.results, [((1,), {}, 2)])
        self.assertEqual(gArgs.run(2), 4)
        self.assertEqual(gArgs.results, [((1,), {}, 2), ((2,), {}, 4)])

    def test_forking_call(self):
        def pid(): return os.getpid()
        def exc(): raise RuntimeError
        def unpicklable(): return lambda x: x**2
        parentPid = os.getpid()

        # Function is run in the child process
        self.assertNotEqual(parentPid, forking_call(pid))

        # Exceptions are thrown
        self.assertRaises(RuntimeError, forking_call, exc)
        
        # Exceptions are thrown in the parent process
        try: forking_call(exc)
        except RuntimeError: self.assertEqual(parentPid, os.getpid())

        self.assertRaises(Exception, forking_call, unpicklable)

    def test_forkify(self):
        self.assertEqual(forkify(lambda x: x**2)(2), 4)

    def test_constantly(self):
        self.assertTrue (constantly(True )(1,2,foo=3))
        self.assertFalse(constantly(False)(1,2,foo=3))

def test():
    suite = unittest.defaultTestLoader.loadTestsFromName('gsn_util.test')
    unittest.TextTestRunner().run(suite)

if type(__builtins__) is type({}):
    names = __builtins__.keys()
else:
    names = dir(__builtins__)

if __name__ == '__main__' and '__IPYTHON__' not in names:
    test()
