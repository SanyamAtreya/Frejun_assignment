from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Passenger, Ticket, Berth, RACSlot, WaitingList
from .serializers import PassengerSerializer, TicketSerializer

class BookTicketAPIView(APIView):
    @transaction.atomic
    def post(self, request):
        data = request.data
        serializer = PassengerSerializer(data=data)
        if serializer.is_valid():
            passenger = serializer.save()
            ticket = Ticket.objects.create(passenger=passenger, status='WAITING')

            available_berths = Berth.objects.filter(is_available=True).order_by('berth_type')

            is_senior = passenger.age >= 60
            is_lady_with_child = passenger.gender == 'F' and passenger.has_child

            if passenger.is_child:
                ticket.status = 'CONFIRMED'
                ticket.berth_type = None
                ticket.berth_number = None
                ticket.save()
                return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

            if available_berths.exists():
                if is_senior or is_lady_with_child:
                    lower = available_berths.filter(berth_type='LOWER').first()
                    if lower:
                        berth = lower
                    else:
                        berth = available_berths.first()
                else:
                    berth = available_berths.first()

                ticket.status = 'CONFIRMED'
                ticket.berth_type = berth.berth_type
                ticket.berth_number = berth.berth_number
                berth.is_available = False
                berth.save()
                ticket.save()
                return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

            for slot in RACSlot.objects.all():
                if not slot.passenger_1:
                    slot.passenger_1 = ticket
                    slot.save()
                    ticket.status = 'RAC'
                    ticket.berth_type = 'SIDE_LOWER'
                    ticket.save()
                    return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)
                elif not slot.passenger_2:
                    slot.passenger_2 = ticket
                    slot.save()
                    ticket.status = 'RAC'
                    ticket.berth_type = 'SIDE_LOWER'
                    ticket.save()
                    return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

            if WaitingList.objects.count() < 10:
                position = WaitingList.objects.count() + 1
                WaitingList.objects.create(ticket=ticket, position=position)
                ticket.status = 'WAITING'
                ticket.save()
                return Response(TicketSerializer(ticket).data, status=status.HTTP_201_CREATED)

            return Response({"detail": "No tickets available."}, status=status.HTTP_400_BAD_REQUEST)


class CancelTicketAPIView(APIView):
    @transaction.atomic
    def post(self, request, ticket_id):
        try:
            ticket = Ticket.objects.select_for_update().get(id=ticket_id)
        except Ticket.DoesNotExist:
            return Response({"detail": "Ticket not found"}, status=status.HTTP_404_NOT_FOUND)

        if ticket.status == 'CONFIRMED':
            Berth.objects.filter(berth_number=ticket.berth_number).update(is_available=True)
            ticket.status = 'CANCELLED'
            ticket.save()

            for slot in RACSlot.objects.all():
                rac_ticket = slot.passenger_1 or slot.passenger_2
                if rac_ticket:
                    berth = Berth.objects.filter(is_available=True).first()
                    if berth:
                        rac_ticket.status = 'CONFIRMED'
                        rac_ticket.berth_type = berth.berth_type
                        rac_ticket.berth_number = berth.berth_number
                        berth.is_available = False
                        berth.save()
                        rac_ticket.save()

                        if slot.passenger_1:
                            slot.passenger_1 = None
                        else:
                            slot.passenger_2 = None
                        slot.save()

                        next_waiting = WaitingList.objects.order_by('position').first()
                        if next_waiting:
                            ticket_to_rac = next_waiting.ticket
                            if not slot.passenger_1:
                                slot.passenger_1 = ticket_to_rac
                            else:
                                slot.passenger_2 = ticket_to_rac
                            slot.save()
                            ticket_to_rac.status = 'RAC'
                            ticket_to_rac.berth_type = 'SIDE_LOWER'
                            ticket_to_rac.save()
                            next_waiting.delete()

                        break

        else:
            ticket.status = 'CANCELLED'
            ticket.save()

        return Response({"detail": "Ticket cancelled successfully"}, status=status.HTTP_200_OK)


class BookedTicketsAPIView(APIView):
    def get(self, request):
        tickets = Ticket.objects.exclude(status='CANCELLED').select_related('passenger')
        return Response(TicketSerializer(tickets, many=True).data)


class AvailableTicketsAPIView(APIView):
    def get(self, request):
        total_berths = 63
        confirmed = Ticket.objects.filter(status='CONFIRMED').count()
        rac = Ticket.objects.filter(status='RAC').count()
        waiting = WaitingList.objects.count()

        return Response({
            "confirmed_left": total_berths - confirmed,
            "rac_left": 18 - rac,
            "waiting_left": 10 - waiting,
            "available_berths": list(Berth.objects.filter(is_available=True).values())
        })
