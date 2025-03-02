from django.test import TestCase
from rest_framework.test import APITestCase
from .models import Employee, Task
from .serializers import EmployeeSerializer, TaskSerializer


class EmployeeModelTest(TestCase):
    def test_create_employee(self):
        employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )
        self.assertEqual(employee.full_name, "Иван Иванов")
        self.assertEqual(employee.position, "Менеджер")
        self.assertIsNotNone(employee.created_at)


class TaskModelTest(TestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )

    def test_create_task(self):
        task = Task.objects.create(
            name="Сортировка файлов",
            assignee=self.employee,
            deadline="2025-03-04",
            status="in_progress"
        )
        self.assertEqual(task.name, "Сортировка файлов")
        self.assertEqual(task.assignee, self.employee)
        self.assertEqual(task.status, "in_progress")
        self.assertIsNotNone(task.created_at)

    def test_task_with_parent(self):
        parent_task = Task.objects.create(
            name="Родительская задача",
            assignee=self.employee,
            deadline="2025-03-04",
            status="in_progress"
        )
        child_task = Task.objects.create(
            name="Дочерняя задача",
            parent_task=parent_task,
            assignee=self.employee,
            deadline="2025-03-05",
            status="not_started"
        )
        self.assertEqual(child_task.parent_task, parent_task)
        self.assertIn(child_task, parent_task.children.all())


class EmployeeSerializerTest(APITestCase):
    def test_employee_serializer(self):
        employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )
        serializer = EmployeeSerializer(employee)
        self.assertEqual(serializer.data['full_name'], "Иван Иванов")
        self.assertEqual(serializer.data['position'], "Менеджер")


class TaskSerializerTest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )

    def test_task_serializer(self):
        task = Task.objects.create(
            name="Сортировка файлов",
            assignee=self.employee,
            deadline="2025-03-04",
            status="in_progress"
        )
        serializer = TaskSerializer(task)
        self.assertEqual(serializer.data['name'], "Сортировка файлов")
        self.assertEqual(serializer.data['assignee'], self.employee.id)
        self.assertEqual(serializer.data['status'], "in_progress")

    def test_task_serializer_deadline_validation(self):
        data = {
            "name": "Просроченная задача",
            "assignee": self.employee.id,
            "deadline": "2020-01-01",
            "status": "not_started"
        }
        serializer = TaskSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("deadline", serializer.errors)


class EmployeeViewSetTest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )

    def test_list_employees(self):
        response = self.client.get('/api/employees/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['full_name'], "Иван Иванов")

    def test_create_employee(self):
        data = {
            "full_name": "Сергей Сергеев",
            "position": "Рабочий"
        }
        response = self.client.post('/api/employees/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Employee.objects.count(), 2)


class TaskViewSetTest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )
        self.task = Task.objects.create(
            name="Сортировка файлов",
            assignee=self.employee,
            deadline="2025-03-04",
            status="in_progress"
        )

    def test_list_tasks(self):
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], "Сортировка файлов")

    def test_create_task(self):
        data = {
            "name": "Новая задача",
            "assignee": self.employee.id,
            "deadline": "2025-03-05",
            "status": "not_started"
        }
        response = self.client.post('/api/tasks/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Task.objects.count(), 2)


class BusyEmployeesViewTest(APITestCase):
    def setUp(self):
        self.employee1 = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )
        self.employee2 = Employee.objects.create(
            full_name="Сергей Сергеев",
            position="Рабочий"
        )
        Task.objects.create(
            name="Сортировка файлов",
            assignee=self.employee1,
            deadline="2025-03-04",
            status="in_progress"
        )
        Task.objects.create(
            name="Верстка сайта",
            assignee=self.employee1,
            deadline="2025-03-05",
            status="in_progress"
        )
        Task.objects.create(
            name="Разбор важных задач",
            assignee=self.employee2,
            deadline="2025-03-06",
            status="in_progress"
        )

    def test_busy_employees(self):
        response = self.client.get('/api/busy-employees/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['full_name'], "Иван Иванов")
        self.assertEqual(response.data[0]['active_tasks'], 2)


class ImportantTasksViewTest(APITestCase):
    def setUp(self):
        self.employee = Employee.objects.create(
            full_name="Иван Иванов",
            position="Менеджер"
        )
        self.parent_task = Task.objects.create(
            name="Родительская задача",
            assignee=self.employee,
            deadline="2025-03-04",
            status="in_progress"
        )
        self.child_task = Task.objects.create(
            name="Дочерняя задача",
            parent_task=self.parent_task,
            assignee=self.employee,
            deadline="2025-03-05",
            status="not_started"
        )

    def test_important_tasks(self):
        response = self.client.get('/api/important-tasks/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['task'], "Дочерняя задача")
