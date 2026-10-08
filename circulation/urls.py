from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_catalog, name='book_catalog'),
    path('books/', views.book_catalog, name='book_catalog_list'),
    path('books/new/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    
    path('issue/', views.issue_book, name='issue_book'),
    path('issue/<int:book_id>/', views.issue_book, name='issue_book_for_item'),
    
    path('return/<int:record_id>/', views.return_book, name='return_book'),
    path('circulation/', views.circulation_list, name='circulation_list'),
    
    path('members/', views.member_list, name='member_list'),
    path('members/new/', views.member_create, name='member_create'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    
    path('authors/', views.author_list, name='author_list'),
    path('authors/new/', views.author_create, name='author_create'),
    
    path('calculator/', views.due_date_calculator, name='due_date_calculator'),
    path('api/calculate-fine/', views.api_calculate_fine, name='api_calculate_fine'),
]
