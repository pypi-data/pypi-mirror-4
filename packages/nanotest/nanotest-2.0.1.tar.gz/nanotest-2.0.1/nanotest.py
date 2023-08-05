import inspect
import re

version = "v2.0.1"

class Nanotester:
    """Initialize a nanotest tester object."""
    def __init__(self):
        self.results   = [] # test results go here
        self.nodestack = [] # used to build hash for struct compares
        self.xhash = {}     # experimental struct hash
        self.ghash = {}     # given struct hash
        self.re_re   = re.compile("\:re\:")
        self.re_type = re.compile("\:ty\:")

    def test(self, xpmtl, given, msg, invert=False):
        """Test two values for equality"""
        if type(xpmtl) != type(given):
            res = self._result(False, type(given), type(xpmtl), msg, "Types don't match")
            self.results.append(res)
        elif isinstance(xpmtl, (tuple, list, dict)):
            self._hash_n_comp(xpmtl, given, msg, invert)
        else:
            passed, reason = self._test_scalar(xpmtl, given, msg, invert)
            self.results.append(self._result(passed, given, xpmtl, msg, reason))
                

    def untest(self, xpmtl, given, msg):
        """Test two values for inequality"""
        self.test(xpmtl, given, msg, invert=True)

    def _result(self, success, given, xpmtl, msg, *args):
        res = {}
        reason = None
        if len(args) > 0:
            reason = args[0]
        # get filename, line num, stuff. should always want the -2nd frame in the stack, since -1 is the exec(). this 
        # may need to be cased when test injection is implemented
        frame = inspect.getouterframes(inspect.currentframe())[-2]
        # frame, filename, linenum, function_name, lines, index
        res["file"]  = frame[1]
        res["line"]  = frame[2]
        res["pass"]  = success
        res["msg"]  = msg
        res["comp"] = []
        res["comp"].append(self._subresult(xpmtl, given, reason))
        return res

    def _subresult(self, xpmtl, given, reason):
        sres = {}
        sres["xpect"]  = given
        sres["got"]    = xpmtl
        sres["reason"] = reason
        return sres

    def _test_scalar(self, xpmtl, given, msg, invert):
        if self.re_re.match(str(given)):
            return self._re_match(xpmtl, given, msg, invert)
        else:
            return self._is_eq(xpmtl, given, msg, invert)

    def _is_eq(self, xpmtl, given, msg, invert):
        if (xpmtl == given and invert == False) or (xpmtl != given and invert == True):
            return True, None
        else:
            return False, None

    def _re_match(self, xpmtl, given, msg, invert):
        restr = given[4:]
        if re.search(restr, str(xpmtl)):
            return True, None
        else:
            if invert:
                return True, None
            else:
                return False, "regexp failure ('got' is not a match for 'expected')"


    def _hash_n_comp(self, xpmtl, given, msg, invert):
        # just a helper function which resets states, hashes the structs to be compared, then calls _compare()
        self.nodestack = []
        self.xhash = {}
        self._hash(xpmtl, self.xhash)
        self.nodestack = []
        self.ghash = {}
        self._hash(given, self.ghash)
        self._compare(msg, invert)

    def _hash(self, element, hashdict):
        if isinstance(element, (tuple, list, dict)):
            # composites are handled here
            if isinstance(element, (dict,)):
                # for dicts we push a 'd' onto the stack for "dict",then push each dict key onto the stack and call
                # ourselves on that key's value
                self.nodestack.append('d')
                for key in sorted(element.keys(), key=lambda key: str(key)):
                    self.nodestack.append(str(key))
                    self._hash(element[key], hashdict)
                    self.nodestack.pop()
            else:
                # lists and tuples are handled like dicts, but get 'l' or 't' on the stack
                if isinstance(element, (list,)):
                    self.nodestack.append('l')
                else:
                    self.nodestack.append('t')
                for idx, subelem in enumerate(element):
                    self.nodestack.append(str(idx))
                    self._hash(subelem, hashdict)
                    self.nodestack.pop()
            self.nodestack.pop()
        else:
            # leafnodes (scalar values) handled here
            key = ".".join(self.nodestack)
            hashdict[key] = element

    def _compare(self, msg, invert):
        if invert:
            # for an inverted test, our only failure condition is equality. a single mismatch is enough to declare
            # success and return.
            mismatch = self._inv_compare(self.xhash, self.ghash)
            if not mismatch:
                mismatch = self._inv_compare(self.ghash, self.xhash)
            if not mismatch:
                self.results.append(self._result(False, None, None, msg, "structs were identical"))
            self.results.append(self._result(True, None, None, msg, None))
            return

        # normal compares are more complex.
        failed = False
        failkeys = []
        for key in sorted(self.xhash.keys()):
            # see if the current key has any of failkeys[] as a prefix. if so, we do not want to proceed; we'll
            # just be producing mismatch cascade errors
            fkmatch = False
            for fk in failkeys:
                if re.match(fk, key): fkmatch = True
            if fkmatch: continue
            # actual comparison starts here
            if key not in self.ghash:
                # key mismatch results in adding a mismatch condition to this test's result. the tests for 'failed'
                # let us know whether we're adding the FIRST mismatch or not. only compares have this tracking
                result = "node {} (value '{}') only in experimental struct".format(key, self.xhash[key])
                if failed:
                    self.results[-1]["comp"].append(self._subresult(None, None, result))
                else:
                    failed = True
                    failkeys.append(key[:-2]) # key mismatch; add (most of) key to failkeys[]
                    self.results.append(self._result(False, None, None, msg, result))
            else:
                # if the key exists in xhash + ghash, call _test_scalar() to see if they are eqivalent
                passed, reason = self._test_scalar(self.ghash[key], self.xhash[key], None, False)
                if not passed:
                    result= "node {} values don't match".format(key)
                    if failed:
                        self.results[-1]["comp"].append(self._subresult(self.ghash[key], self.xhash[key], result))
                    else:
                        failed = True
                        self.results.append(self._result(False, self.ghash[key], self.xhash[key], msg, result))
        # normal compare, step 2: repeat key comparison with ghash as the source. there's no need to check scalars
        # because we've already tested everything which is in both structs.
        failkeys = []
        for key in sorted(self.ghash.keys()):
            fkmatch = False
            for fk in failkeys:
                if re.match(fk, key): fkmatch = True
            if fkmatch: continue
            if key not in self.xhash:
                result = "node {} (value '{}') only in given struct".format(key, self.ghash[key])
                if failed:
                    self.results[-1]["comp"].append(self._subresult(None, None, result))
                else:
                    failed = True
                    failkeys.append(key[:-2])
                    self.results.append(self._result(False, None, None, msg, result))
        # finally, if failed still isn't True, then the compare is a pass
        if not failed:
            self.results.append(self._result(True, None, None, msg, None))

    def _inv_compare(self, a, b):
        for key in sorted(a.keys()):
            if key not in b:
                return True
            else:
                passed, reason = self._test_scalar(a[key], b[key], None, False)
                if not passed: return True
        return False
