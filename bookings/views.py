from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Room, Booking, BookingLog
from datetime import datetime
from bookings.services.service import BookingService, BookingEmailService
from datetime import datetime

def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

def send_booking_confirmation_email(booking: Booking):
    print(f"Sending email for booking {booking.id}")

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
            booking_service = BookingService(mail_service)

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
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/booking_history.html', {'bookings': bookings})
