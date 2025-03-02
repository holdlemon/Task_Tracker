from django.db import models
from django.utils import timezone


class Employee(models.Model):
    full_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    created_at = models.DateTimeField(default=timezone.now)


class Task(models.Model):
    STATUS_CHOICES = [
        ('not_started', 'Не начата'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
    ]
    name = models.CharField(max_length=255)
    parent_task = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    assignee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    deadline = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    created_at = models.DateTimeField(default=timezone.now)
