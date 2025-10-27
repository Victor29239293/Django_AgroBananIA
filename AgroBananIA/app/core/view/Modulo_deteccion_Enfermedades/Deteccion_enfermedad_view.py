from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.contrib import messages
from AgroBananIA.utils.diagnostic import (
    predict_with_custom,
    obtener_nombre_enfermedad_custom,
    obtener_recomendaciones_custom,
    segment_and_save_custom
)
import os
import shutil
import logging
import numpy as np


logger = logging.getLogger(__name__)


class DeteccionListView(View):
    """Vista principal para el listado del módulo de detección"""
    def get(self, request):
        return render(request, 'core/Dashboard/Modulo Deteccion Enfermedades/deteccion_list.html')


# --------------------- FUNCIÓN DE ANÁLISIS ---------------------

def analizar_imagen(request):

    diagnostico = None
    diagnostico_numero = None
    imagenes_procesadas = []
    imagen_original = None
    recomendaciones = ""
    probabilidad = None

    if request.method == 'POST' and request.FILES.get('imagen'):
        imagen = request.FILES['imagen']
        nombre_archivo = imagen.name
        
        # Crear rutas de almacenamiento
        carpeta_temp = os.path.join(settings.MEDIA_ROOT, 'temp')
        carpeta_resultados = os.path.join(settings.MEDIA_ROOT, 'resultados')
        os.makedirs(carpeta_temp, exist_ok=True)
        os.makedirs(carpeta_resultados, exist_ok=True)
        
        ruta_temp = os.path.join(carpeta_temp, nombre_archivo)

        # Guardar imagen temporal
        try:
            with open(ruta_temp, 'wb+') as destino:
                for chunk in imagen.chunks():
                    destino.write(chunk)
            logger.info(f"Imagen guardada temporalmente: {ruta_temp}")
        except Exception as e:
            logger.error(f"Error al guardar imagen temporal: {e}")
            messages.error(request, "No se pudo guardar la imagen. Intente nuevamente.")
            return render(request, 'core/Dashboard/Modulo Deteccion/deteccion_form.html', {
                'diagnostico': diagnostico,
                'imagenes': imagenes_procesadas,
                'imagen_original': imagen_original,
                'recomendaciones': recomendaciones,
                'probabilidad': probabilidad
            })

        # Copiar imagen original a resultados
        nombre_original = f"original_{nombre_archivo}"
        ruta_original_resultado = os.path.join(carpeta_resultados, nombre_original)
        
        try:
            shutil.copy2(ruta_temp, ruta_original_resultado)
            logger.info(f"Imagen original copiada a: {ruta_original_resultado}")
        except Exception as e:
            logger.error(f"Error al copiar imagen original: {e}")

        try:
            # ========== PASO 1: PREDICCIÓN CON EL MODELO CNN ==========
            logger.info("Iniciando predicción con Custom CNN...")
            diagnostico_numero, pred_array = predict_with_custom(ruta_temp)
            
            # Obtener información del diagnóstico
            diagnostico = obtener_nombre_enfermedad_custom(diagnostico_numero)
            probabilidad_valor = np.max(pred_array)
            probabilidad = round(float(probabilidad_valor) * 100, 2)
            recomendaciones = obtener_recomendaciones_custom(diagnostico_numero)
            
            logger.info(f"Diagnóstico: {diagnostico} (clase {diagnostico_numero}) - Confianza: {probabilidad}%")

            # ========== PASO 2: SEGMENTACIÓN ADAPTATIVA ==========
            logger.info("Iniciando segmentación adaptativa...")
            paths_dict = segment_and_save_custom(
                image_path=ruta_temp,
                output_dir=carpeta_resultados,
                predicted_class=diagnostico_numero,  # Pasar la clase predicha
                adaptive=True  # Activar segmentación adaptativa
            )
            
            logger.info(f"Segmentación completada. Archivos generados: {len(paths_dict)}")

            # ========== PASO 3: PREPARAR DATOS PARA LA PLANTILLA ==========
            imagen_original = {
                "nombre": "Imagen Original",
                "url": settings.MEDIA_URL + 'resultados/' + nombre_original
            }

            imagenes_procesadas = [
                {
                    "nombre": "Contorno de la Enfermedad",
                    "url": settings.MEDIA_URL + 'resultados/' + os.path.basename(paths_dict["contorno"]),
                    "descripcion": "Áreas afectadas delimitadas con contornos"
                },
                {
                    "nombre": "Mapa de Calor (Overlay)",
                    "url": settings.MEDIA_URL + 'resultados/' + os.path.basename(paths_dict["overlay"]),
                    "descripcion": "Visualización superpuesta de las zonas afectadas"
                },
                {
                    "nombre": "Región Afectada",
                    "url": settings.MEDIA_URL + 'resultados/' + os.path.basename(paths_dict["damage"]),
                    "descripcion": "Solo las áreas con síntomas de la enfermedad"
                }
            ]

            messages.success(request, f'✅ Análisis completado correctamente. Diagnóstico: {diagnostico} ({probabilidad}% de confianza)')

        except Exception as e:
            logger.exception(f"Error durante el análisis de la imagen: {e}")
            messages.error(request, f"❌ Ocurrió un error durante el análisis: {str(e)}")
            diagnostico = "Error en el análisis"
            recomendaciones = "No se pudo generar una recomendación. Por favor, intente con otra imagen."

        finally:
            # ========== PASO 4: LIMPIEZA DE ARCHIVOS TEMPORALES ==========
            try:
                if os.path.exists(ruta_temp):
                    os.remove(ruta_temp)
                    logger.info(f"Archivo temporal eliminado: {ruta_temp}")
            except Exception as e:
                logger.warning(f"No se pudo eliminar el archivo temporal: {e}")

    # Renderizar template con los resultados
    return render(request, 'core/Dashboard/Modulo Deteccion Enfermedades/deteccion_form.html', {
        'diagnostico': diagnostico,
        'diagnostico_numero': diagnostico_numero,
        'imagenes': imagenes_procesadas,
        'imagen_original': imagen_original,
        'recomendaciones': recomendaciones,
        'probabilidad': probabilidad
    })
