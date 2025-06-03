from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Room, Booking, BookingLog
from datetime import datetime
from bookings.services.service import BookingService, BookingEmailService, PaymentService
from datetime import datetime
from django.views.decorators.cache import cache_page

from django.core.cache import cache
from django.utils.cache import _generate_cache_key

@cache_page(60 * 15)
def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'bookings/room_list.html', {'rooms': rooms})


@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        check_in = datetime.strptime(check_in, '%Y-%m-%d').date()
        check_out = datetime.strptime(check_out, '%Y-%m-%d').date()

        try:
            mail_service = BookingEmailService()
            payment_service = PaymentService()
            booking_service = BookingService(mail_service, payment_service)

            booking = booking_service.create_booking(
                user=request.user,
                room=room,
                check_in_date=check_in,
                check_out_date=check_out
            )
            
            messages.success(request, 'Booking created successfully!')
            return redirect('bookings:booking_history')
        
        except Exception as e:
            print("\n\n\n\n", e)
            messages.error(request, 'No es posible crear la reservación. Contacte con soporte.')
    
    return render(request, 'bookings/book_room.html', {'room': room})

@login_required
# @cache_page(60 * 15, key_prefix="booking_history")
def booking_history(request):
    bookings = cache.get('my_booking_history')
    
    if not bookings:
        bookings = Booking.objects.future_bookings(request.user)
        cache.set('my_booking_history', bookings, timeout=60 * 10, version=1)

    return render(request, 'bookings/booking_history.html', {'bookings': bookings})
