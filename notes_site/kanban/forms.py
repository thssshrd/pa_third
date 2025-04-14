from django import forms
from kanban.models import Board, Column

class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["name"]

class ColumnForm(forms.ModelForm):
    class Meta:
        model = Column
        fields = ["name"]