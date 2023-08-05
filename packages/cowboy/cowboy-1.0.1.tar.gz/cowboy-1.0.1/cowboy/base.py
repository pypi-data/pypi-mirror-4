'base class - range'
class Range(object):
    'base class for ranges'
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def steps(self, granularity):
        '''return a list of steps at the given granularity

        if a subclass wants to provide a default for this, they should override
        the method signature to provide a default granularity.'''
        current = self.start
        while current <= self.end:
            yield current
            current += granularity

    @property
    def is_valid(self):
        'get whether this range is valid'
        return self.start <= self.end

    def __contains__(self, other):
        'test if an object is within the range'
        return self.start <= other and self.end >= other

    def __repr__(self):
        'return a nice representation of an instance'
        return u'<%s: %s to %s>' % (
            self.__class__.__name__,
            repr(self.start), repr(self.end)
        )

    def __add__(self, other):
        'get the union of two ranges'
        if type(self) != type(other):
            raise TypeError('Cannot add two unlike types')

        return self.__class__(
            min([self.start, other.start]),
            max([self.end, other.end])
        )

    def __eq__(self, other):
        'equality of two ranges'
        return self.start == other.start and self.end == other.end
