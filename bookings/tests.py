from django.test import TestCase
from django.contrib.auth.models import User
from bookings.models import Booking, Room, BookingLog
from bookings.services.service import BookingService, BookingEmailService, PaymentService
from datetime import date, timedelta
from bookings.utils.errors import BookingError, CheckInDateError
from unittest.mock import patch

class BookingServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='user_test',
            password='user_test_1234'
        )

        self.room = Room.objects.create(
            number=101,
            room_type='Suite',
            price_per_night=10,
            capacity=2,
            description='description',
            is_available=True
        )
        self.payment_service = PaymentService()
        self.mail_service = BookingEmailService()
        
        self.booking_service = BookingService(
            self.mail_service,
            self.payment_service
        )

    def test_create_valid_booking(self):
        booking = self.booking_service.create_booking(
            user=self.user,
            room=self.room,
            check_in_date=date.today(),
            check_out_date=date.today() + timedelta(days=2)
        )

        self.assertIsNotNone(booking)
        self.assertEqual(1, Booking.objects.count())
        self.assertEqual(1, BookingLog.objects.count())

    def test_validate_available_room(self):
        room = Room.objects.create(
            number=102,
            room_type='Suite',
            price_per_night=10,
            capacity=2,
            description='description',
            is_available=False
        )

        with self.assertRaises(BookingError):
            self.booking_service.create_booking(
                user=self.user,
                room=room,
                check_in_date=date.today(),
                check_out_date=date.today() + timedelta(days=2)
            )

    def test_past_dates(self):
        with self.assertRaises(CheckInDateError):
            self.booking_service.create_booking(
                user=self.user,
                room=self.room,
                check_in_date=date.today() - timedelta(days=10),
                check_out_date=date.today() - timedelta(days=5)
            )
    @patch(
        'bookings.services.service.BookingEmailService.send_confirmation_mail'
    )
    def test_send_confirmation_mail_fail(self, mock_send_confirmation_mail):
        mock_send_confirmation_mail.side_effect = Exception('Opps!!!')

        with self.assertRaises(BookingError):
            self.booking_service.create_booking(
                user=self.user,
                room=self.room,
                check_in_date=date.today(),
                check_out_date=date.today() + timedelta(days=5)
            )

    @patch(
        'bookings.services.service.PaymentService.validate_payment'
    )
    def test_validate_payment_fail(self, mock_validate_payment):
        mock_validate_payment.side_effect = Exception('Opps!!!')

        with self.assertRaises(BookingError):
            self.booking_service.create_booking(
                user=self.user,
                room=self.room,
                check_in_date=date.today(),
                check_out_date=date.today() + timedelta(days=5)
            )
        self.assertEqual(0, Booking.objects.count())
        self.assertEqual(0, BookingLog.objects.count())
           