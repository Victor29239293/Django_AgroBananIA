// Variables globales
const dropZone = document.getElementById("dropZone");
const imageInput = document.getElementById("imageInput");
const previewContainer = document.getElementById("previewContainer");
const previewImg = document.getElementById("previewImg");
const fileLabel = document.getElementById("fileLabel");
const fileInfo = document.getElementById("fileInfo");
const uploadForm = document.getElementById("uploadForm");
const loadingOverlay = document.getElementById("loadingOverlay");
const submitBtn = document.getElementById("submitBtn");
const alertContainer = document.getElementById("alertContainer");

// Función para mostrar alertas
function showAlert(message, type = "error") {
  const alert = document.createElement("div");
  alert.className = `alert alert-${type}`;
  alert.innerHTML = `
      <strong>${
        type === "error" ? "❌ Error:" : "✅ Éxito:"
      }</strong> ${message}
      <button onclick="this.parentElement.remove()" style="float: right; background: none; border: none; font-size: 18px; cursor: pointer;">×</button>
    `;
  alertContainer.appendChild(alert);
  setTimeout(() => {
    if (alert.parentElement) alert.remove();
  }, 5000);
}

// Drag and Drop
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const files = e.dataTransfer.files;
  if (files.length > 0) {
    imageInput.files = files;
    previewImage();
  }
});

// Validación de archivos
function validateFile(file) {
  if (!file.type.match("image/(jpeg|png|jpg)")) {
    showAlert("Por favor selecciona solo archivos JPG, PNG o JPEG");
    return false;
  }
  if (file.size > 10 * 1024 * 1024) {
    showAlert("El archivo es demasiado grande. Tamaño máximo: 10MB");
    return false;
  }
  return true;
}

// Vista previa de la imagen
function previewImage() {
  const file = imageInput.files[0];
  if (!file) {
    removePreview();
    return;
  }

  if (!validateFile(file)) {
    imageInput.value = "";
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    previewContainer.style.display = "block";
    dropZone.classList.add("has-file");
    fileLabel.textContent = "Imagen lista para analizar";

    const fileSize = (file.size / (1024 * 1024)).toFixed(2);
    const lastModified = new Date(file.lastModified).toLocaleDateString();
    fileInfo.innerHTML = `
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; text-align: left;">
          <div><strong>Archivo:</strong> ${file.name}</div>
          <div><strong>Tamaño:</strong> ${fileSize} MB</div>
          <div><strong>Tipo:</strong> ${file.type}</div>
          <div><strong>Modificado:</strong> ${lastModified}</div>
        </div>
      `;

    submitBtn.disabled = false;
    submitBtn.style.background = "#27ae60";
    showAlert("Imagen cargada correctamente", "success");
  };
  reader.onerror = () => {
    showAlert("Error al cargar la imagen");
    removePreview();
  };
  reader.readAsDataURL(file);
}

// Remover vista previa
function removePreview() {
  imageInput.value = "";
  previewImg.src = "";
  previewContainer.style.display = "none";
  dropZone.classList.remove("has-file");
  fileLabel.textContent =
    "Arrastra una imagen aquí o haz clic para seleccionar";
  fileInfo.innerHTML = "";
  submitBtn.disabled = true;
  submitBtn.style.background = "#95a5a6";
}

// Evento de cambio en input
imageInput.addEventListener("change", previewImage);

// Manejo del formulario
uploadForm.addEventListener("submit", (e) => {
  if (!imageInput.files.length) {
    e.preventDefault();
    showAlert("Por favor selecciona una imagen");
    return;
  }
  loadingOverlay.style.display = "flex";
  submitBtn.disabled = true;

  // Animación de progreso
  let progress = 0;
  const progressFill = document.querySelector(".progress-fill");
  const interval = setInterval(() => {
    progress += Math.random() * 15;
    if (progress >= 90) {
      clearInterval(interval);
    }
    progressFill.style.width = Math.min(progress, 90) + "%";
  }, 300);
});

// Funciones del modal
function openImageModal(imageUrl, imageName) {
  const modal = document.getElementById("imageModal");
  const modalImg = document.getElementById("modalImg");
  const modalCaption = document.getElementById("modalCaption");
  modal.style.display = "block";
  modalImg.src = imageUrl;
  modalCaption.textContent = imageName;
}

function closeImageModal() {
  document.getElementById("imageModal").style.display = "none";
}

// Cerrar modal con ESC
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape") closeImageModal();
});

// Prevenir cierre del modal al hacer clic en la imagen
document.querySelector(".modal-content").addEventListener("click", (e) => {
  e.stopPropagation();
});

// Inicialización
document.addEventListener("DOMContentLoaded", () => {
  submitBtn.disabled = true;
  submitBtn.style.background = "#95a5a6";

  // Configuración para móviles
  const isMobile = /Mobi|Android/i.test(navigator.userAgent);
  if (isMobile) {
    imageInput.setAttribute("capture", "camera");
  } else {
    imageInput.removeAttribute("capture");
  }
});

// Formatear bytes
function formatBytes(bytes, decimals = 2) {
  if (!bytes) return "0 Bytes";
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}
