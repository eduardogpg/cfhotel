from django.db import models
from django.utils import timezone

import time

class BookingManager(models.Manager):
    def future_bookings(self, user):    
        time.sleep(2)
        return self.filter(user=user, check_in_date__gte=timezone.now())
    

