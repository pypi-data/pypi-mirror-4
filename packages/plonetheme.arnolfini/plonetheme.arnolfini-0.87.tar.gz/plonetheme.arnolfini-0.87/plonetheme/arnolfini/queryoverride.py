from collections import namedtuple
Row = namedtuple('Row', ['index', 'operator', 'values'])
from DateTime import DateTime

def _largerThan(context, row):
    tmp = {row.index: {
              'query': row.values,
              'range': 'min',
              },
          }
    return tmp

def _afterToday(context, row):
    row = Row(index=row.index,
              operator=row.operator,
              values=DateTime().earliestTime())
    return _largerThan(context, row)