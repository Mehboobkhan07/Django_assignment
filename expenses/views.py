from django.shortcuts import render

from rest_framework import generics, permissions
from .models import Expense
from .serializers import ExpenseSerializer
from datetime import datetime
from django.db.models import Sum ,Avg
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse  
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth

def home(request):
    return JsonResponse({"message": "Welcome to the Expense Tracker API"})

class ExpenseListCreateView(generics.ListCreateAPIView):
    serializer_class = ExpenseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        queryset = Expense.objects.filter(user=user)

        if start_date and end_date:
            queryset = queryset.filter(date__range=[start_date, end_date])

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ExpenseAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')

        expenses = Expense.objects.filter(user=user)
        if start_date and end_date:
            expenses = expenses.filter(date__range=[start_date, end_date])

        # Total Expenses
        total_expenses = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

        # Category-wise Breakdown
        category_wise = expenses.values('category').annotate(total=Sum('amount'))

        # Daily Trends
        daily_trend = expenses.annotate(day=TruncDay('date')) \
                              .values('day') \
                              .annotate(total=Sum('amount'), avg=Avg('amount')) \
                              .order_by('day')
                              

        # Weekly Trends
        weekly_trend = expenses.annotate(week=TruncWeek('date')) \
                               .values('week') \
                               .annotate(total=Sum('amount'), avg=Avg('amount')) \
                               .order_by('week')

        # Monthly Trends
        monthly_trend = expenses.annotate(month=TruncMonth('date')) \
                                .values('month') \
                                .annotate(total=Sum('amount'), avg=Avg('amount')) \
                                .order_by('month')

        data = {
            "total_expenses": total_expenses,
            "category_wise": list(category_wise),
            "daily_trend": list(daily_trend),
            "weekly_trend": list(weekly_trend),
            "monthly_trend": list(monthly_trend),
        }
        return Response(data)
