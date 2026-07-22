#Archivo para gestionar las rutas internas dela aplicacion nomina
from django.urls import path
from django.shortcuts import redirect
#Importamos la lógica de negocio de la aplicación
from . import views
#Listadp de rutas de la Aplicación
urlpatterns = [
    path('', views.inicio),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('newcliente/', views.newcliente),
    path('guardar_cliente/', views.guardar_Cliente),
    path('showclientes/', views.showclientes),
    path('eliminarcliente/<int:id>/', views.eliminarcliente),
    path('detalle_encomienda/<int:id>/', views.detalle_encomienda),
    path('guardar_encomienda/', views.guardar_encomienda),
    path('newencomienda/', views.newencomienda),
    path('showencomiendas/', views.showencomiendas),
    path('eliminarencomienda/<int:id>/', views.eliminarencomienda),
    path('rastrear_encomienda/', views.rastrear_encomienda),
    path('editcliente/<int:id>', views.editcliente),
    path('actualizar_cliente/<int:id>/', views.actualizar_cliente),
    path('editencomienda/<int:id>', views.editencomienda),
    path('actualizar_encomienda/<int:id>/', views.actualizar_encomienda),
    path('actualizar_estados/', views.actualizar_estados),
]