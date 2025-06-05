from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.cache import cache


class Room(models.Model):
    ROOM_TYPES = [
        ('SINGLE', 'Single Room'),
        ('DOUBLE', 'Double Room'),
        ('SUITE', 'Suite'),
    ]
    
    number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPES)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    capacity = models.IntegerField()
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Room {self.number} - {self.room_type}"


class BookingManager(models.Manager):

    def bookings_for_user(self, user):
        import time

        # time.sleep(5)

        return self.filter(user=user)

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookingManager()
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.username} - Room {self.room.number}"
    
    class Meta:
        ordering = ['-created_at']


class BookingLog(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Booking {self.booking.id} - {self.action} - {self.timestamp}"

@receiver(post_save, sender=Booking)
def invalidate_booking_history(sender, instance, *args, **kwargs):
    cache.delete(f'booking_for_user_{instance.user.pk}')
    
    cache.set(
        f'booking_for_user_{instance.user.pk}', 
        sender.objects.bookings_for_user(user=instance.user)
    )