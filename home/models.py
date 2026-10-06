from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Workspace(models.Model):

   owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='workspaces')

   name = models.CharField(max_length=100)
   description = models.TextField(blank=True, null=True)

   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
      return self.name

class Board(models.Model):
    VISIBILITY_CHOICES = [
        ('private', 'Private'),
        ('workspace', 'Workspace Visible'),
        ('public', 'Public'),
    ]

    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='boards')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='workspace')
    background = models.CharField(max_length=50, default='gradient-ocean')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class BoardList(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name='lists')
    name = models.CharField(max_length=100)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.name

class Task(models.Model):
    board_list = models.ForeignKey(BoardList, on_delete=models.CASCADE, related_name='tasks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    position = models.PositiveIntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    label_color = models.CharField(max_length=30, blank=True, null=True, default='blue')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['position', 'id']

    def __str__(self):
        return self.title