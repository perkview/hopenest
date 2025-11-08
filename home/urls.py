from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('about/', views.about, name="about"),
    path('projects/', views.projects, name="projects"),
    path('impacts/', views.impacts, name="impacts"),
    path('feedback/', views.feedback, name="feedback"),
    path('contact/', views.contact, name="contact"),
    path('donate/', views.donate, name="donate"),
    path('policy/', views.policy, name="policy"),
    path('terms/', views.terms, name="terms"),
]
