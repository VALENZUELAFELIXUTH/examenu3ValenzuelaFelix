# tienda/admin.py
# Importamos el módulo admin de Django para registrar modelos
from django.contrib import admin
# Importamos todos nuestros modelos
from .models import Categoria, Producto, Proveedor, Cliente, PerfilUsuario, Venta, DetalleVenta


# ============ CONFIGURACIÓN DEL ADMIN PARA PERFILES DE USUARIO ============
@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    """Configuración personalizada del admin para Perfiles de Usuario"""
    list_display = ('user', 'rol', 'departamento', 'activo', 'fecha_contratacion')  # Columnas visibles
    list_filter = ('rol', 'activo', 'departamento')  # Filtros laterales por rol, estado y departamento
    search_fields = ('user__username', 'user__email', 'departamento')  # Búsqueda por usuario o departamento
    list_editable = ('rol', 'activo')  # Permite editar rol y estado desde la lista
    ordering = ('-fecha_contratacion',)  # Orden descendente por fecha de contratación


# ============ CONFIGURACIÓN DEL ADMIN PARA CATEGORÍAS ============
@admin.register(Categoria)  # Decorador que registra el modelo Categoria
class CategoriaAdmin(admin.ModelAdmin):
    """Configuración personalizada del admin para Categorías"""
    list_display = ('id', 'nombre', 'fecha_creacion')  # Columnas que se muestran en la lista
    search_fields = ('nombre',)  # Campos por los que se puede buscar
    list_filter = ('fecha_creacion',)  # Filtros laterales
    ordering = ('nombre',)  # Orden por defecto


# ============ CONFIGURACIÓN DEL ADMIN PARA PRODUCTOS ============
@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    """Configuración personalizada del admin para Productos"""
    list_display = ('id', 'nombre', 'categoria', 'precio', 'stock', 'activo', 'fecha_creacion')  # Columnas visibles
    search_fields = ('nombre', 'descripcion')  # Búsqueda por nombre o descripción
    list_filter = ('categoria', 'activo', 'fecha_creacion')  # Filtros por categoría, estado y fecha
    list_editable = ('precio', 'stock', 'activo')  # Campos editables directamente en la lista
    ordering = ('-fecha_creacion',)  # Orden descendente por fecha


# ============ CONFIGURACIÓN DEL ADMIN PARA PROVEEDORES ============
@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    """Configuración personalizada del admin para Proveedores"""
    list_display = ('id', 'nombre', 'empresa', 'telefono', 'email', 'fecha_registro')
    search_fields = ('nombre', 'empresa', 'email')  # Búsqueda por nombre, empresa o email
    list_filter = ('fecha_registro',)
    ordering = ('empresa',)


# ============ CONFIGURACIÓN DEL ADMIN PARA CLIENTES ============
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Configuración personalizada del admin para Clientes"""
    list_display = ('id', 'nombre', 'apellido', 'email', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'apellido', 'email')  # Búsqueda por nombre, apellido o email
    list_filter = ('fecha_registro',)
    ordering = ('apellido', 'nombre')  # Orden por apellido y luego nombre

# ============ CONFIGURACIÓN DEL ADMIN PARA VENTAS ============
class DetalleVentaInline(admin.TabularInline):
    """Permite editar los detalles de venta dentro del formulario de Venta."""
    model = DetalleVenta
    extra = 0 # No muestra filas vacías por defecto

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('id', 'fecha_venta', 'total', 'cliente', 'vendido_por')
    list_filter = ('fecha_venta',)
    search_fields = ('cliente__nombre', 'cliente__apellido')
    readonly_fields = ('total',) # El total se calcula automáticamente
    inlines = [DetalleVentaInline] # Muestra los detalles de venta

# Si Venta y DetalleVenta no se registran en los decoradores, puedes usar esta alternativa:
# admin.site.register(DetalleVenta) 
# admin.site.register(Venta, VentaAdmin)

# Nota: Con estas configuraciones, los modelos aparecerán en el panel de administración de Django
# accesible en http://localhost:8000/admin/