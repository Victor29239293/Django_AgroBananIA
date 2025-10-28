document.addEventListener("DOMContentLoaded", function () {
  // Función para formatear probabilidades con colores dinámicos
  const probabilityCircles = document.querySelectorAll(".probability-circle");

  probabilityCircles.forEach((circle) => {
    const value = parseInt(circle.textContent);

    // Agregar efecto de pulso para probabilidades altas
    if (value >= 80) {
      circle.style.animation = "pulse 2s infinite";
    }
  });

  // Función para agregar efectos de hover mejorados
  const analysisCards = document.querySelectorAll(".analysis-card");

  analysisCards.forEach((card) => {
    card.addEventListener("mouseenter", function () {
      this.style.transform = "translateY(-8px) scale(1.02)";
    });

    card.addEventListener("mouseleave", function () {
      this.style.transform = "translateY(0) scale(1)";
    });
  });

  // Animación de entrada escalonada para las tarjetas
  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
      if (entry.isIntersecting) {
        setTimeout(() => {
          entry.target.style.opacity = "1";
          entry.target.style.transform = "translateY(0)";
        }, index * 100);
      }
    });
  });

  analysisCards.forEach((card) => {
    observer.observe(card);
  });
});

// Agregar keyframes para el pulso
const style = document.createElement("style");
style.textContent = `
  @keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
  }
`;
document.head.appendChild(style);
