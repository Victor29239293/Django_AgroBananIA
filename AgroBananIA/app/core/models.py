from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from decimal import Decimal

# Definición de actividades agrícolas reutilizable
class ActividadAgricola(models.TextChoices):
    FERTILIZACION = 'fertilizacion', 'Fertilización'
    RIEGO = 'riego', 'Riego'
    COSECHA = 'cosecha', 'Cosecha'
    PODA = 'poda', 'Poda'
    OTRO = 'otro', 'Otro'

# Campo decimal redondeado automáticamente
class RoundedDecimalField(models.DecimalField):
    def to_python(self, value):
        val = super().to_python(value)
        if val is None:
            return val
        # Redondeo automático según max_digits y decimal_places
        return val.quantize(Decimal('1.' + '0' * self.decimal_places))

class PerfilUsuario(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")
    direccion = models.TextField(blank=True, verbose_name="Dirección")
    foto_perfil = models.ImageField(
        upload_to='perfiles/',
        blank=True, 
        null=True
    )
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.user.username}"

class Plantacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plantaciones')
    nombre_finca = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    extension_hectareas = models.DecimalField(max_digits=6, decimal_places=2)
    latitud = models.DecimalField(max_digits=9, decimal_places=6)
    longitud = models.DecimalField(max_digits=9, decimal_places=6)
    fecha_registro = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre_finca} ({self.usuario.username})"

    @property
    def registros_activos(self):
        return self.registros_campo.count()

    @property
    def ultimo_registro(self):
        return self.registros_campo.order_by('-fecha_registro').first()

    @property
    def temperatura_promedio(self):
        # Uso eficiente de aggregate para evitar cargar todos los registros
        return self.registros_campo.aggregate(avg=Avg('temperatura'))['avg'] or Decimal('0.0')

class RegistroCampo(models.Model):
    plantacion = models.ForeignKey(Plantacion, on_delete=models.CASCADE, related_name='registros_campo')
    fecha_registro = models.DateField(default=timezone.now, db_index=True)  # Índice para mejorar rendimiento
    
    # Datos Climáticos
    temperatura = models.DecimalField(max_digits=4, decimal_places=1, help_text="Temperatura en °C")
    humedad = models.DecimalField(
        max_digits=5, decimal_places=2, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Humedad relativa en %"
    )
    precipitacion = models.DecimalField(
        max_digits=6, decimal_places=2, 
        validators=[MinValueValidator(0)],
        help_text="Precipitación en mm"
    )
    
    # Datos del Suelo
    ph_suelo = models.DecimalField(
        max_digits=4, decimal_places=1,  # Ajustado max_digits para cubrir 0.0 a 14.0
        validators=[MinValueValidator(0), MaxValueValidator(14)],
        help_text="pH del suelo"
    )
    humedad_suelo = models.DecimalField(
        max_digits=5, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Humedad del suelo en %"
    )
    nitrogeno = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0)],
        # Usar RoundedDecimalField para evitar errores de validación por precisión
        help_text="Nitrógeno en ppm"
    )
    
    # Prácticas Agrícolas
    actividad_realizada = models.CharField(
        max_length=100, 
        blank=True, 
        choices=ActividadAgricola.choices  # Uso de TextChoices
    )
    observaciones = models.TextField(blank=True)
    
    # Metadatos
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = "Registro de Campo"
        verbose_name_plural = "Registros de Campo"

    def __str__(self):
        return f"Registro {self.plantacion.nombre_finca} - {self.fecha_registro}"

class ImagenAnalisis(models.Model):
    plantacion = models.ForeignKey(Plantacion, on_delete=models.CASCADE, related_name='imagenes')
    imagen = models.ImageField(upload_to='imagenes_analisis/')
    contorno = models.ImageField(upload_to='imagenes_analisis/contornos/', null=True, blank=True)
    overlay = models.ImageField(upload_to='imagenes_analisis/overlay/', null=True, blank=True)
    damage = models.ImageField(upload_to='imagenes_analisis/dano/', null=True, blank=True)
    fecha_envio = models.DateTimeField(auto_now_add=True, db_index=True)  # Índice para consultas frecuentes

    def __str__(self):
        return f"Imagen {self.id} - {self.plantacion.nombre_finca}"

class ResultadoAnalisis(models.Model):
    imagen = models.OneToOneField(ImagenAnalisis, on_delete=models.CASCADE, related_name='resultado')
    enfermedad_detectada = models.CharField(max_length=100)
    probabilidad = models.FloatField()
    recomendaciones = models.TextField()
    informe_pdf = models.FileField(upload_to='informes/', null=True, blank=True)
    fecha_analisis = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resultado - {self.enfermedad_detectada} ({self.probabilidad:.2f}%)"

class AlertaComunitaria(models.Model):
    usuario_origen = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_emitidas')
    usuario_destino = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alertas_recibidas')
    plantacion_origen = models.ForeignKey(Plantacion, on_delete=models.CASCADE, related_name='alertas_generadas')
    enfermedad = models.CharField(max_length=100)
    distancia = models.FloatField(help_text='Distancia en km')
    fecha_alerta = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-fecha_alerta']
        verbose_name = 'Alerta Comunitaria'
        verbose_name_plural = 'Alertas Comunitarias'

    def __str__(self):
        return f"Alerta de {self.enfermedad} de {self.usuario_origen} a {self.usuario_destino} ({self.distancia} km)"
