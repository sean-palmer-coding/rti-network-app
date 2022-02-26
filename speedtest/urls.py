from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('api', views.chart_data, name='chart_api'),
    path('', views.PerformanceView.as_view(), name='index'),
    path('performance/', views.PerformanceView.as_view(), name='performance_list'),
    path('records/', views.FilterView, name='record_view'),
    path('admin/', admin.site.urls, name='admin_settings'),
    path('csvoutput/', views.CSV_output, name='csv')
]
