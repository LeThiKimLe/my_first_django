from django.urls import path
from students import views

urlpatterns=[
    path('students/', views.getview, name='getliststudent'),
]