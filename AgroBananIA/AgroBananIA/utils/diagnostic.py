import os
import logging
import traceback
import numpy as np
import cv2
import uuid
from django.conf import settings
import tensorflow as tf
from keras import preprocessing, models


logger = logging.getLogger(__name__)


MODEL_DIR = os.path.join(settings.BASE_DIR, 'static', 'models')


class_mapping = {
    0: "Banana Black Sigatoka Disease",
    1: "Banana Healthy Leaf",
    2: "Banana Insect Pest Disease",
    3: "Banana Moko Disease",
    4: "Banana Panama Disease",
    5: "Banana Yellow Sigatoka Disease",
}

# Rangos HSV optimizados por enfermedad
# Formato: (lower_bound, upper_bound)
color_ranges_by_disease = {
    0: ([0, 0, 0], [180, 255, 100]),           # Black Sigatoka: zonas oscuras/necróticas (marrón-negro)
    1: ([35, 40, 40], [85, 255, 255]),         # Healthy Leaf: verde saludable (no debería segmentar mucho)
    2: ([0, 50, 50], [15, 255, 255]),          # Insect Pest: áreas rojizas, marrones claras
    3: ([15, 60, 60], [35, 255, 230]),         # Moko: amarillo-verdoso con manchas marrones
    4: ([18, 70, 50], [30, 255, 200]),         # Panama: amarillo-marrón en márgenes de hojas
    5: ([20, 100, 100], [35, 255, 255]),       # Yellow Sigatoka: amarillo brillante con centro marrón
}

recomendaciones_mapping = {
    0: "Retirar y destruir hojas gravemente afectadas. Aplicar fungicidas sistémicos (como triazoles) y de contacto (como clorotalonil o mancozeb) de forma alternada. Mejorar la ventilación y drenaje del cultivo para reducir la humedad.",
    1: "La planta está sana. Continuar con buenas prácticas de manejo agronómico, monitoreo periódico de plagas y enfermedades, y fertilización balanceada.",
    2: "Identificar el tipo de plaga presente. Aplicar insecticidas específicos (por ejemplo, piretroides o neonicotinoides) según el nivel de infestación. Implementar prácticas de manejo integrado de plagas (MIP) y mejorar la sanidad del entorno.",
    3: "Eliminar completamente las plantas infectadas, incluyendo rizomas. Evitar herramientas contaminadas y el uso de agua de riego contaminada. Implementar rotación de cultivos y desinfección de suelos si es posible.",
    4: "Eliminar y destruir plantas afectadas. Implementar cuarentena para evitar la propagación. Asegurar un buen drenaje y evitar el estrés hídrico en las plantas. Utilizar variedades resistentes si están disponibles.",
    5: "Aplicar fungicidas preventivos y curativos (como estrobilurinas o ditiocarbamatos). Mantener el cultivo bien aireado mediante podas sanitarias. Realizar monitoreos constantes para detectar síntomas tempranos.",
}


def load_custom_model():
    model_path = os.path.join(MODEL_DIR, 'best_custom_cnn_improved.keras')
    try:
        model = models.load_model(model_path, compile=False)
        logger.info(f"Modelo Custom CNN cargado correctamente: {model_path}")
        return model
    except Exception as e:
        logger.error(f"Error al cargar Custom CNN: {e}")
        logger.debug(traceback.format_exc())
        return None


model_custom = load_custom_model()


def preprocess_image_custom(image_path, target_size=(128, 128)):
    img = preprocessing.image.load_img(image_path, target_size=target_size)
    img_array = preprocessing.image.img_to_array(img) / 255.0
    return np.expand_dims(img_array, axis=0)


def predict_with_custom(image_path):
    if model_custom is None:
        raise RuntimeError("El modelo Custom CNN no está cargado correctamente.")
    img = preprocess_image_custom(image_path)
    try:
        pred = model_custom.predict(img)
        pred = np.squeeze(pred)
        if pred.ndim == 1:
            pred = np.expand_dims(pred, axis=0)
        pred_class = int(np.argmax(pred, axis=1)[0])
        return pred_class, pred
    except Exception as e:
        logger.exception("Error durante la predicción con Custom CNN: %s", e)
        raise RuntimeError("Error al predecir con el modelo Custom CNN.")


def segment_and_save_custom(image_path, output_dir, predicted_class=None, adaptive=True):
    os.makedirs(output_dir, exist_ok=True)
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"No se pudo cargar la imagen: {image_path}")
    
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_hsv = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2HSV)
    
    # Seleccionar rango de color según la enfermedad predicha
    if adaptive and predicted_class is not None and predicted_class in color_ranges_by_disease:
        lower_bound, upper_bound = color_ranges_by_disease[predicted_class]
        lower = np.array(lower_bound)
        upper = np.array(upper_bound)
        disease_name = class_mapping.get(predicted_class, "Desconocida")
        logger.info(f"Segmentación adaptativa para: {disease_name} (clase {predicted_class})")
        logger.debug(f"Rango HSV: {lower} - {upper}")
    else:
        # Rango por defecto (zonas oscuras - Black Sigatoka)
        lower = np.array([0, 0, 0])
        upper = np.array([180, 255, 100])
        logger.info("Usando segmentación por defecto (zonas oscuras)")
    
    # Crear máscara
    mask = cv2.inRange(img_hsv, lower, upper)
    
    # Operaciones morfológicas adaptativas
    if predicted_class in [0, 5]:  # Sigatokas: lesiones alargadas
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    elif predicted_class in [3, 4]:  # Moko, Panama: manchas irregulares
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    else: 
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    min_area = 100  
    mask_filtered = np.zeros_like(mask)
    for contour in contours:
        if cv2.contourArea(contour) > min_area:
            cv2.drawContours(mask_filtered, [contour], -1, 255, -1)

    contoured = img_rgb.copy()
    cv2.drawContours(contoured, contours, -1, (255, 0, 0), 2)

    heatmap = np.zeros_like(img_rgb)
    heatmap[:, :, 0] = mask_filtered  
    overlay = cv2.addWeighted(img_rgb, 0.7, heatmap, 0.5, 0)

    only_damage = cv2.bitwise_and(img_rgb, img_rgb, mask=mask_filtered)
    
    uid = uuid.uuid4().hex
    paths = {
        "contorno": os.path.join(output_dir, f"{uid}_contour.jpg"),
        "overlay": os.path.join(output_dir, f"{uid}_overlay.jpg"),
        "damage": os.path.join(output_dir, f"{uid}_damage.jpg"),
    }
    
    cv2.imwrite(paths["contorno"], cv2.cvtColor(contoured, cv2.COLOR_RGB2BGR))
    cv2.imwrite(paths["overlay"], cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    cv2.imwrite(paths["damage"], cv2.cvtColor(only_damage, cv2.COLOR_RGB2BGR))
    
    logger.info(f"Segmentación completada. Archivos guardados en: {output_dir}")
    return paths


def obtener_nombre_enfermedad_custom(diagnostico):
    if diagnostico is None:
        return "Enfermedad desconocida"
    key = diagnostico
    try:
        key = int(diagnostico)
    except Exception:
        pass

    nombre = class_mapping.get(key)
    if nombre is None:
        logger.warning("Clave de diagnóstico no encontrada en class_mapping: %s", diagnostico)
        return "Enfermedad desconocida"
    return nombre


def obtener_recomendaciones_custom(diagnostico):
    if diagnostico is None:
        return "Recomendación no disponible para este diagnóstico."

    key = diagnostico
    try:
        key = int(diagnostico)
    except Exception:
        pass

    return recomendaciones_mapping.get(key, "Recomendaciones no disponibles.")
