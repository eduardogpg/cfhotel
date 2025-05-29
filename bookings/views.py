from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Room, Booking
from datetime import datetime

def room_list(request):
    rooms = Room.objects.filter(is_available=True)
    return render(request, 'bookings/room_list.html', {'rooms': rooms})

@login_required
def book_room(request, room_id):
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        
        try:
            check_in_date = datetime.strptime(check_in, '%Y-%m-%d').date()
            check_out_date = datetime.strptime(check_out, '%Y-%m-%d').date()
            
            if check_in_date < timezone.now().date():
                messages.error(request, 'Check-in date cannot be in the past')
                return redirect('book_room', room_id=room_id)
            
            if check_out_date <= check_in_date:
                messages.error(request, 'Check-out date must be after check-in date')
                return redirect('book_room', room_id=room_id)
            
            # Calculate number of nights and total price
            nights = (check_out_date - check_in_date).days
            total_price = room.price_per_night * nights
            
            booking = Booking.objects.create(
                user=request.user,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                total_price=total_price
            )
            
            messages.success(request, 'Booking created successfully!')
            return redirect('bookings:booking_history')
            
        except ValueError:
            messages.error(request, 'Invalid date format')
            return redirect('book_room', room_id=room_id)
    
    return render(request, 'bookings/book_room.html', {'room': room})

@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'bookings/booking_history.html', {'bookings': bookings})
