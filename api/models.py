from django.db import models

# Create your models here.
class Passenger(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )

    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    has_child = models.BooleanField(default=False)
    is_child = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.age})"

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('CONFIRMED', 'Confirmed'),
        ('RAC', 'RAC'),
        ('WAITING', 'Waiting List'),
        ('CANCELLED', 'Cancelled'),
    )

    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    berth_type = models.CharField(
        max_length=15,
        null=True,
        blank=True,
        choices=(
            ('LOWER', 'Lower'),
            ('MIDDLE', 'Middle'),
            ('UPPER', 'Upper'),
            ('SIDE_LOWER', 'Side Lower'),
        )
    )
    berth_number = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ticket #{self.id} - {self.passenger.name} [{self.status}]"

class RACSlot(models.Model):
    slot_number = models.PositiveIntegerField(unique=True)
    passenger_1 = models.OneToOneField(
        Ticket, null=True, blank=True, on_delete=models.SET_NULL, related_name='rac_passenger_1'
    )
    passenger_2 = models.OneToOneField(
        Ticket, null=True, blank=True, on_delete=models.SET_NULL, related_name='rac_passenger_2'
    )

    def __str__(self):
        return f"RAC Slot #{self.slot_number}"

class WaitingList(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    position = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return f"Waiting List Position #{self.position} - {self.ticket.passenger.name}"

class Berth(models.Model):
    berth_number = models.PositiveIntegerField(unique=True)
    berth_type = models.CharField(
        max_length=15,
        choices=(
            ('LOWER', 'Lower'),
            ('MIDDLE', 'Middle'),
            ('UPPER', 'Upper'),
            ('SIDE_LOWER', 'Side Lower'),
        )
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.berth_type} - #{self.berth_number} ({'Free' if self.is_available else 'Booked'})"
