from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *


urlpatterns = [
    path('v1/tickets/book', BookTicketAPIView.as_view(), name='book-ticket'),
    path('v1/tickets/cancel/<int:ticket_id>', CancelTicketAPIView.as_view(), name='cancel-ticket'),
    path('v1/tickets/booked', BookedTicketsAPIView.as_view(), name='booked-tickets'),
    path('v1/tickets/available', AvailableTicketsAPIView.as_view(), name='available-tickets'),
]