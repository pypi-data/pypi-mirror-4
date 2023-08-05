from itertools import islice
from datetime import date, timedelta


def isplitter(iterable, size):
    it = iter(iterable)
    chunk = list(islice(it, size))
    while chunk:
        yield chunk
        chunk = list(islice(it, size))


def daterange(start_date, end_date, frequency='daily'):
    if frequency == 'yearly':
        for n in range(end_date.year - start_date.year + 1):
            yield date(start_date.year + n, start_date.month, start_date.day)
    elif frequency == 'monthly':
        for n in range(12 * start_date.year + start_date.month - 1, 12 * end_date.year + end_date.month):
            year, month = divmod(n, 12)
            yield date(year, month + 1, start_date.day)
    else:
        for n in range((end_date - start_date).days + 1):
            yield (start_date + timedelta(n)).date()
