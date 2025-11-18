from django.db.models.signals import pre_save, pre_delete
from django.dispatch import receiver
from models import DetalleVenta, Producto

@receiver(pre_save, sender=DetalleVenta)
def actualizar_stock_pre_save(sender, instance, **kwargs):
    """
    Gestiona el stock antes de guardar un DetalleVenta (para nuevas creaciones o modificaciones).
    """
    try:
        # Si el objeto ya existe (modificación)
        detalle_anterior = DetalleVenta.objects.get(pk=instance.pk)
        
        # 1. Recuperar la cantidad anterior y devolverla al stock.
        cantidad_a_devolver = detalle_anterior.cantidad
        producto = detalle_anterior.producto
        producto.stock += cantidad_a_devolver
        producto.save()
        
    except DetalleVenta.DoesNotExist:
        # Si es un nuevo objeto (creación), no hay stock que devolver.
        pass

    # 2. Restar la nueva cantidad del stock del producto.
    producto = instance.producto
    cantidad_a_restar = instance.cantidad
    
    # Comprobación de stock (opcional, pero recomendada)
    if producto.stock < cantidad_a_restar:
        # Si no hay suficiente stock, podrías lanzar una excepción o ajustarlo.
        # Aquí solo lo restamos, asumiendo que el formulario de Admin ya lo valida.
        pass

    producto.stock -= cantidad_a_restar
    producto.save()


@receiver(pre_delete, sender=DetalleVenta)
def actualizar_stock_pre_delete(sender, instance, **kwargs):
    """
    Devuelve la cantidad del DetalleVenta eliminado al stock del Producto.
    """
    producto = instance.producto
    cantidad_a_devolver = instance.cantidad
    
    # Sumar la cantidad devuelta al stock
    producto.stock += cantidad_a_devolver
    producto.save()