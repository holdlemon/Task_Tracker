from django.utils import timezone
from rest_framework import serializers
from .models import Employee, Task


class EmployeeSerializer(serializers.ModelSerializer):
    ''' Сериализитор для модели сотрудника '''

    active_tasks_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'full_name', 'position', 'active_tasks_count']


class TaskSerializer(serializers.ModelSerializer):
    ''' Сериализатор для модели задачи с валидацией данных '''

    class Meta:
        model = Task
        fields = '__all__'

    def validate_deadline(self, value):

        if value < timezone.now().date():
            raise serializers.ValidationError("Дедлайн не может иметь срок выполнения в прошлом.")
        return value
