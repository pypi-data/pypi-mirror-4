from pyutil import benchutil, randutil

from pyutil.assertutil import precondition

import collections, copy, itertools, random, sys
from stringchain.stringchain import StringChain

from cStringIO import StringIO

class StringIOy(object):
    def __init__(self):
        self.s = StringIO()

    def __len__(self):
        return self.s.tell()

    def append(self, s):
        self.s.write(s)

    def trim(self, l):
        v = self.s.getvalue()
        self.s = StringIO()
        self.s.write(v[l:])

    def popleft_new_stringchain(self, l):
        n = self.__class__()
        self.s.seek(0)
        n.s.write(self.s.read(l))
        rem = self.s.read()
        self.s = StringIO()
        self.s.write(rem)
        return n

    def popleft(self, l):
        self.s.seek(0)
        res = self.s.read(l)
        rem = self.s.read()
        self.s = StringIO()
        self.s.write(rem)
        return res

    def __str__(self):
        return self.s.getvalue()

    def copy(self):
        n = self.__class__()
        n.s = StringIO()
        x = self.s.tell()
        self.s.seek(0)
        n.s.write(self.s.read())
        self.s.seek(x)
        return n

class Stringy(object):
    def __init__(self):
        self.s = ''

    def __len__(self):
        return len(self.s)

    def append(self, s):
        self.s += s

    def trim(self, l):
        self.s = self.s[l:]

    def popleft_new_stringchain(self, l):
        n = self.__class__()
        n.s = self.s[:l]
        self.s = self.s[l:]
        return n

    def popleft(self, l):
        res = self.s[:l]
        self.s = self.s[l:]
        return res

    def __str__(self):
        return self.s

    def copy(self):
        n = self.__class__()
        n.s = self.s
        return n

class SimplerStringChain(object):
    def __init__(self):
        self.ss = []
        self.len = 0

    def __len__(self):
        return self.len

    def append(self, s):
        self.ss.append(s)
        self.len += len(s)

    def _collapse(self):
        s = ''.join(self.ss)
        del self.ss[:]
        self.ss.append(s)

    def trim(self, l):
        self._collapse()
        self.ss[0] = self.ss[0][l:]
        self.len = len(self.ss[0])

    def popleft_new_stringchain(self, l):
        self._collapse()
        n = self.__class__()
        n.ss.append(self.ss[0][:l])
        self.ss[0] = self.ss[0][l:]
        self.len = len(self.ss[0])
        return n

    def popleft(self, l):
        self._collapse()
        res = self.ss[0][:l]
        self.ss[0] = self.ss[0][l:]
        self.len = len(self.ss[0])
        return res

    def __str__(self):
        self._collapse()
        return self.ss[0]

    def copy(self):
        n = self.__class__()
        n.ss = copy.copy(self.ss)
        n.len = self.len
        return n

class Dequey(object):
    def __init__(self):
        self.d = collections.deque()

    def __len__(self):
        return len(self.d)

    def append(self, s):
        self.d.extend(s)

    def trim(self, l):
        l = min(l, len(self.d))
        for i in range(l):
            self.d.popleft()

    def popleft_new_stringchain(self, l):
        l = min(l, len(self.d))
        n = self.__class__()
        for i in range(l):
            n.d.append(self.d.popleft())
        return n

    def popleft(self, l):
        l = min(l, len(self.d))
        res = []
        for i in range(l):
            res.append(self.d.popleft())
        return ''.join(res)

    def __str__(self):
        return ''.join(list(self.d))

    def copy(self):
        n = self.__class__()
        n.d = copy.copy(self.d)
        return n

class StringChainWithList(object):
    def __init__(self):
        self.d = []
        self.ignored = 0
        self.tailignored = 0
        self.len = 0

    def append(self, s):
        """ Add s to the end of the chain. """
        if not s:
            return

        # First trim off any ignored tail bytes.
        if self.tailignored:
            self.d[-1] = self.d[-1][:-self.tailignored]
            self.tailignored = 0

        self.d.append(s)
        self.len += len(s)

    def __str__(self):
        """ Return the entire contents of this chain as a single
        string. (Obviously this requires copying all of the bytes, so don't do
        this unless you need to.) This has a side-effect of collecting all the
        bytes in this StringChain object into a single string which is stored
        in the first element of its internal deque. """
        self._collapse()
        if self.d:
            return self.d[0]
        else:
            return ''

    def popleft_new_stringchain(self, bytes):
        """ Remove some of the leading bytes of the chain and return them as a
        new StringChain object. (Use str() on it if you want the bytes in a
        string, or call popleft() instead of popleft_new_stringchain().) """
        if not bytes or not self.d:
            return self.__class__()

        assert precondition(bytes >= 0, bytes)

        # We need to add at least this many bytes to the new StringChain.
        bytesleft = bytes + self.ignored
        n = self.__class__()
        n.ignored = self.ignored

        while bytesleft > 0 and self.d:
            s = self.d.pop(0)
            self.len -= (len(s) - self.ignored)
            n.d.append(s)
            n.len += (len(s)-self.ignored)
            self.ignored = 0
            bytesleft -= len(s)

        overrun = - bytesleft

        if overrun > 0:
            self.d.insert(0, s)
            self.len += overrun
            self.ignored = len(s) - overrun
            n.len -= overrun
            n.tailignored = overrun
        else:
            self.ignored = 0

        # Either you got exactly how many you asked for, or you drained self entirely and you asked for more than you got.

        return n

    def popleft(self, bytes):
        """ Remove some of the leading bytes of the chain and return them as a
        string. """
        if not bytes or not self.d:
            return ''

        assert precondition(bytes >= 0, bytes)

        # We need to add at least this many bytes to the result.
        bytesleft = bytes
        resstrs = []

        s = self.d.pop(0)
        if self.ignored:
            s = s[self.ignored:]
            self.ignored = 0
        self.len -= len(s)
        resstrs.append(s)
        bytesleft -= len(s)

        while bytesleft > 0 and self.d:
            s = self.d.pop(0)
            self.len -= len(s)
            resstrs.append(s)
            bytesleft -= len(s)

        overrun = - bytesleft

        if overrun > 0:
            self.d.insert(0, s)
            self.ignored = (len(s) - overrun)
            self.len += overrun
            resstrs[-1] = resstrs[-1][:-overrun]

        resstr = ''.join(resstrs)

        # Either you got exactly how many you asked for, or you drained self entirely and you asked for more than you got.
        assert (len(resstr) == bytes) or ((not self.d) and (bytes > self.len)), (len(resstr), bytes, len(self.d), overrun)


        return resstr

    def __len__(self):
        return self.len

    def trim(self, bytes):
        """ Trim off some of the leading bytes. """
        self.ignored += bytes
        self.len -= bytes
        while self.d and self.ignored >= len(self.d[0]):
            s = self.d.pop(0)
            self.ignored -= len(s)
        if self.len < 0:
            self.len = 0
        if not self.d:
            self.ignored = 0

    def copy(self):
        n = self.__class__()
        n.ignored = self.ignored
        n.len = self.len
        n.d = copy.copy(self.d)
        return n

    def _collapse(self):
        """ Concatenate all of the strings into one string and make that string
        be the only element of the chain. (Obviously this requires copying all
        of the bytes, so don't do this unless you need to.) """
        # First trim off any leading ignored bytes.
        if self.ignored:
            self.d[0] = self.d[0][self.ignored:]
            self.ignored = 0
        # Then any tail ignored bytes.
        if self.tailignored:
            self.d[-1] = self.d[-1][:-self.tailignored]
            self.tailignored = 0
        if len(self.d) > 1:
            newstr = ''.join(self.d)
            del self.d[:]
            self.d.append(newstr)

def accit(accumulator, nextstring):
    accumulator += nextstring
    return accumulator

class B(object):
    def __init__(self, impl):
        self.impl = impl

    def init(self, N, randstr=randutil.insecurerandstr, rr=random.randrange):
        random.seed(76)
        self.l = []
        self.gulpsizes = []
        self.r = []
        self.a = self.impl()

        bytesleft = N
        for i in xrange(N / 2048):
            nextchunksize = random.randrange(0, 4096)
            self.l.append(randstr(nextchunksize))
            bytesleft -= nextchunksize
            self.gulpsizes.append(random.randrange(0, 2048))

    def init_loaded(self, N):
        self.init(N)
        for s in self.l:
            self.a.append(s)

    def accumulate_then_one_gulp(self, N):
        for s in self.l:
            self.a.append(s)
        s = str(self.a)
        return s

    def inline_acc_onegulp(self, N):
        x = ''
        for s in self.l:
            x += s
        return x

    def out_of_line_acc_onegulp(self, N):
        x = ''
        for s in self.l:
            x = accit(x, s)
        return x

    def _append(self, nextstring):
        self.x += nextstring

    def oo_acc_onegulp(self, N):
        self.x = ''
        for s in self.l:
            self._append(s)
        return self.x

    def accumulate_then_many_gulps_sc(self, N):
        for s in self.l:
            self.a.append(s)
        while len(self.a):
            str(self.a.popleft_new_stringchain(4000))

    def accumulate_then_many_gulps(self, N):
        for s in self.l:
            self.a.append(s)
        for gulpsize in self.gulpsizes:
            self.a.popleft(gulpsize)

    def product_and_consume_sc(self, N):
        acc=True
        i = 0
        while (i < len(self.l)) or (len(self.a) > 0):
            if (acc) or (i == len(self.l)):
                acc = False
                str(self.a.popleft_new_stringchain(3000))
            else:
                acc = True
                self.a.append(self.l[i])
                i += 1

    def produce_and_consume(self, N):
        # Let's accumulate approximately twice as fast as we consume. It
        # seems as fair a measure as any.
        for (chunk, gulpsize) in itertools.izip(self.l, self.gulpsizes):
            self.a.append(chunk)
            self.a.popleft(gulpsize)

# Report benchmarking results in nanoseconds per byte.
UNITS_PER_SECOND=1000000000

def quick_bench(profile=False):
    if profile:
        from pyutil import time_format
        allprofresultsfileobj = open("stringchain-bench-quick-all.txt", "wab+")
        allprofresultsfileobj.write(time_format.iso_utc() + "\n")
        import statprof
        statprof.start()
        
    print "N is the total number of bytes produced and consumed; results are in nanoseconds per byte (scientific notation)"
    print
    for impl in [StringChain, Stringy]:
        print "impl: ", impl.__name__
        b = B(impl)
        for (task, initfunc) in [
            (b.accumulate_then_one_gulp, b.init),
            (b.produce_and_consume, b.init),
            ]:
            print "task: ", task.__name__
            for BSIZE in [1*10**5, 1*10**6,]:
                print "N: %9d" % BSIZE,
                sys.stdout.flush()
                benchutil.rep_bench(task, BSIZE, initfunc=initfunc, MAXTIME=0.5, MAXREPS=20, UNITS_PER_SECOND=UNITS_PER_SECOND)
        print

    print "nanoseconds per byte produced and consumed"
    print

    if profile:
        statprof.stop()
        statprof.display(allprofresultsfileobj)

def slow_bench(profile=False):
    if profile:
        from pyutil import time_format
        # profresultsfileobj = open("stringchain-bench-slow.txt", "wab+")
        # profresultsfileobj.write(time_format.iso_utc() + "\n")

        allprofresultsfileobj = open("stringchain-bench-slow-all.txt", "wab+")
        allprofresultsfileobj.write(time_format.iso_utc() + "\n")
        import statprof
        statprof.start()
        
    print "N is the total number of bytes produced and consumed; results are in nanoseconds per byte (scientific notation)"
    print
    for impl in [
        StringChain,
        SimplerStringChain,
        # StringIOy,
        Stringy,
        # StringChainWithList,
        # Dequey
        ]:
        print "impl: ", impl.__name__
        b = B(impl)
        for (task, initfunc) in [
            (b.accumulate_then_one_gulp, b.init),
            (b.accumulate_then_many_gulps, b.init_loaded),
            (b.produce_and_consume, b.init),
            ]:
            print "task: ", task.__name__
            for BSIZE in [4*10**6, 8*10**6, 16*10**6, 32*10**6]:
                print "N: %10d" % BSIZE,
                sys.stdout.flush()
                benchutil.rep_bench(task, BSIZE, initfunc=initfunc, UNITS_PER_SECOND=UNITS_PER_SECOND)
        print

    print "nanoseconds per byte produced and consumed"
    print

    if profile:
        statprof.stop()
        statprof.display(allprofresultsfileobj)
