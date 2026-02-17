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
        return self.reservation_name
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        print(f"Args = {args}, Kwargs = {kwargs}")
        if is_new:
            # Save first to get the file path
            super().save(*args, **kwargs)
            # Then generate thumbnail
            if self.reservation_file:
                self.generate_thumbnail()

    def generate_thumbnail(self):
        if not self.reservation_file:
            return
        try:
            # Open PDF
            pdf_document = fitz.open(self.reservation_file.path)
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
            filename = f"{self.reservation_file.name.split('/')[-1].split('.')[0]}_thumb.png"
            self.image_thumbnail.save(
                filename,
                ContentFile(thumb_io.read()),
                save=False  # Don't trigger another save
            )
            
            pdf_document.close()
            
            # Now save the model with the thumbnail
            super(Reservations, self).save(update_fields=['image_thumbnail'])
            
        except Exception as e:
            print(f"Error generating thumbnail: {e}")


class UserProfile(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'USD - United States Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - Pound Sterling'),
        ('INR', 'INR - Indian Rupee'),
        ('AUD', 'AUD - Australian Dollar'),
        ('CAD', 'CAD - Canadian Dollar'),
        ('JPY', 'JPY - Japanese Yen'),
        ('CNY', 'CNY - Chinese Yuan'),
        ('SGD', 'SGD - Singapore Dollar'),
        ('CHF', 'CHF - Swiss Franc'),
        ('NZD', 'NZD - New Zealand Dollar'),
        ('ZAR', 'ZAR - South African Rand'),
        ('SEK', 'SEK - Swedish Krona'),
        ('NOK', 'NOK - Norwegian Krone'),
        ('DKK', 'DKK - Danish Krone'),
        ('BRL', 'BRL - Brazilian Real'),
        ('MXN', 'MXN - Mexican Peso'),
        ('RUB', 'RUB - Russian Ruble'),
        ('HKD', 'HKD - Hong Kong Dollar'),
        ('KRW', 'KRW - South Korean Won'),
        ('AED', 'AED - United Arab Emirates Dirham'),
        ('ARS', 'ARS - Argentine Peso'),
        ('BDT', 'BDT - Bangladeshi Taka'),
        ('BGN', 'BGN - Bulgarian Lev'),
        ('BHD', 'BHD - Bahraini Dinar'),
        ('BND', 'BND - Brunei Dollar'),
        ('BOB', 'BOB - Bolivian Boliviano'),
        ('BWP', 'BWP - Botswana Pula'),
        ('BYN', 'BYN - Belarusian Ruble'),
        ('CLP', 'CLP - Chilean Peso'),
        ('COP', 'COP - Colombian Peso'),
        ('CRC', 'CRC - Costa Rican Colón'),
        ('CZK', 'CZK - Czech Koruna'),
        ('DOP', 'DOP - Dominican Peso'),
        ('EGP', 'EGP - Egyptian Pound'),
        ('ETB', 'ETB - Ethiopian Birr'),
        ('GHS', 'GHS - Ghanaian Cedi'),
        ('GTQ', 'GTQ - Guatemalan Quetzal'),
        ('HUF', 'HUF - Hungarian Forint'),
        ('IDR', 'IDR - Indonesian Rupiah'),
        ('ILS', 'ILS - Israeli New Shekel'),
        ('IQD', 'IQD - Iraqi Dinar'),
        ('IRR', 'IRR - Iranian Rial'),
        ('JOD', 'JOD - Jordanian Dinar'),
        ('KES', 'KES - Kenyan Shilling'),
        ('KWD', 'KWD - Kuwaiti Dinar'),
        ('KZT', 'KZT - Kazakhstani Tenge'),
        ('LAK', 'LAK - Lao Kip'),
        ('LKR', 'LKR - Sri Lankan Rupee'),
        ('MAD', 'MAD - Moroccan Dirham'),
        ('MDL', 'MDL - Moldovan Leu'),
        ('MXV', 'MXV - Mexican Unidad de Inversion (UDI)'),
        ('MNT', 'MNT - Mongolian Tögrög'),
        ('MUR', 'MUR - Mauritian Rupee'),
        ('MVR', 'MVR - Maldivian Rufiyaa'),
        ('MWK', 'MWK - Malawian Kwacha'),
        ('MYR', 'MYR - Malaysian Ringgit'),
        ('NGN', 'NGN - Nigerian Naira'),
        ('NPR', 'NPR - Nepalese Rupee'),
        ('OMR', 'OMR - Omani Rial'),
        ('PAB', 'PAB - Panamanian Balboa'),
        ('PEN', 'PEN - Peruvian Sol'),
        ('PHP', 'PHP - Philippine Peso'),
        ('PKR', 'PKR - Pakistani Rupee'),
        ('PLN', 'PLN - Polish Złoty'),
        ('PYG', 'PYG - Paraguayan Guaraní'),
        ('QAR', 'QAR - Qatari Riyal'),
        ('RON', 'RON - Romanian Leu'),
        ('RSD', 'RSD - Serbian Dinar'),
        ('SHP', 'SHP - Saint Helena Pound'),
        ('SOS', 'SOS - Somali Shilling'),
        ('SRD', 'SRD - Surinamese Dollar'),
        ('SYP', 'SYP - Syrian Pound'),
        ('THB', 'THB - Thai Baht'),
        ('TND', 'TND - Tunisian Dinar'),
        ('TRY', 'TRY - Turkish Lira'),
        ('TTD', 'TTD - Trinidad and Tobago Dollar'),
        ('TWD', 'TWD - New Taiwan Dollar'),
        ('UAH', 'UAH - Ukrainian Hryvnia'),
        ('UGX', 'UGX - Ugandan Shilling'),
        ('UYU', 'UYU - Uruguayan Peso'),
        ('UZS', 'UZS - Uzbekistani Som'),
        ('VND', 'VND - Vietnamese Dong'),
        ('VUV', 'VUV - Vanuatu Vatu'),
        ('XAF', 'XAF - Central African CFA Franc'),
        ('XCD', 'XCD - East Caribbean Dollar'),
        ('XOF', 'XOF - West African CFA Franc'),
        ('XPF', 'XPF - CFP Franc'),
        ('YER', 'YER - Yemeni Rial'),
        ('ZMW', 'ZMW - Zambian Kwacha'),
        ('ZWL', 'ZWL - Zimbabwean Dollar'),
    ]
    
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='profile')
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default='INR')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"