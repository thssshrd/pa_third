from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.db import transaction
from django.http import JsonResponse
import json
from notes.models import Note
from kanban.models import Board, Column
from kanban.forms import BoardForm, ColumnForm


@login_required
def kanban_board(request, board_id):
    """Displays the Kanban board with its columns."""
    board = get_object_or_404(Board, id=board_id, users=request.user)
    columns = board.columns.all()
    return render(request, "kanban/kanban_board.html", {"board": board, "columns": columns})


@login_required
def board_list(request):
    """Displays all Kanban boards the user has access to."""
    boards = Board.objects.filter(users=request.user)
    return render(request, "kanban/board_list.html", {"boards": boards})


@login_required
def create_board(request):
    """Allows users to create a new Kanban board."""
    if request.method == "POST":
        form = BoardForm(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.save()
            board.users.add(request.user)  # Assign the board to the logged-in user
            return redirect("kanban_board", board_id=board.id)
    else:
        form = BoardForm()
    
    return render(request, "kanban/create_board.html", {"form": form})


@login_required
def add_column(request, board_id):
    """Allows users to add a column directly from the Kanban board page."""
    board = get_object_or_404(Board, id=board_id, users=request.user)

    if request.method == "POST":
        form = ColumnForm(request.POST)
        if form.is_valid():
            column = form.save(commit=False)
            column.board = board
            column.position = board.columns.count()
            column.save()
            return redirect("kanban_board", board_id=board.id)

    return redirect("kanban_board", board_id=board.id)

@login_required
def delete_column(request, column_id):
    """Deletes a column from a board."""
    column = get_object_or_404(Column, id=column_id, board__users=request.user)
    board_id = column.board.id
    column.delete()
    return redirect("kanban_board", board_id=board_id)


@login_required
def add_note(request, column_id):
    """Allows users to add a new note (task) inside a specific column."""
    if request.method == "POST":
        column = get_object_or_404(Column, id=column_id, board__users=request.user)
        title = request.POST.get("title", "").strip()

        if not title:
            return JsonResponse({"status": "error", "message": "Title cannot be empty"}, status=400)

        with transaction.atomic():
            note = Note.objects.create(
                title=title,
                column=column,
                user=request.user,
                position=column.notes.count()
            )

        return JsonResponse({
            "status": "success",
            "note_id": note.id,
            "title": note.title,
            "column_id": column.id
        }, status=201)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)


@login_required
@csrf_exempt
def update_note_position(request):
    """Updates the note position after a drag-and-drop action."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            note = Note.objects.get(id=data["note_id"])
            column = Column.objects.get(id=data["column_id"])

            # Shift other cards down if moving within the same column
            if note.column == column:
                old_position = note.position
                new_position = data["position"]

                if old_position < new_position:
                    Note.objects.filter(column=column, position__gt=old_position, position__lte=new_position).update(position=F("position") - 1)
                else:
                    Note.objects.filter(column=column, position__lt=old_position, position__gte=new_position).update(position=F("position") + 1)

            # If moving to a new column, adjust positions in both columns
            else:
                Note.objects.filter(column=note.column, position__gt=note.position).update(position=F("position") - 1)
                note.column = column
                note.position = data["position"]

            note.save()
            return JsonResponse({"status": "success"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "error", "message": "Invalid request"}, status=400)