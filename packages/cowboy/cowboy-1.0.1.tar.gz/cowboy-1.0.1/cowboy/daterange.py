'date range object'
from cowboy.base import Range
from datetime import timedelta

class DateRange(Range):
    'represent a range of dates'
    def steps(self, granularity=timedelta(days=1)):
        'return superclass steps with default granularity of one day'
        return super(DateRange, self).steps(granularity)
