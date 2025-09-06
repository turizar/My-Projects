// Toggle menú para móviles
const toggle = document.getElementById("menuToggle");
const nav = document.getElementById("nav").querySelector("ul");

toggle.addEventListener("click", () => {
  nav.classList.toggle("show");
});




// Carrousel
let currentSlide = 0;
const slides = document.querySelectorAll('.hero-slide');
const prevBtn = document.getElementById('prevSlide');
const nextBtn = document.getElementById('nextSlide');

let autoSlideInterval;
const slideIntervalTime = 5000; // 5 segundos

function showSlide(index) {
  slides.forEach((slide, i) => {
    slide.classList.remove('active');
    if (i === index) slide.classList.add('active');
  });
}

function nextSlide() {
  currentSlide = (currentSlide + 1) % slides.length;
  showSlide(currentSlide);
}

function prevSlide() {
  currentSlide = (currentSlide - 1 + slides.length) % slides.length;
  showSlide(currentSlide);
}

function resetAutoSlide() {
  clearInterval(autoSlideInterval);
  autoSlideInterval = setInterval(nextSlide, slideIntervalTime);
}

// Event listeners
nextBtn.addEventListener('click', () => {
  nextSlide();
  resetAutoSlide();
});

prevBtn.addEventListener('click', () => {
  prevSlide();
  resetAutoSlide();
});

// Inicializar
showSlide(currentSlide);
autoSlideInterval = setInterval(nextSlide, slideIntervalTime);


const cabinData = [
  {
    "name": "Cabaña Familiar 0",
    "capacity": 4,
    "description": "Ideal para familias con niños.",
    "image": "images/cabin 0 - living room.jpg",
    "link": "cabin0.html"
  },
  {
    "name": "Cabaña Familiar 1",
    "capacity": 8,
    "description": "Primera línea de playa, ideal para adultos mayores.",
    "image": "images/cabin 1 - living room.jpg",
    "link": "cabin1.html"
  },
  {
    "name": "Cabaña Familiar 2",
    "capacity": 6,
    "description": "Comodidad y funcionalidad garantizadas.",
    "image": "images/cabin 2 - living room.jpg",
    "link": "cabin2.html"
  },
  {
    "name": "Cabaña Familiar 3",
    "capacity": 7,
    "description": "Ideal para grupos grandes o familias extensas.",
    "image": "images/cabin 3 - living room kitchen.jpg",
    "link": "cabin3.html"
  },
  {
    "name": "Cabaña Familiar 4",
    "capacity": 7,
    "description": "La mejor vista al mar desde el segundo piso.",
    "image": "images/cabin 4 - living room.jpg",
    "link": "cabin4.html"
  },
  {
    "name": "Cabaña Familiar 6",
    "capacity": 2,
    "description": "Vista panorámica de 180° al océano.",
    "image": "images/cabin 6 - terrace.jpg",
    "link": "cabin6.html"
  }
];

// Call Icon
document.addEventListener('DOMContentLoaded', () => {
  const callButtons = document.querySelector('.call-buttons');
  const primaryCall = document.querySelector('.primary-call');
  let expanded = false;

  // Ocultar secundario al inicio
  callButtons.classList.remove('expanded');

  primaryCall.addEventListener('click', (e) => {
    if (!expanded) {
      e.preventDefault();
      callButtons.classList.add('expanded');
      expanded = true;
    }
    // Si ya está expandido, se permite la llamada
  });
});


// Despliegue Imagenes Servicios
document.addEventListener("DOMContentLoaded", function () {
  const serviceItems = document.querySelectorAll(".features li");
  const lightbox = document.getElementById("lightbox");
  const carouselImage = document.getElementById("carousel-image");
  const closeBtn = document.getElementById("close-lightbox");
  const prevBtn = document.querySelector(".nav.prev");
  const nextBtn = document.querySelector(".nav.next");

  let images = [];
  let currentIndex = 0;

  // Mostrar imagen actual del carrusel
  function showImage() {
    if (images.length > 0) {
      carouselImage.src = images[currentIndex];
    }
  }

  // Abrir lightbox al hacer clic en un ítem
  serviceItems.forEach(item => {
    item.addEventListener("click", () => {
      const dataImages = item.getAttribute("data-images");
      if (dataImages) {
        images = dataImages.split(",");
        currentIndex = 0;
        showImage();
        lightbox.classList.remove("hidden");
      }
    });
  });

  // Navegar a imagen anterior
  prevBtn.addEventListener("click", () => {
    currentIndex = (currentIndex - 1 + images.length) % images.length;
    showImage();
  });

  // Navegar a imagen siguiente
  nextBtn.addEventListener("click", () => {
    currentIndex = (currentIndex + 1) % images.length;
    showImage();
  });

  // Cerrar lightbox con botón
  closeBtn.addEventListener("click", () => {
    lightbox.classList.add("hidden");
  });

  // Cerrar lightbox con tecla Escape
  document.addEventListener("keydown", (e) => {
    if (lightbox.classList.contains("hidden")) return;

    if (e.key === "Escape") {
      lightbox.classList.add("hidden");
    } else if (e.key === "ArrowRight") {
      currentIndex = (currentIndex + 1) % images.length;
      showImage();
    } else if (e.key === "ArrowLeft") {
      currentIndex = (currentIndex - 1 + images.length) % images.length;
      showImage();
    }
  });
});



// Aquí se podrían agregar funciones que manipulen el DOM para mostrar los datos de las cabañas dinámicamente


