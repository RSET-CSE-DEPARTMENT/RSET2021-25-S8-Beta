from django.db import models

class UserProfile(models.Model):
    user_id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=100)
    contact_email = models.EmailField(unique=True)
    user_password = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)

    class Meta:
        db_table = 'user_profiles'

