from django.urls import path
from home import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Workspace routes
    path('workspace/create/', views.create_workspace, name='create_workspace'),
    path('workspace/<int:workspace_id>/', views.workspace_detail, name='workspace_detail'),
    
    # Board routes
    path('board/<int:board_id>/', views.board_detail, name='board_detail'),
    path('board/<int:board_id>/update/', views.update_board, name='update_board'),
    path('board/<int:board_id>/delete/', views.delete_board, name='delete_board'),
    
    # List routes
    path('board/<int:board_id>/create_list/', views.create_list, name='create_list'),
    path('list/<int:list_id>/update/', views.update_list, name='update_list'),
    path('list/<int:list_id>/delete/', views.delete_list, name='delete_list'),
    
    # Task routes
    path('list/<int:list_id>/create_task/', views.create_task, name='create_task'),
    path('task/<int:task_id>/update/', views.update_task, name='update_task'),
    path('task/<int:task_id>/delete/', views.delete_task, name='delete_task'),
]