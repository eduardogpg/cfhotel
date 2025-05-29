from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.room_list, name='room_list'),
    path('book/<int:room_id>/', views.book_room, name='book_room'),
    path('history/', views.booking_history, name='booking_history'),
] 