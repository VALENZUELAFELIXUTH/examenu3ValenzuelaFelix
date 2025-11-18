from tienda.models import Venta
from django.utils import timezone
from datetime import timedelta
from django.db import transaction 
from datetime import timedelta, datetime, time, date # <<< IMPORTACIONES AÑADIDAS
# tienda/views.py
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import render, redirect, get_object_or_404 # Funciones comunes para renderizar, redirigir y obtener objetos.
from django.contrib.auth.decorators import login_required, permission_required # Decoradores para requerir autenticación y permisos.
from django.contrib.auth.views import LoginView, LogoutView # Vistas predefinidas de Django para autenticación.
from django.urls import reverse_lazy # Función para obtener URLs de forma perezosa.
from django.contrib.auth.models import Group # Modelo para gestionar grupos/roles de usuarios.
from django.contrib import messages # Módulo para enviar mensajes de notificación al usuario.
from .models import Producto, Categoria, PerfilUsuario, Proveedor, Cliente, Venta, DetalleVenta # Importa los modelos necesarios.
from .forms import ProductoForm, CategoriaForm, ProveedorForm, ClienteForm # Importa el formulario de Producto.

from django.db.models import Sum, Count 
from django.utils import timezone 
from datetime import timedelta


# ============ DECORADOR PERSONALIZADO PARA PERMISOS POR ROL ============
def rol_requerido(*roles_permitidos):
    """
    Decorador personalizado que verifica si el usuario tiene uno de los roles permitidos.
    
    Uso:
        @rol_requerido('gerente', 'administrador')
        def mi_vista(request):
            ...
    
    Parámetros:
        *roles_permitidos: Lista de roles que pueden acceder a la vista
        Opciones: 'vendedor', 'gerente', 'administrador'
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            # 1. Verificar si el usuario está autenticado
            if not request.user.is_authenticated:
                messages.error(request, 'Debes iniciar sesión para acceder')
                return redirect('login')
            
            # 2. Si es superusuario, permitir acceso siempre
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            
            # 3. Verificar si el usuario tiene perfil con rol asignado
            try:
                perfil = request.user.perfil  # Obtener perfil del usuario
                # 4. Verificar si su rol está en los roles permitidos
                if perfil.rol in roles_permitidos:
                    return view_func(request, *args, **kwargs)  # Permitir acceso
                else:
                    # Mostrar mensaje de error indicando roles necesarios
                    roles_texto = ', '.join([r.capitalize() for r in roles_permitidos])
                    messages.error(request, f'⚠️ Acceso denegado. Se requiere rol: {roles_texto}')
                    return redirect('home')  # Redirigir al home
            except PerfilUsuario.DoesNotExist:
                # Si el usuario no tiene perfil asignado
                messages.error(request, '⚠️ Tu cuenta no tiene un perfil asignado. Contacta al administrador.')
                return redirect('home')
        
        return _wrapped_view
    return decorator


# ============ VISTA DE LOGIN ============
def login_view(request):
    """Vista para el inicio de sesión de usuarios"""
    # Si el usuario ya está autenticado, redirigir al home
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Si el método es POST, procesamos el formulario de login
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)  # Creamos el formulario con los datos enviados
        if form.is_valid():  # Si el formulario es válido
            username = form.cleaned_data.get('username')  # Obtenemos el nombre de usuario
            password = form.cleaned_data.get('password')  # Obtenemos la contraseña
            user = authenticate(username=username, password=password)  # Autenticamos al usuario
            if user is not None:  # Si la autenticación fue exitosa
                login(request, user)  # Iniciamos sesión
                messages.success(request, f'Bienvenido {username}!')  # Mensaje de bienvenida
                return redirect('home')  # Redirigimos al home
            else:
                messages.error(request, 'Usuario o contraseña incorrectos')  # Mensaje de error
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')  # Mensaje de error si el formulario no es válido
    else:
        form = AuthenticationForm()  # Si es GET, creamos un formulario vacío
    
    return render(request, 'tienda/login.html', {'form': form})  # Renderizamos el template de login


# ============ VISTA DE LOGOUT ============
def logout_view(request):
    """Vista para cerrar sesión"""
    logout(request)  # Cerramos la sesión del usuario
    messages.info(request, 'Sesión cerrada correctamente')  # Mensaje informativo
    return redirect('login')  # Redirigimos al login


# ============ VISTA PRINCIPAL (HOME) ============
@login_required  # Decorador que requiere autenticación para acceder a esta vista
def home(request):
    """Vista principal que muestra el dashboard con estadísticas"""
    # Contamos los registros de cada modelo
    total_productos = Producto.objects.count()  # Cuenta todos los productos
    total_categorias = Categoria.objects.count()  # Cuenta todas las categorías
    total_proveedores = Proveedor.objects.count()  # Cuenta todos los proveedores
    total_clientes = Cliente.objects.count()  # Cuenta todos los clientes
    
    # Obtenemos los últimos 5 productos creados
    productos_recientes = Producto.objects.all()[:5]  # Slice de los primeros 5 productos
    
    # Creamos un diccionario con los datos que enviaremos al template
    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_proveedores': total_proveedores,
        'total_clientes': total_clientes,
        'productos_recientes': productos_recientes,
    }
    
    return render(request, 'tienda/home.html', context)  # Renderizamos el template con el contexto


# ============ VISTAS CRUD PARA PRODUCTOS ============
@login_required
def producto_lista(request):
    """Vista que lista todos los productos"""
    productos = Producto.objects.all()  # Obtenemos todos los productos de la base de datos
    return render(request, 'tienda/producto_lista.html', {'productos': productos})  # Renderizamos template con la lista


@login_required
def producto_crear(request):
    """Vista para crear un nuevo producto"""
    if request.method == 'POST':  # Si se envió el formulario
        form = ProductoForm(request.POST)  # Creamos el formulario con los datos enviados
        if form.is_valid():  # Si el formulario es válido (todos los campos correctos)
            form.save()  # Guardamos el producto en la base de datos
            messages.success(request, 'Producto creado exitosamente')  # Mensaje de éxito
            return redirect('producto_lista')  # Redirigimos a la lista de productos
    else:
        form = ProductoForm()  # Si es GET, creamos un formulario vacío
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Crear'})  # Renderizamos el formulario


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador pueden editar
def producto_editar(request, pk):
    """Vista para editar un producto existente"""
    producto = get_object_or_404(Producto, pk=pk)  # Obtenemos el producto por su ID (Primary Key), si no existe muestra 404
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)  # Creamos el formulario con los datos del producto existente
        if form.is_valid():
            form.save()  # Guardamos los cambios
            messages.success(request, 'Producto actualizado exitosamente')
            return redirect('producto_lista')
    else:
        form = ProductoForm(instance=producto)  # Mostramos el formulario con los datos actuales del producto
    
    return render(request, 'tienda/producto_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')  # Solo Administrador puede eliminar
def producto_eliminar(request, pk):
    """Vista para eliminar un producto"""
    producto = get_object_or_404(Producto, pk=pk)  # Obtenemos el producto
    if request.method == 'POST':  # Confirmación de eliminación debe ser POST por seguridad
        producto.delete()  # Eliminamos el producto de la base de datos
        messages.success(request, 'Producto eliminado exitosamente')
        return redirect('producto_lista')
    
    return render(request, 'tienda/producto_eliminar.html', {'producto': producto})  # Mostramos página de confirmación


# ============ VISTAS CRUD PARA CATEGORÍAS ============
@login_required
@rol_requerido('gerente', 'administrador', 'cliente', 'vendedor')  # Vendedor NO puede ver categorías
def categoria_lista(request):
    """Vista que lista todas las categorías"""
    categorias = Categoria.objects.all()
    return render(request, 'tienda/categoria_lista.html', {'categorias': categorias})


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador
def categoria_crear(request):
    """Vista para crear una nueva categoría"""
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm()
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def categoria_editar(request, pk):
    """Vista para editar una categoría existente"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada exitosamente')
            return redirect('categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    
    return render(request, 'tienda/categoria_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')  # Solo Administrador
def categoria_eliminar(request, pk):
    """Vista para eliminar una categoría"""
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada exitosamente')
        return redirect('categoria_lista')
    
    return render(request, 'tienda/categoria_eliminar.html', {'categoria': categoria})


# ============ VISTAS CRUD PARA PROVEEDORES ============
@login_required
@rol_requerido('gerente', 'administrador', 'vendedor')  # Vendedor NO puede ver proveedores
def proveedor_lista(request):
    """Vista que lista todos los proveedores"""
    proveedores = Proveedor.objects.all()
    return render(request, 'tienda/proveedor_lista.html', {'proveedores': proveedores})


@login_required
@rol_requerido('gerente', 'administrador')  # Solo Gerente y Administrador
def proveedor_crear(request):
    """Vista para crear un nuevo proveedor"""
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor creado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm()
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def proveedor_editar(request, pk):
    """Vista para editar un proveedor existente"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado exitosamente')
            return redirect('proveedor_lista')
    else:
        form = ProveedorForm(instance=proveedor)
    
    return render(request, 'tienda/proveedor_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')
def proveedor_eliminar(request, pk):
    """Vista para eliminar un proveedor"""
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, 'Proveedor eliminado exitosamente')
        return redirect('proveedor_lista')
    
    return render(request, 'tienda/proveedor_eliminar.html', {'proveedor': proveedor})


# ============ VISTAS CRUD PARA CLIENTES ============
@login_required
def cliente_lista(request):
    """Vista que lista todos los clientes"""
    clientes = Cliente.objects.all()
    return render(request, 'tienda/cliente_lista.html', {'clientes': clientes})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_crear(request):
    """Vista para crear un nuevo cliente"""
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente creado exitosamente')
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    
    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Crear'})


@login_required
@rol_requerido('gerente', 'administrador')
def cliente_editar(request, pk):
    """Vista para editar un cliente existente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente')
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    
    return render(request, 'tienda/cliente_form.html', {'form': form, 'accion': 'Editar'})


@login_required
@rol_requerido('administrador')
def cliente_eliminar(request, pk):
    """Vista para eliminar un cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado exitosamente')
        return redirect('cliente_lista')
    
    return render(request, 'tienda/cliente_eliminar.html', {'cliente': cliente})

# ============ VISTAS PARA VENTAS (REGISTRAR) ============
try:
    from .forms import VentaForm, DetalleVentaFormSet 
except ImportError:
    VentaForm = None
    DetalleVentaFormSet = None
    print("ADVERTENCIA: No se pudieron importar VentaForm o DetalleVentaFormSet. 'registrar_venta' fallará.")

#============ VISTA PRINCIPAL (DASHBOARD) - CORREGIDA FINAL ============
@login_required
def dashboard(request):
    """Vista principal que muestra el dashboard con estadísticas y cálculo de ventas."""
    
    # Cálculos base
    total_productos = Producto.objects.count()
    total_categorias = Categoria.objects.count()
    total_proveedores = Proveedor.objects.count()
    total_clientes = Cliente.objects.count()
    
    # LÓGICA DE CÁLCULO DE VENTAS DE HOY USANDO RANGO
    now = timezone.localtime(timezone.now())
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + timedelta(days=1)
    
    ventas_hoy_query = Venta.objects.filter(
        fecha_venta__gte=start_of_day,
        fecha_venta__lt=end_of_day
    ).aggregate(
        total_hoy=Sum('total')
    )['total_hoy']
    
    total_ventas_hoy = ventas_hoy_query or 0.00
    
    productos_recientes = Producto.objects.order_by('-id')[:5]
    
    context = {
        'total_productos': total_productos,
        'total_categorias': total_categorias,
        'total_proveedores': total_proveedores,
        'total_clientes': total_clientes,
        'productos_recientes': productos_recientes,
        'total_ventas_hoy': total_ventas_hoy, 
    }
    
    return render(request, 'tienda/dashboard.html', context)
    

# ============ VISTA DE REPORTE DE VENTAS (COMPLETA CON FILTRO POR RANGO) ============

@login_required
@rol_requerido('gerente', 'administrador', 'vendedor') 
def reporte_ventas(request):
    """
    Calcula y muestra el reporte de ventas, implementando la funcionalidad de filtrar
    por rango de fechas usando parámetros GET.
    """
    
    # 1. Definición de la zona horaria actual (base para Mes y Año)
    now = timezone.localtime(timezone.now())
    
    # 2. LÓGICA DE FILTRO POR RANGO DE FECHAS
    fecha_inicio_str = request.GET.get('fecha_inicio')
    fecha_fin_str = request.GET.get('fecha_fin')
    
    # QuerySet base para Venta y DetalleVenta
    ventas_base_query = Venta.objects.all()
    detalles_base_query = DetalleVenta.objects.select_related(
        'venta', 'producto', 'venta__vendido_por'
    )
    
    # Variables para pasar al template (mantener los valores en el formulario)
    filtro_fecha_inicio = fecha_inicio_str
    filtro_fecha_fin = fecha_fin_str
    
    # 3. Aplicar el filtro si se proporcionan las fechas
    if fecha_inicio_str and fecha_fin_str:
        try:
            # Convertir la fecha de inicio a datetime (00:00:00) y hacerlo consciente de la zona horaria (aware)
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_inicio_dt = timezone.make_aware(datetime.combine(fecha_inicio, time.min))
            
            # Convertir la fecha de fin a datetime (23:59:59.999999) y hacerlo consciente de la zona horaria (aware)
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
            fecha_fin_dt = timezone.make_aware(datetime.combine(fecha_fin, time.max))

            # Aplicar filtro __range al QuerySet
            ventas_filtradas = ventas_base_query.filter(
                fecha_venta__range=(fecha_inicio_dt, fecha_fin_dt)
            )
            detalles_ventas_filtrados = detalles_base_query.filter(
                venta__fecha_venta__range=(fecha_inicio_dt, fecha_fin_dt)
            ).order_by('-venta__fecha_venta')
            
        except ValueError:
            # Si hay un error en el formato de fecha, se usa la lógica de HOY
            messages.error(request, 'Formato de fecha inválido. Usando ventas de HOY.')
            
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            ventas_filtradas = ventas_base_query.filter(
                fecha_venta__gte=start_of_day,
                fecha_venta__lt=end_of_day
            )
            detalles_ventas_filtrados = detalles_base_query.filter(
                venta__fecha_venta__gte=start_of_day,
                venta__fecha_venta__lt=end_of_day
            ).order_by('-venta__fecha_venta')

            # Ajustar variables para el contexto de la tabla y el formulario
            filtro_fecha_inicio = start_of_day.strftime('%Y-%m-%d')
            filtro_fecha_fin = (end_of_day - timedelta(seconds=1)).strftime('%Y-%m-%d')


    else:
        # Si NO hay filtros, se usan las ventas de HOY como predeterminadas
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = start_of_day + timedelta(days=1)
        
        ventas_filtradas = ventas_base_query.filter(
            fecha_venta__gte=start_of_day,
            fecha_venta__lt=end_of_day
        )
        detalles_ventas_filtrados = detalles_base_query.filter(
            venta__fecha_venta__gte=start_of_day,
            venta__fecha_venta__lt=end_of_day
        ).order_by('-venta__fecha_venta')

        # Ajustar variables para el contexto de la tabla y el formulario
        filtro_fecha_inicio = start_of_day.strftime('%Y-%m-%d')
        filtro_fecha_fin = (end_of_day - timedelta(seconds=1)).strftime('%Y-%m-%d')
        
    # 4. Calcular los agregados (Total y Conteo) del conjunto FILTRADO
    agregados_filtrados = ventas_filtradas.aggregate(
        total=Sum('total'),
        numero=Count('id')
    )
    
    # 5. CÁLCULO MANUAL DEL PROMEDIO
    total_vendido = agregados_filtrados.get('total') or 0.00
    numero_ventas = agregados_filtrados.get('numero') or 0
    promedio_venta = total_vendido / numero_ventas if numero_ventas > 0 else 0.00
    
    # 6. Cálculos para Mes y Año (Estos no se filtran por el GET, mantienen su lógica)
    start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    end_of_next_month = (start_of_month + timedelta(days=32)).replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    ventas_mes_query = Venta.objects.filter(
        fecha_venta__gte=start_of_month,
        fecha_venta__lt=end_of_next_month
    ).aggregate(total_mes=Sum('total')).get('total_mes')

    ventas_anio_query = Venta.objects.filter(
        fecha_venta__year=now.year
    ).aggregate(total_anio=Sum('total')).get('total_anio')

    total_mes = ventas_mes_query or 0.00
    total_anio = ventas_anio_query or 0.00
    
    # 7. Preparación del Contexto
    contexto = {
        'titulo': 'Reporte de Ventas',
        'fecha_reporte': now,
        'total_vendido': total_vendido, 
        'numero_ventas': numero_ventas,
        'promedio_venta': promedio_venta, 
        'detalles_ventas': detalles_ventas_filtrados, # Usamos el QuerySet filtrado
        'ventas_mes': total_mes,
        'ventas_anio': total_anio,
        'fecha_inicio': filtro_fecha_inicio, # Para mantener el valor en el form
        'fecha_fin': filtro_fecha_fin,       # Para mantener el valor en el form
        'today_date': date.today(),
    }

    return render(request, 'tienda/reporte_ventas.html', contexto)
    

@login_required
@rol_requerido('gerente', 'administrador')
def registrar_venta(request):
    """
    Vista principal del Punto de Venta (TPV). Maneja el formulario Venta y el formset
    para DetalleVenta, incluyendo la lógica de guardado transaccional.
    """
    if VentaForm is None or DetalleVentaFormSet is None:
        messages.error(request, 'Error: Faltan formularios (VentaForm/DetalleVentaFormSet). Contacta al administrador.')
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = VentaForm(request.POST)
        formset = DetalleVentaFormSet(request.POST, instance=Venta()) 
        
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    venta = form.save(commit=False)
                    venta.empleado = request.user 
                    venta.total = request.POST.get('total', 0.00) 
                    venta.vendido_por = request.user
                    venta.save()
                    
                    formset.instance = venta 
                    detalle_venta_objects = formset.save(commit=False)
                    
                    for detalle in detalle_venta_objects:
                        detalle.venta = venta
                        detalle.save()
                        
                        producto = detalle.producto
                        if producto.stock >= detalle.cantidad:
                            producto.stock -= detalle.cantidad
                            producto.save()
                        else:
                            raise Exception(f'Stock insuficiente para {producto.nombre}. Cantidad disponible: {producto.stock}')
                            
                    formset.save_m2m()
                        
                messages.success(request, f"Venta #{venta.pk} registrada con éxito.")
                return redirect('dashboard') 

            except Exception as e:
                messages.error(request, f"Error al registrar la venta. Detalles: {e}")
        else:
            messages.warning(request, "Revisa los errores del formulario principal o de los detalles.")
            
    else: # GET request (Inicialización)
        form = VentaForm()
        formset = DetalleVentaFormSet(instance=Venta())

    contexto = {
        'titulo': 'Registrar Nueva Venta',
        'form': form,
        'formset': formset,
    }
    
    return render(request, 'tienda/registrar_venta.html', contexto)
#=======================
# VISTAS PARA CLIENTES (ROL CLIENTE)
# =======================
@login_required
@rol_requerido('cliente')
def cliente_dashboard(request):
    """Dashboard exclusivo para clientes (solo ven sus propias compras)."""
    cliente = getattr(request.user, 'cliente', None)
    if not cliente:
        messages.error(request, "Tu cuenta no está asociada a un cliente.")
        return redirect('login')

    # Obtener las ventas del cliente autenticado
    ventas_cliente = Venta.objects.filter(cliente=cliente).order_by('-fecha_venta')

    context = {
        'titulo': 'Mi Panel de Cliente',
        'cliente': cliente,
        'ventas': ventas_cliente,
    }
    return render(request, 'tienda/cliente_dashboard.html', context)


@login_required
@rol_requerido('cliente')
def cliente_detalle_venta(request, pk):
    """Permite al cliente ver el detalle de una venta suya."""
    cliente = getattr(request.user, 'cliente', None)
    venta = get_object_or_404(Venta, pk=pk, cliente=cliente)
    detalles = venta.detalles.all()
    
    context = {
        'titulo': f'Detalle de Venta #{venta.pk}',
        'venta': venta,
        'detalles': detalles,
    }
    return render(request, 'tienda/cliente_detalle_venta.html', context)