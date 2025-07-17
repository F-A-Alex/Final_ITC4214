from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(
        max_length=17, 
        blank=True, 
        help_text="Format: +1234567890 or 1234567890"
    )
    address = models.TextField(
        blank=True,
        max_length=500,
        help_text="Maximum 500 characters"
    )
    city = models.CharField(
        max_length=100, 
        blank=True,
        help_text="City name"
    )
    postal_code = models.CharField(
        max_length=10, 
        blank=True, 
        help_text="Format: 12345 or A1B 2C3"
    )
    country = models.CharField(
        max_length=100, 
        blank=True,
        help_text="Country name"
    )
    date_of_birth = models.DateField(
        null=True, 
        blank=True,
        help_text="Your date of birth"
    )
    
    def __str__(self):
        return f"{self.user.username}'s Profile"  

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()