from django.urls import path
from .views import home, ExpenseListCreateView, ExpenseAnalyticsView


urlpatterns = [
    path('', home),  
    
  path('expenses/', ExpenseListCreateView.as_view(), name='expense-list-create'),
  path('expenses/analytics/', ExpenseAnalyticsView.as_view(), name='expense-analytics')
]
