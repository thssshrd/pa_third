import uuid
from django.db import models
from django.contrib.auth.models import User
from .utils import load_priorities
from kanban.models import Column, default_column

# def default_column():
#     """Returns a default column ID for new and existing notes."""
#     board, _ = Board.objects.get_or_create(name="Default Board")
#     column, _ = Column.objects.get_or_create(name="Default Column", board=Board.objects.first())
#     return column.id

class Note(models.Model):
    """Represents a task (Kanban card) in a column on the board."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120, blank=True, default="")
    text = models.TextField(max_length=10000, blank=True)
    priority = models.PositiveSmallIntegerField(choices=load_priorities(), default=1)
    due_date = models.DateField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True)

    column = models.ForeignKey(Column, related_name="notes", on_delete=models.CASCADE, default=default_column)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.title if self.title else self.text[:50]