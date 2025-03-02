from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import TrackerConfig
from .views import EmployeeViewSet, TaskViewSet, BusyEmployeesView, ImportantTasksView


app_name = TrackerConfig.name

router = DefaultRouter()
router.register(r'employees', EmployeeViewSet)
router.register(r'tasks', TaskViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('busy-employees/', BusyEmployeesView.as_view()),
    path('important-tasks/', ImportantTasksView.as_view()),
]
