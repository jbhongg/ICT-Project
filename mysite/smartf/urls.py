from django.conf.urls import url, include
from . import views

from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

app_name = 'smartf'

urlpatterns = [
    path('', views.main, name='main'),
    path('search/',views.chart_search,name='chart_search'),
    path('predict/', views.predict,name='predict'),
    path('data/',views.chart_get,name='chart_get'),
    path('correlation/',views.Correlation,name='Correlation'),
    path('stability/',views.stability,name='stability'),

]
