from typing import Optional
from bookings.models import Booking, Room, BookingLog
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from bookings.utils.errors import BookingError, CheckInDateError
from django.db import transaction

class BookingEmailService:
    def send_confirmation_mail(self):
        print(">>> Mail enviado exitosamente.")

class PaymentService:
    def validate_payment(self):
        return True


class BookingService:
    def __init__(
            self,
            mail_service: BookingEmailService,
            payment_service: PaymentService
        ) -> None:
        self.mail_service = mail_service
        self.payment_service = payment_service

    @transaction.atomic
    def create_booking(
        self,
        *,
        user: User,
        room: Room,
        check_in_date: date,
        check_out_date: date
    ) -> Optional[Booking | None]:
        if not user:
            raise BookingError('User requerido')

        if not room:
            raise BookingError('Room requerido')
        
        if not room.is_available:
            raise BookingError('El cuarto no esta disponible')

        if not check_in_date or not check_out_date:
            raise BookingError('check_in_date y check_out_date requerido')
        
        if check_in_date < timezone.now().date():
            raise CheckInDateError('Check-in date cannot be in the past')
        
        if check_out_date <= check_in_date:
            raise CheckInDateError('Check-out date must be after check-in date')
        
        nights = (check_out_date - check_in_date).days
        total_price = room.price_per_night * nights
        
        has_bookings = Booking.objects.filter(
            room=room,
            check_in_date__lte=check_out_date,
            check_out_date__gte=check_in_date
        ).exists()

        if has_bookings:
            raise BookingError('No es possible reservar este cuarto.')

        try:
            booking = Booking.objects.create(
                user=user,
                room=room,
                check_in_date=check_in_date,
                check_out_date=check_out_date,
                total_price=total_price
            )

            self.payment_service.validate_payment()

            BookingLog.objects.create(
                booking=booking,
                action='create',
                user=user
            )
            
            self.mail_service.send_confirmation_mail()
            
            # Facturar

            return booking
        except Exception as e:
            raise BookingError('No fue posible completar la operación') from e