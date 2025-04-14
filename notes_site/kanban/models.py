import uuid
from django.db import models
from django.contrib.auth.models import User
import datetime as dt

class Board(models.Model):
    """Represents a Kanban board, allowing multiple users to collaborate."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    date_created = models.DateField(default = dt.date.today)
    users = models.ManyToManyField(User, related_name="boards")

    def __str__(self):
        return self.name

class Column(models.Model):
    """Represents a column on the Kanban board (e.g., To Do, In Progress, Done)."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    board = models.ForeignKey(Board, related_name="columns", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["position"]

    def __str__(self):
        return self.name

def default_column():
    """Ensures a default Board and Column exist, returning the column ID."""
    board, _ = Board.objects.get_or_create(name="Default Board")
    column, _ = Column.objects.get_or_create(name="Default Column", board=board)
    return column.id
