from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.utils import timezone
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np

class User(AbstractUser):
    phone = models.CharField(max_length=15, blank=True)
    is_verified = models.BooleanField(default=False)

class VerificationQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.question_text

class ItemBase(models.Model):
    STATUS_CHOICES = [
        ('REPORTED', 'Reported'),
        ('VERIFYING', 'Verifying'),
        ('CLAIMED', 'Claimed'),
        ('DONATED', 'Donated'),
    ]
    brand = models.CharField(max_length=100, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    unique_identifiers = models.TextField(blank=True, null=True)
    description = models.TextField(validators=[MinLengthValidator(10)])
    location = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    date_submitted = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='REPORTED')

    class Meta:
        abstract = True

class FoundItem(ItemBase):
    STATUS_CHOICES = [
        ('FOUND_WAITING', 'Found, Waiting for Owner'),
        ('IN_CUSTODY', 'In Custody'),
        ('DONATED', 'Donated'),
        ('CLAIMED', 'Claimed'),
    ]
    
    photo = models.ImageField(upload_to='found_items/')
    submitter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Submitter (optional)"
    )
    submitter_name = models.CharField(max_length=100, blank=True)
    submitter_contact = models.CharField(max_length=100, blank=True)
    submitter_email = models.EmailField(blank=True)
    found_date = models.DateField()
    found_time = models.TimeField(null=True, blank=True)
    storage_location = models.CharField(max_length=255, blank=True, null=True)
    custody_date = models.DateTimeField(null=True, blank=True)
    donation_date = models.DateTimeField(null=True, blank=True)
    scheduled_donation_date = models.DateField(null=True, blank=True)
    claimed_by = models.ForeignKey(User, related_name='claimed_items', null=True, blank=True, on_delete=models.SET_NULL)
    ai_category = models.CharField(max_length=100, blank=True, null=True)
    ai_confidence = models.FloatField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='FOUND_WAITING')

    def save(self, *args, **kwargs):
        if not self.scheduled_donation_date:
            self.scheduled_donation_date = self.found_date + timezone.timedelta(days=30)
        
        if self.status == 'IN_CUSTODY' and not self.custody_date:
            self.custody_date = timezone.now()
        elif self.status == 'DONATED' and not self.donation_date:
            self.donation_date = timezone.now()
            
        super().save(*args, **kwargs)

    def analyze_image(self):
        """Use AI to categorize the item image"""
        try:
            model = MobileNetV2(weights='imagenet')
            img_path = self.photo.path
            img = image.load_img(img_path, target_size=(224, 224))
            x = image.img_to_array(img)
            x = np.expand_dims(x, axis=0)
            x = preprocess_input(x)

            preds = model.predict(x)
            results = decode_predictions(preds, top=1)[0]
            
            self.ai_category = results[0][1]
            self.ai_confidence = float(results[0][2])
            self.save()
            
            return results[0][1], float(results[0][2])
        except Exception as e:
            print(f"AI analysis failed: {str(e)}")
            return None, None

class LostItem(ItemBase):
    photo = models.ImageField(upload_to='lost_items/', blank=True, null=True)
    lost_date = models.DateField()
    contact_reward = models.CharField(max_length=255, blank=True, null=True)

class Message(models.Model):
    found_item = models.ForeignKey(FoundItem, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']
