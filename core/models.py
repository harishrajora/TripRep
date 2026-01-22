from django.db import models

# Add your models here when needed.

class Tickets(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=False)
    title = models.CharField(max_length=200, null=False, blank=False)
    ticket_file = models.FileField(upload_to='tickets/')
    source = models.CharField(max_length=100, null=False, blank=False)
    destination = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    date_of_journey = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ticket_type = models.CharField(max_length=100, null=False, blank=False)
    booked_through = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return self.title
