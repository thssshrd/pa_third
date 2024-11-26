import uuid
from django.db import models
from django.contrib.auth.models import User
from .utils import load_priorities

class Note(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    PRIORITY_CHOICES = load_priorities()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, blank=True, default='')
    text = models.TextField(max_length=10000, blank=True)
    priority = models.PositiveSmallIntegerField(choices=PRIORITY_CHOICES, default=1)
    due_date = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else self.text[:50]