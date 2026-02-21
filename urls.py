from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Dashboard & Lists
    path('', views.dashboard, name='dashboard'),
    path('members/', views.member_list, name='member_list'),
    path('members/<str:member_id>/', views.member_detail, name='member_detail'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('reports/', views.reports, name='reports'),
    
    # Recipient Management (এররটি এই সেকশনটির জন্য আসছে)
    path('recipients/', views.recipient_list, name='recipient_list'),
    path('recipient/add/', views.recipient_add, name='recipient_add'),
    # নিচের লাইনটি আপনার এরর সমাধান করবে
    path('recipient/<int:pk>/', views.recipient_detail, name='recipient_detail'),
    
    # Add/Create Forms
    path('member/add/', views.member_add, name='member_add'),
    path('deposit/add/', views.deposit_add, name='deposit_add'),
    path('project/add/', views.project_add, name='project_add'),
    path('investment/add/', views.investment_add, name='investment_add'),
    path('payment/add/', views.payment_add, name='payment_add'),
    path('profit/add/', views.profit_add, name='profit_add'),
    
    # Edit & Delete
    path('member/<str:member_id>/edit/', views.member_edit, name='member_edit'),
    path('member/<str:member_id>/delete/', views.member_delete, name='member_delete'),
    path('project/<int:project_id>/edit/', views.project_edit, name='project_edit'),
    path('project/<int:project_id>/delete/', views.project_delete, name='project_delete'),
    
    # Transactions Delete
    path('deposit/<int:deposit_id>/delete/', views.deposit_delete, name='deposit_delete'),
    path('payment/<int:payment_id>/delete/', views.payment_delete, name='payment_delete'),
    path('investment/<int:investment_id>/delete/', views.investment_delete, name='investment_delete'),
    path('profit/<int:profit_id>/delete/', views.profit_delete, name='profit_delete'),
    
    # Receipts
    path('deposit/<int:deposit_id>/receipt/', views.deposit_receipt, name='deposit_receipt'),
    path('payment/<int:payment_id>/receipt/', views.payment_receipt, name='payment_receipt'),
]