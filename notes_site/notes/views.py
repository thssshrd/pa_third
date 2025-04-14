from uuid import UUID
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.http import JsonResponse
from django.db import transaction
from django.db.models import F
import json
from .forms import NoteForm, SignUpForm, SigninForm
from notes.models import Note
from kanban.models import Board, Column


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('note_list')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('note_list')
    if request.method == 'POST':
        form = SigninForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('note_list')
    else:
        form = SigninForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def note_list(request):
    notes = Note.objects.filter(user=request.user).order_by('-date_created')
    return render(request, 'note_list.html', {'notes': notes})

@login_required
def add_note(request):
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.save()
            return redirect('note_list')
    else:
        form = NoteForm()
    return render(request, 'add_note.html', {'form': form})

@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        note.delete()
        return redirect('note_list')
    return render(request, 'delete_note.html', {'note': note})

@login_required
def edit_note(request, note_id):
    note = get_object_or_404(Note, id=note_id, user=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST, instance=note)
        if form.is_valid():
            form.save()
            return redirect('note_list')
    else:
        form = NoteForm(instance=note)
    return render(request, 'edit_note.html', {'form': form, 'note': note})

@login_required
def kanban_board(request, board_id):
    """Displays the Kanban board with its columns and notes."""
    board = get_object_or_404(Board, id=board_id, users=request.user)
    columns = board.columns.all()
    return render(request, "kanban_board.html", {"board": board, "columns": columns})

@login_required
def update_note_position(request):
    """Handles drag-and-drop reordering of notes within columns."""
    if request.method == "POST":
        data = json.loads(request.body)
        note_id = data.get("note_id")
        column_id = data.get("column_id")
        new_position = int(data.get("position"))

        try:
            note = Note.objects.get(id=note_id, user=request.user)
            old_column = note.column
            old_position = note.position
            new_column = Column.objects.get(id=column_id, board__users=request.user)

            with transaction.atomic():
                if old_column == new_column:
                    if new_position < old_position:
                        Note.objects.filter(
                            column=old_column,
                            position__gte=new_position,
                            position__lt=old_position
                        ).exclude(id=note.id).update(position=F("position") + 1)
                    elif new_position > old_position:
                        Note.objects.filter(
                            column=old_column,
                            position__gt=old_position,
                            position__lte=new_position
                        ).exclude(id=note.id).update(position=F("position") - 1)
                else:
                    Note.objects.filter(column=old_column, position__gt=old_position).update(position=F("position") - 1)
                    Note.objects.filter(column=new_column, position__gte=new_position).update(position=F("position") + 1)

                note.column = new_column
                note.position = new_position
                note.save()

            return JsonResponse({"status": "success"})

        except Note.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Note not found"}, status=404)
        except Column.DoesNotExist:
            return JsonResponse({"status": "error", "message": "Column not found"}, status=404)
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)