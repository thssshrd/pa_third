from django.urls import path
from . import views

urlpatterns = [
    path("boards/", views.board_list, name="board_list"),
    path("<uuid:board_id>/", views.kanban_board, name="kanban_board"),
    path("update_note_position/", views.update_note_position, name="update_note_position"),
    path("create_board/", views.create_board, name="create_board"),
    path("delete_column/<uuid:column_id>/", views.delete_column, name="delete_column"),
    path("add_column/<uuid:board_id>/", views.add_column, name="add_column"),
    path("add_note/<uuid:column_id>/", views.add_note, name="add_note"),
]