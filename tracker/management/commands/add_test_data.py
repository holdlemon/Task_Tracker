from django.core.management import call_command
from django.core.management.base import BaseCommand

from tracker.models import Employee, Task


class Command(BaseCommand):
    ''' Кастомная команда для загрузки тестовых данных '''
    help = "Добавление тестовых данных из фикстур"

    def handle(self, *args, **kwargs):
        # Удаляем существующие записи
        Employee.objects.all().delete()
        Task.objects.all().delete()

        # Загружаем данные из фикстур
        call_command("loaddata", "employee_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Сотрудники загружены из фикстур успешно"))

        call_command("loaddata", "task_fixture.json", format="json")
        self.stdout.write(self.style.SUCCESS("Задачи загружены из фикстур успешно"))
