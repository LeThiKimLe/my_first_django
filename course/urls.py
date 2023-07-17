from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from course import views

urlpatterns = [
    path('course/', views.SubjectList.as_view()),
    path('course/<int:pk>/', views.SubjectDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)