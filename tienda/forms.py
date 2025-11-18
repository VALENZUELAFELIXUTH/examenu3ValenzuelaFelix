# tienda/forms.py
# Importamos forms de Django para crear formularios
from django import forms
from django.forms.models import inlineformset_factory 
from .models import Producto, Categoria, Proveedor, Cliente, Venta, DetalleVenta # Importamos nuestros modelos


# ============ FORMULARIO PARA PRODUCTOS ============
class ProductoForm(forms.ModelForm):
    """Formulario para crear y editar productos"""
    
    # Meta clase define la configuración del formulario
    class Meta:
        model = Producto  # El modelo que usará este formulario
        fields = ['nombre', 'descripcion', 'precio', 'stock', 'categoria', 'activo']  # Campos que aparecerán en el formulario
        
        # Widgets: personalización de cómo se muestran los campos en HTML
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',  # Clase de Bootstrap para estilos
                'placeholder': 'Ingrese el nombre del producto'  # Texto de ayuda en el campo
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,  # Altura del textarea en filas
                'placeholder': 'Ingrese una descripción del producto'
            }),
            'precio': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',  # Permite decimales de 2 dígitos
                'min': '0',  # Valor mínimo
                'placeholder': '0.00'
            }),
            'stock': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'placeholder': '0'
            }),
            # Select para la categoría (combobox con las opciones de categorías)
            'categoria': forms.Select(attrs={
                'class': 'form-control'
            }),
            # Checkbox para el campo activo
            'activo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        
        # Labels: etiquetas personalizadas para cada campo
        labels = {
            'nombre': 'Nombre del Producto',
            'descripcion': 'Descripción',
            'precio': 'Precio ($)',
            'stock': 'Cantidad en Stock',
            'categoria': 'Categoría',
            'activo': '¿Producto Activo?',
        }


# ============ FORMULARIO PARA CATEGORÍAS ============
class CategoriaForm(forms.ModelForm):
    """Formulario para crear y editar categorías"""
    
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']  # Solo nombre y descripción
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el nombre de la categoría'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Ingrese una descripción (opcional)'
            }),
        }
        
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
        }


# ============ FORMULARIO PARA PROVEEDORES ============
class ProveedorForm(forms.ModelForm):
    """Formulario para crear y editar proveedores"""
    
    class Meta:
        model = Proveedor
        fields = ['nombre', 'empresa', 'telefono', 'email', 'direccion']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del contacto'
            }),
            'empresa': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de la empresa'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'email': forms.EmailInput(attrs={  # EmailInput valida formato de email
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección completa'
            }),
        }
        
        labels = {
            'nombre': 'Nombre del Contacto',
            'empresa': 'Empresa',
            'telefono': 'Teléfono',
            'email': 'Correo Electrónico',
            'direccion': 'Dirección',
        }


# ============ FORMULARIO PARA CLIENTES ============
class ClienteForm(forms.ModelForm):
    """Formulario para crear y editar clientes"""
    
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'email', 'telefono', 'direccion']
        
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre del cliente'
            }),
            'apellido': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apellido del cliente'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'telefono': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Teléfono de contacto'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Dirección de entrega'
            }),
        }
        
        labels = {
            'nombre': 'Nombre',
            'apellido': 'Apellido',
            'email': 'Correo Electrónico',
            'telefono': 'Teléfono',
            'direccion': 'Dirección',
        }


# ============ FORMULARIO PARA VENTA ============
class VentaForm(forms.ModelForm):
    """Formulario para registrar una venta. Anteriormente daba error."""
    
    class Meta:
        # El error era porque Venta no estaba importado en la línea 3
        model = Venta 
        fields = ['cliente'] 
        
        # Widgets y Labels recomendados para la Venta
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-control'}),
            'total': forms.NumberInput(attrs={
                'class': 'form-control', 
                'step': '0.01', 
                'min': '0',
                'placeholder': '0.00'
            }),
        }
        
        labels = {
            'cliente': 'Cliente',
            'total': 'Total de la Venta ($)',
        }

# ==============================
# FORMSET para Detalle de Venta
# ==============================
DetalleVentaFormSet = inlineformset_factory(
    Venta,                        # Modelo principal
    DetalleVenta,                 # Modelo hijo
    fields=['producto', 'cantidad'],  # Campos que se llenan manualmente
    extra=1,                      # Cuántas filas vacías aparecerán
    can_delete=True,              # Permite eliminar líneas del detalle
    widgets={
        'producto': forms.Select(attrs={'class': 'form-control'}),
        'cantidad': forms.NumberInput(attrs={
            'class': 'form-control',
            'min': '1',
            'placeholder': 'Cantidad'
        }),
        'precio_unitario': forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        }),
    }
)
class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['producto', 'cantidad', 'precio_unitario']
        widgets = {
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'placeholder': 'Cantidad'}),
            'precio_unitario': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
        }
