import random
from django.utils import timezone
from datetime import timedelta

class DatetimeGenerator:
    def generate(self, short_time=True, subtract=True):
        """if date == None:
            date = timezone.now()
            date_type = random.sample(range(6), 1)
            time_range = random.sample(range(10), 1)
            date -= timedelta(hours=time_range[0])
            if date_type[0] == 0:
                date -= timedelta(seconds=time_range[0])
            elif date_type[0] == 1:
                date -= timedelta(minutes=time_range[0])
            elif date_type[0] == 2:
                date -= timedelta(hours=time_range[0])
            else:
                date -= timedelta(days=time_range[0])
            return date
        else:"""
        date = timezone.now()
        time_range = random.sample(range(10), 3)
        print(time_range)
        date = date - (timedelta(minutes=time_range[0]) + \
                timedelta(hours=time_range[1]) + timedelta(days=time_range[2]))

        if not short_time:
            time_range = random.sample(range(1, 21), 1)
            date -= timedelta(days=time_range[0])

        return date
