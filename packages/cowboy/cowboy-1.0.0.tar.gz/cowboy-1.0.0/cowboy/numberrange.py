'range for numbers'
from cowboy.base import Range

class NumberRange(Range):
    'range of numbers'
    def steps(self, granularity=1):
        'return superclass steps with default granularity of 1'
        return super(NumberRange, self).steps(granularity)
