from django.contrib import admin

# Register your models here if you add any later.
from .models import Tickets, Reservations, UserProfile, Trips
admin.site.register(Tickets)
admin.site.register(Reservations)
admin.site.register(UserProfile)
admin.site.register(Trips)