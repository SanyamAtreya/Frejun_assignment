from rest_framework import serializers
from .models import *

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = ['id', 'name', 'age', 'gender', 'has_child', 'is_child']


class TicketSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer()

    class Meta:
        model = Ticket
        fields = [
            'id',
            'passenger',
            'status',
            'berth_type',
            'berth_number',
            'created_at'
        ]
