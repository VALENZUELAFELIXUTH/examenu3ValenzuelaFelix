# tienda/models.py
import os
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum # Importado para calcular el total
from decimal import Decimal # Importado para manejar valores decimales


# ===================== MODELO PERFIL DE USUARIO =====================
class PerfilUsuario(models.Model):
    ROLES = (
        ('vendedor', 'Vendedor'),
        ('gerente', 'Gerente'),
        ('administrador', 'Administrador'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    rol = models.CharField(max_length=20, choices=ROLES, default='vendedor')
    telefono = models.CharField(max_length=15, blank=True, null=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    fecha_contratacion = models.DateField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

    # ===================== MÉTODOS DE ROL Y PERMISOS =====================
    def es_vendedor(self):
        return self.rol == 'vendedor'

    def es_gerente(self):
        return self.rol == 'gerente'

    def es_administrador(self):
        return self.rol == 'administrador'

    def tiene_permiso_lectura(self):
        return True  # Todos pueden leer

    def tiene_permiso_escritura(self):
        return self.rol in ['gerente', 'administrador']

    def tiene_permiso_eliminacion(self):
        return self.rol == 'administrador'

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"


# ===================== MODELO CATEGORÍA =====================
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ['nombre']


# ===================== MODELO PROVEEDOR =====================
class Proveedor(models.Model):
    """Información de las empresas que suministran los productos."""
    nombre = models.CharField(max_length=200)
    empresa = models.CharField(max_length=200, unique=True, default='Sin Empresa')
    telefono = models.CharField(max_length=15, blank=True) 
    email = models.EmailField(max_length=191, unique=True, null=True, blank=True) 
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nombre} - {self.empresa}" 
    
    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        ordering = ['empresa']

# ===================== MODELO PRODUCTO =====================
class Producto(models.Model):
    """Artículo que se vende en la tienda."""
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField()
    precio = models.DecimalField(max_digits=10, decimal_places=2) 
    stock = models.IntegerField(default=0) 
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos') 
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True, related_name='productos_suministrados') 
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='productos_creados') 
    fecha_creacion = models.DateTimeField(auto_now_add=True) 
    activo = models.BooleanField(default=True) 

    def __str__(self):
        return self.nombre 
    
    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"


# ===================== MODELO CLIENTE =====================
class Cliente(models.Model):

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE, 
        related_name='cliente', 
        null=True, blank=True)
    
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    email = models.EmailField(max_length=191, unique=True)
    telefono = models.CharField(max_length=15)
    direccion = models.TextField()
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['apellido', 'nombre']


# ============ MODELO VENTA (Transacción) - CORREGIDO ============
class Venta(models.Model):
    """Registro de una transacción de venta."""
    fecha_venta = models.DateTimeField(auto_now_add=True) 
    total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        null=True,   # <-- 🛑 CORRECCIÓN: Permite NULL para evitar IntegrityError en el admin
        blank=True   # <-- 🛑 CORRECCIÓN: Permite dejarlo en blanco en el formulario
    ) 
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name='ventas') 
    vendido_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ventas_realizadas') 
    
    def calcular_total(self):
        """Calcula el total sumando los subtotales de los detalles."""
        # Se usa self.detalles, que es el related_name del ForeignKey en DetalleVenta
        total_calculado = self.detalles.aggregate(total=Sum('subtotal'))['total']
        return total_calculado if total_calculado is not None else Decimal('0.00')
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Recalcula el total después de guardar, en caso de que haya detalles
        total_calculado = self.calcular_total()
        if self.total != total_calculado:
            self.total = total_calculado
            super().save(update_fields=['total'])

    def __str__(self):
        # Muestra el total si no es None, si es None muestra N/A
        return f"Venta #{self.id} - Total: {self.total if self.total is not None else 'N/A'}"
    
    class Meta:
        verbose_name = "Venta"
        verbose_name_plural = "Ventas"

# ============ MODELO DETALLE DE VENTA ============
class DetalleVenta(models.Model):
    """Artículos incluidos en una venta específica."""
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2) 
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False, default=0) # Añadido default=0
    
    def save(self, *args, **kwargs):
        """Calcula el subtotal automáticamente antes de guardar."""
        # Forzar precio_unitario a 0 si es None
        if self.precio_unitario is None or self.precio_unitario == 0:
            self.precio_unitario = self.producto.precio

        # Calcular subtotal
        self.subtotal = self.cantidad * self.precio_unitario

        super().save(*args, **kwargs)
        
        # Recalcular y actualizar total de la venta
        if self.venta_id:
            self.venta.total = self.venta.calcular_total()
            self.venta.save(update_fields=['total'])


    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre} en Venta #{self.venta.id}"
    
    class Meta:
        verbose_name = "Detalle de Venta"
        verbose_name_plural = "Detalles de Venta"
        unique_together = ('venta', 'producto')