import copy

from pyutil.assertutil import precondition, _assert

from collections import deque

# Note: when changing this class, you should set this to True. test_chain.py sets it to True.
debug = False

class StringChain(object):
    def __init__(self):
        self.d = deque()
        self.ignored = 0
        self.tailignored = 0
        self.len = 0

    def append(self, s):
        """ Add s to the end of the chain. """
        #self._assert_invariants()
        if not s:
            return

        # First trim off any ignored tail bytes.
        if self.tailignored:
            self.d[-1] = self.d[-1][:-self.tailignored]
            self.tailignored = 0

        self.d.append(s)
        self.len += len(s)
        #self._assert_invariants()

    def appendleft(self, s):
        """ Add s to the beginning of the chain. """
        #self._assert_invariants()
        if not s:
            return

        # First trim off any ignored bytes.
        if self.ignored:
            self.d[0] = self.d[0][self.ignored:]
            self.ignored = 0

        self.d.appendleft(s)
        self.len += len(s)
        #self._assert_invariants()

    def DISABLED__str__(self):
        """ Return the entire contents of this chain as a single
        string. (Obviously this requires copying all of the bytes, so don't
        do this unless you need to.) This has a side-effect of collecting all
        the bytes in this StringChain object into a single string which is
        stored in the first element of its internal deque."""
        self._collapse()
        if self.d:
            return self.d[0]
        else:
            return ''

    def popall(self):
        """ Return the entire contents of this chain as a single string and
        empty this chain. (Obviously this requires copying all of the bytes,
        so don't do this unless you need to.)"""
        res = self.__str__()
        self.clear()
        return res

    def popall_new_stringchain(self):
        """ Return the entire contents of this chain and empty this
        chain."""
        res = self.copy()
        self.clear()
        return res

    def popleft_new_stringchain(self, numbytes):
        """ Remove some of the leading bytes of the chain and return them as a
        new StringChain object. (Use str() on it if you want the bytes in a
        string, or call popleft() instead of popleft_new_stringchain().) """
        #self._assert_invariants()
        if not numbytes or not self.d:
            return self.__class__()

        precondition(numbytes > 0, numbytes)

        # We need to add at least this many bytes to the new StringChain.
        bytesleft = numbytes + self.ignored
        n = self.__class__()
        n.ignored = self.ignored

        while bytesleft > 0 and self.d:
            s = self.d.popleft()
            self.len -= (len(s) - self.ignored)
            n.d.append(s)
            n.len += (len(s)-self.ignored)
            self.ignored = 0
            bytesleft -= len(s)

        overrun = - bytesleft

        if overrun > 0:
            self.d.appendleft(s)
            self.len += overrun
            self.ignored = len(s) - overrun
            n.len -= overrun
            n.tailignored = overrun
        else:
            self.ignored = 0

        # Either you got exactly how many you asked for, or you drained self entirely and you asked for more than you got.
        # if debug:
        #     _assert((n.len == numbytes) or ((not self.d) and (numbytes > self.len)), (n.len, numbytes, len(self.d)))

        # self._assert_invariants()
        # n._assert_invariants()
        return n

    def popleft_at_least_new_stringchain(self, numbytes):
        """ Remove some of the leading bytes of the chain -- at least
        `numbytes` of them -- and return them as a new StringChain
        object. (Use str() on it if you want the bytes in a string, or call
        popleft() instead of popleft_new_stringchain().)

        This can be slightly more efficient than popleft_new_stringchain(),
        since it doesn't have to slice a string in order to get exactly
        `numbytes`."""
        # self._assert_invariants()
        if not numbytes or not self.d:
            return self.__class__()

        precondition(numbytes > 0, numbytes)

        # We need to add at least this many bytes to the new StringChain.
        bytesleft = numbytes + self.ignored
        n = self.__class__()
        n.ignored = self.ignored

        while bytesleft > 0 and self.d:
            s = self.d.popleft()
            self.len -= (len(s) - self.ignored)
            n.d.append(s)
            n.len += (len(s)-self.ignored)
            self.ignored = 0
            bytesleft -= len(s)

        self.ignored = 0

        # Either you got at least how many you asked for, or you drained self entirely and you asked for more than you got.
        # if debug:
        #     _assert((n.len == numbytes) or ((not self.d) and (numbytes > self.len)), (n.len, numbytes, len(self.d)))

        # self._assert_invariants()
        # n._assert_invariants()
        return n

    def popleft(self, numbytes):
        """ Remove some of the leading bytes of the chain and return them as a
        string. """
        # self._assert_invariants()
        if not numbytes or not self.d:
            return ''

        precondition(numbytes > 0, numbytes)

        # We need to add at least this many bytes to the result.
        bytesleft = numbytes
        resstrs = []

        s = self.d.popleft()
        if self.ignored:
            s = s[self.ignored:]
            self.ignored = 0
        self.len -= len(s)
        resstrs.append(s)
        bytesleft -= len(s)

        while bytesleft > 0 and self.d:
            s = self.d.popleft()
            self.len -= len(s)
            resstrs.append(s)
            bytesleft -= len(s)

        overrun = - bytesleft

        if overrun > 0:
            self.d.appendleft(s)
            self.ignored = (len(s) - overrun)
            self.len += overrun
            resstrs[-1] = resstrs[-1][:-overrun]

        resstr = ''.join(resstrs)

        # Either you got exactly how many you asked for, or you drained self entirely and you asked for more than you got.
        # if debug:
        #     _assert((len(resstr) == numbytes) or ((not self.d) and (numbytes > self.len)), (len(resstr), numbytes, len(self.d), overrun))

        # self._assert_invariants()

        return resstr

    def popleft_at_least(self, numbytes):
        """ Remove some of the leading bytes of the chain -- at least
        `numbytes` of them -- and return them as a string. This can can be
        slightly more efficient than popleft(), since it doesn't have to
        slice a string in order to get exactly `numbytes`."""
        # self._assert_invariants()
        if not numbytes or not self.d:
            return ''

        precondition(numbytes > 0, numbytes)

        # We need to add at least this many bytes to the result.
        bytesleft = numbytes
        resstrs = []

        s = self.d.popleft()
        if self.ignored:
            s = s[self.ignored:]
            self.ignored = 0
        self.len -= len(s)
        resstrs.append(s)
        bytesleft -= len(s)

        while bytesleft > 0 and self.d:
            s = self.d.popleft()
            self.len -= len(s)
            resstrs.append(s)
            bytesleft -= len(s)

        resstr = ''.join(resstrs)

        # Either you got at least how many you asked for, or you drained self entirely and you asked for more than you got.
        # if debug:
        #     _assert((len(resstr) >= numbytes) or ((not self.d) and (numbytes > self.len)), (len(resstr), numbytes, len(self.d)))

        # self._assert_invariants()

        return resstr

    def __len__(self):
        # self._assert_invariants()
        return self.len

    def trim(self, numbytes):
        """ Trim off some of the leading bytes. """
        # self._assert_invariants()
        self.ignored += numbytes
        self.len -= numbytes
        while self.d and self.ignored >= len(self.d[0]):
            s = self.d.popleft()
            self.ignored -= len(s)
        if self.len < 0:
            self.len = 0
        if not self.d:
            self.ignored = 0
        # self._assert_invariants()

    def clear(self):
        """ Empty it out. """
        # self._assert_invariants()
        self.d.clear()
        self.ignored = 0
        self.tailignored = 0
        self.len = 0
        # self._assert_invariants()

    def copy(self):
        n = self.__class__()
        n.ignored = self.ignored
        n.tailignored = self.tailignored
        n.len = self.len
        n.d = copy.copy(self.d)
        # n._assert_invariants()
        return n

    def _assert_invariants(self):
        if not debug:
            return True
        _assert(self.ignored >= 0, self.ignored)
        _assert(self.tailignored >= 0, self.tailignored)
        _assert(self.len >= 0, self.len)
        _assert((not self.d) or (self.d[0]), "First element is required to be non-empty.", self.d and self.d[0])
        _assert((not self.d) or (self.ignored < len(self.d[0])), self.ignored, self.d and len(self.d[0]))
        _assert((not self.d) or (self.tailignored < len(self.d[-1])), self.tailignored, self.d and len(self.d[-1]))
        _assert(self.ignored+self.len+self.tailignored == sum([len(x) for x in self.d]), self.ignored, self.len, self.tailignored, sum([len(x) for x in self.d]))
        return True

    def _collapse(self):
        """ Concatenate all of the strings into one string and make that string
        be the only element of the chain. (Obviously this requires copying all
        of the bytes, so don't do this unless you need to.) """
        # self._assert_invariants()
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
            self.d.clear()
            self.d.append(newstr)
        # self._assert_invariants()
