from django.urls import path, include
from snippets import views
from rest_framework.urlpatterns import format_suffix_patterns
from snippets.views import SnippetViewSet, UserViewSet, api_root
from rest_framework import renderers
from rest_framework.routers import DefaultRouter

"""
Tạo ra nhiều view từ một ViewSet
"""

snippet_list = SnippetViewSet.as_view(
{
    'get': 'list',
    'post': 'create'
})

snippet_detail = SnippetViewSet.as_view(
    {
    'get': 'retrieve',
    'put' : 'update',
    'patch': 'partial_update',
    'delete': 'destroy'
})

snippet_highlight = SnippetViewSet.as_view({
    'get': 'highlight'
}, renderer_classes = [renderers.StaticHTMLRenderer])

user_list = UserViewSet.as_view({
    'get':'list'
})

user_detail = UserViewSet.as_view({
    'get': 'retrieve'
})

"""
Khai báo url với từng view lẻ
"""
# urlpatterns = [
#     path('', api_root),
#     path('snippets/', views.SnippetList.as_view(), name='snippet-list'),
#     path('snippets/<int:pk>/', views.SnippetDetail.as_view(), name='snippet-detail'),
#     path('snippets/<int:pk>/highlight/',views.SnippetHighlight.as_view(), name='snippet-highlight'),
#     path('users/', views.UserList.as_view(), name='user-list'),
#     path('users/<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
#     ]

# urlpatterns = format_suffix_patterns(urlpatterns)

""" 
Khai báo url với các view được tạo từ ViewSet thì 
dùng luôn tên view ở trên, nhưng mà vẫn phải khai báo name
"""
# urlpatterns = [
#     path('', api_root),
#     path('snippets/', snippet_list , name='snippet-list'),
#     path('snippets/<int:pk>/', snippet_detail, name='snippet-detail'),
#     path('snippets/<int:pk>/highlight/',snippet_highlight, name='snippet-highlight'),
#     path('users/', user_list , name='user-list'),
#     path('users/<int:pk>/', user_detail , name='user-detail'),
#     ]

# urlpatterns = format_suffix_patterns(urlpatterns)

"""
Khi dùng ViewSet thì ngta thường dùng Router để định nghĩa url hơn
"""
router = DefaultRouter()
router.register(r'snippets', views.SnippetViewSet, basename='snippet')
router.register(r'users', views.UserViewSet, basename='user')

# API URLs tự động tạo bởi router :v
urlpatterns=[
    path('', include(router.urls)),
]
