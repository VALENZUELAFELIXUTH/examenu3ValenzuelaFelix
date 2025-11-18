from django.urls import path
from . import views

urlpatterns = [
    # Autenticación
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Dashboard
    path('', views.dashboard, name='home'),  # URL raíz
    path('dashboard/', views.dashboard, name='dashboard'),

    # CRUD Productos
    path('productos/', views.producto_lista, name='producto_lista'),
    path('productos/crear/', views.producto_crear, name='producto_crear'),
    path('productos/editar/<int:pk>/', views.producto_editar, name='producto_editar'),
    path('productos/eliminar/<int:pk>/', views.producto_eliminar, name='producto_eliminar'),

    # Categorías
    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/crear/', views.categoria_crear, name='categoria_crear'),
    path('categorias/editar/<int:pk>/', views.categoria_editar, name='categoria_editar'),
    path('categorias/eliminar/<int:pk>/', views.categoria_eliminar, name='categoria_eliminar'),

    # Proveedores
    path('proveedores/', views.proveedor_lista, name='proveedor_lista'),
    path('proveedores/crear/', views.proveedor_crear, name='proveedor_crear'),
    path('proveedores/editar/<int:pk>/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/eliminar/<int:pk>/', views.proveedor_eliminar, name='proveedor_eliminar'),

    # Clientes
    path('clientes/', views.cliente_lista, name='cliente_lista'),
    path('clientes/crear/', views.cliente_crear, name='cliente_crear'),
    path('clientes/editar/<int:pk>/', views.cliente_editar, name='cliente_editar'),
    path('clientes/eliminar/<int:pk>/', views.cliente_eliminar, name='cliente_eliminar'),


# ==============================
    # VENTAS (¡NUEVA SECCIÓN!)
    # ==============================
    # Esta es la URL que faltaba para resolver el error 'NoReverseMatch'
    path('ventas/registrar/', views.registrar_venta, name='registrar_venta'),
    
    # Reporte de Ventas
    path('ventas/reporte/', views.reporte_ventas, name='reporte_ventas'),
]
