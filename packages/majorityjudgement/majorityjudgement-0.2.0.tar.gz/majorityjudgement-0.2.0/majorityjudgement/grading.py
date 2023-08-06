"""
Majority Judgement is a method of voting proposed by Michel Balinski
and Rida Laraki in "A theory of measuring, electing, and ranking"
(http://www.pnas.org/content/104/21/8720.full)

Members of the electorate vote by assigning grades to candidates. These grades
can be any ordinal values (numbers, "A,B,C", "Good, Bad,Terrible", etc.
All that matters is the relative ordinal positions of the grades.

In this module we assume that grades are consecutive integer values starting
from 0 as the lowest. Because all that matters is the ordering, any other
grading scheme can be trivially converted to this form.

The essential idea of majority judgement is that we sort the grades assigned to
the candidate in order of most significant to least significant. At any given
point the most significant grade of those left is the lower median of the set
(i.e. the highest grade which at least 50% of the population supports).

So for example given the grading Bad, OK, OK, Good we would convert this to the
sequence

OK, Bad, OK, Good

Another candidate might have the grading

OK, Good, OK, Good

This candidate would win because their second grading is better than the first
candidate's.

This module provides a type which wraps a tally of grades and is then ordered
in terms of the majority judgement. It may then be used to implement a voting
procedure by assigning each candidate their tally and taking the maximum.
"""

import collections
import copy

def _how_many_to_pop(preceding, votes, total):
    return 1 + min(total - 2 * preceding - 1,
                   2 * preceding + 2 * votes - total)

def _calculate_judgement_trail(tallies):
    judgement_trail = []
    tallies = list(tallies)
    tallies_remaining = sum(tallies)
    while len(tallies) > 0:
        tot = 0
        for i in xrange(len(tallies)):  # pragma: no branch
            preceding = tot
            v = tallies[i]
            tot += v
            if 2 * tot >= tallies_remaining:
                if 2 * tot == tallies_remaining:
                    next_index = i+1
                    while not tallies[next_index]:
                        next_index += 1

                    relevant_indices = [i, next_index]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v + tallies[next_index],
                                                    tallies_remaining)
                    k = votes_to_pop / 2
                    votes_to_pop = k * 2
                else:
                    relevant_indices = [i]
                    votes_to_pop = _how_many_to_pop(preceding,
                                                    v,
                                                    tallies_remaining)
                    k = votes_to_pop

                tallies_remaining -= votes_to_pop
                for i in relevant_indices:
                    tallies[i] -= k

                while len(tallies) > 0 and tallies[-1] <= 0:
                    tallies.pop()
                r = [relevant_indices, k]
                judgement_trail.append(r)
                break
    return judgement_trail


class MajorityJudgement(collections.Sequence):
    """
    Objects of type MajorityJudgement behave like a lazily evaluated frozen
    list. They may be indexed, iterated over and _compared exactly as if they
    were their list of majority judgement grades.
    """
    def __init__(self, tally=None, votes=None):
        """
        Create a MajorityJudgement object from a tally of grades. Note that
        the votes are taken as tallies, not as a list of grades. i.e.
        [1,2,1] means that there is one vote each of grades 0 and 2 and 2 votes
        of grade 1, not that there 2 votes of grade 1 and 1 of grade 2.
        """

        if tally and votes:
            raise StandardError("Invalid arguments: Cannot provide both tally"
                                "and votes")

        if isinstance(tally, MajorityJudgement):
            raise TypeError("tally argument may not be of type "
                            "MajorityJudgement. It's basically impossible that"
                            " this is really what you meant to do. If you"
                            " really wanted to do that, convert it to a list" 
                            " first. Else pass it as the votes argument")

        if votes:
            if isinstance(votes, MajorityJudgement):
                self._length = votes._length
                self._judgement_trail = copy.deepcopy(votes._judgement_trail)
                return
            else:
                tally = [0 for _ in xrange(max(votes) + 1)]
                for x in votes:
                    tally[x] += 1

        self._length = sum(tally)
        self._judgement_trail = _calculate_judgement_trail(tally)

    def __repr__(self):
        return "MajorityJudgement(%s)" % (self._judgement_trail)

    def __eq__(self, other):
        return self._compare(other) == 0

    def __ne__(self, other):
        return self._compare(other) != 0

    def __lt__(self, other):
        return self._compare(other) < 0

    def __le__(self, other):
        return self._compare(other) <= 0

    def __gt__(self, other):
        return self._compare(other) > 0

    def __ge__(self, other):
        return self._compare(other) >= 0

    def __len__(self):
        return self._length

    def __getitem__(self, i):
        if isinstance(i, slice):
            if i.stop <= i.start:
                return []
            ix = 0
            result = []
            for x in self:
                if ix >= i.start and (ix - i.start) % (i.step or 1) == 0:
                    result.append(x)
                ix += 1
                if ix >= i.stop:
                    break
            return result

        if not isinstance(i, int):
            raise TypeError(
                "MajorityJudgement indices must be integers,"
                " not %s" % type(i).__name__)
        l = len(self)
        if i < 0 and i > -l:
            i = i + l
        elif i < 0 or i >= l:
            raise IndexError("Index %d out of range [0, %d)", i, len(self))
        for x, n in self._judgement_trail:    # pragma: no branch
            m = n * len(x)
            if i < m:
                return x[i % len(x)]
            i = i - m

    def __delitem__(self, i):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __setitem__(self, i, x):
        raise TypeError(
            "MajorityJudgement objects do not support modifying"
            "the contents")

    def __iter__(self):
        for (xs, n) in self._judgement_trail:
            for _ in xrange(n):
                for x in xs:
                    yield x

    def __reversed__(self):
        for (xs, n) in reversed(self._judgement_trail):
            for _ in xrange(n):
                for x in reversed(xs):
                    yield x

    def __contains__(self, x):
        if not isinstance(x, int):
            return False
        if x < 0:
            return False
        for (ys, n) in self._judgement_trail:
            if x in ys:
                return True
        return False

    def __copy__(self):
        return MajorityJudgement(votes=self)

    def __deepcopy__(self, _):
        return self.__copy__()

    def _compare(self, other):
        """
            Return an integer expressing the order relation between self and
            other. -1 if self < other, 0 if self == other, 1 if self > other.

            Ordering is defined to be equivalent to lexicographical ordering of
            list(self) and list(other), but may not fully evaluate the sequence
            and may require less iteration due to long stretches of common
            values.
        """
        if self is other:
            return 0
        if len(self) == 0 and len(other) == 0:
            return 0
        if len(self) == 0:
            return -1
        if len(other) == 0:
            return 1

        self_stack = list(reversed(self._judgement_trail))
        other_stack = list(reversed(other._judgement_trail))

        while self_stack and other_stack:
            x, xn = self_stack.pop()
            y, yn = other_stack.pop()

            m = min(xn, yn)

            if x[0] < y[0]:
                return -1
            elif y[0] < x[0]:
                return 1
            elif len(x) == len(y):
                if len(x) == 2:
                    if x[1] < y[1]:
                        return -1
                    elif y[1] < x[1]:
                        return 1
            
                if xn > yn:
                    self_stack.append((x, xn - yn))
                elif yn > xn:
                    other_stack.append((y, yn - xn))
            else:
                if xn > 1: self_stack.append((x, xn - 1))
                if yn > 1: other_stack.append((y, yn - 1))

                if len(x) > 1: self_stack.append(([x[1]], 1))
                else: other_stack.append(([y[1]], 1))

        if self_stack: return 1
        if other_stack: return -1

        return 0
