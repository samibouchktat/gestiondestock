from django.conf import settings
from django.db import models
from django.utils import timezone

class EmailOTP(models.Model):
    user        = models.ForeignKey(settings.AUTH_USER_MODEL,
                                    on_delete=models.CASCADE)
    code        = models.CharField("Code OTP", max_length=6)
    created_at  = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField()

    def is_expired(self):
        return timezone.now() > self.valid_until

    def __str__(self):
        return f"OTP {self.code} for {self.user.username}"
