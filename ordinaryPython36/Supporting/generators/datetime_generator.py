import random
from django.utils import timezone
from datetime import timedelta

class DatetimeGenerator:
    def generate(self, date=None):
        if date == None:
            date = timezone.now()
            date_type = random.sample(range(6), 1)
            time_range = random.sample(range(10), 1)
            if date_type[0] == 0:
                date -= timedelta(seconds=time_range[0])
            elif date_type[0] == 1:
                date -= timedelta(minutes=time_range[0])
            elif date_type[0] == 2:
                date -= timedelta(hours=time_range[0])
            else:
                date -= timedelta(days=time_range[0])
            return date
        else:
            time_range = random.sample(range(1, 6), 4)
            date += timedelta(seconds=time_range[0]) + timedelta(minutes=time_range[1]) + \
                    timedelta(hours=time_range[2]) + timedelta(days=time_range[3])
            return date