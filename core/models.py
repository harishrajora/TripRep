from django.db import models
import fitz  # PyMuPDF
from PIL import Image
import io
from django.core.files.base import ContentFile


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
    image_thumbnail = models.ImageField(upload_to='thumbnails/', null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.00)

    def generate_thumbnail(self):
        if not self.ticket_file:
            return
        try:
            # Open PDF
            pdf_document = fitz.open(self.ticket_file.path)
            # Get first page
            first_page = pdf_document[0]
            mat = fitz.Matrix(2, 2)  # 2x zoom for better quality
            pix = first_page.get_pixmap(matrix=mat)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            img.thumbnail((1024, 1024))
            
            # Save to BytesIO
            thumb_io = io.BytesIO()
            img.save(thumb_io, format='PNG')
            thumb_io.seek(0)
            
            # Save to model
            filename = f"{self.ticket_file.name.split('/')[-1].split('.')[0]}_thumb.png"
            self.image_thumbnail.save(
                filename,
                ContentFile(thumb_io.read()),
                save=False  # Don't trigger another save
            )
            
            pdf_document.close()
            
            # Now save the model with the thumbnail
            super(Tickets, self).save(update_fields=['image_thumbnail'])
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        print(f"Args = {args}, Kwargs = {kwargs}")
        if is_new:
            # Save first to get the file path
            super().save(*args, **kwargs)
            # Then generate thumbnail
            if self.ticket_file:
                self.generate_thumbnail()

    def __str__(self):
        return self.title


class Reservations(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=False)
    reservation_name = models.CharField(max_length=200, null=False, blank=False)
    reservation_file = models.FileField(upload_to='reservations/')
    description = models.TextField()
    date_of_reservation = models.DateField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    reservation_type = models.CharField(max_length=100, null=False, blank=False)
    booked_through = models.CharField(max_length=100, null=False, blank=False)
    image_thumbnail = models.ImageField(upload_to='reservation_thumbnails/', null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False, default=0.00)

    def __str__(self):
        return self.reservation_id