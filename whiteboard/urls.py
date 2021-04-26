from django.urls import path

from . import views

urlpatterns = [
    path('', views.homePage, name='Homepage'),
    path('demoPage/', views.demoPage, name='Demopage'),
    path('demoPage/steerpoint', views.demoSteer, name="fromDemoWhiteboard"),
    path('steerpoint', views.homeSteer, name="fromHomeWhiteboard"),
    path('steerpoint/whiteboard', views.whiteboard, name="whiteboard"),

]