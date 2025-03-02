from rest_framework import viewsets, status, views
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class BusyEmployeesView(views.APIView):
    def get(self, request):
        employees = Employee.objects.annotate(
            active_tasks_count=Count('tasks', filter=Q(tasks__status='in_progress'))
        ).order_by('-active_tasks_count')
        serializer = EmployeeSerializer(employees, many=True, context={'request': request})
        return Response([{
            **emp,
            'active_tasks': emp['active_tasks_count'],
            'tasks': TaskSerializer(Task.objects.filter(assignee=emp['id'], status='in_progress'), many=True).data
        } for emp in serializer.data])


class ImportantTasksView(views.APIView):
    def get(self, request):
        # Фильтруем задачи:
        # 1. Статус задачи — "не запущена".
        # 2. Либо дочерняя задача в работе, либо родительская задача в работе.
        important_tasks = Task.objects.filter(
            status='not_started'
        ).filter(
            Q(children__status='in_progress') | Q(parent_task__status='in_progress')
        ).distinct()

        employees = list(Employee.objects.annotate(
            active_tasks_count=Count('tasks', filter=Q(tasks__status='in_progress'))
        ))
        if not employees:
            return Response([])

        min_load = min(emp.active_tasks_count for emp in employees)
        employees_dict = {emp.id: emp for emp in employees}

        result = []
        for task in important_tasks:
            candidates = []
            least_loaded = [emp for emp in employees if emp.active_tasks_count == min_load]
            candidates.extend(least_loaded)

            if task.parent_task and task.parent_task.assignee:
                parent_assignee = employees_dict.get(task.parent_task.assignee.id)
                if parent_assignee and parent_assignee.active_tasks_count <= min_load + 2:
                    candidates.append(parent_assignee)

            unique_candidates = list({emp.id: emp for emp in candidates}.values())
            result.append({
                'task': task.name,
                'deadline': task.deadline,
                'employees': [emp.full_name for emp in unique_candidates]
            })

        return Response(result)
