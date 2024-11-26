from django.urls import path
from . import views

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('add/', views.add_note, name='add_note'),
    path('<uuid:note_id>/', views.edit_note, name='edit_note'),
    path('delete/<uuid:note_id>/', views.delete_note, name='delete_note'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]