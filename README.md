# 🌌 Mundos Simulados — Laboratorio de Computación Visual

> **Plataforma interactiva de divulgación científica, física computacional y simulación de sistemas dinámicos en el navegador.**

🌐 **Sitio Web Oficial:** [mundossimulados.online](https://mundossimulados.online)

![HTML5](https://img.shields.io/badge/HTML5-Canvas%20%2F%20WebGL-E34F26?style=flat-square&logo=html5&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)
![Domain](https://img.shields.io/badge/Domain-Física%20%26%20Computación%20Visual-6366F1?style=flat-square)

---

## 🔬 Visión del Proyecto

**Mundos Simulados** es un entorno experimental que traduce ecuaciones diferenciales y leyes de la física clásica en simulaciones visuales interactivas accesibles directamente desde el navegador web, sin requerir instalaciones complejas.

Diseñado tanto para la docencia como para la curiosidad científica, permite a los usuarios alterar constantes físicas (gravedad, fricción, masa, carga eléctrica) y observar el comportamiento emergente de sistemas complejos.

---

## 🧪 Simulaciones Disponibles

1. **Sistemas Gravitacionales de N Cuerpos:**
   - Órbitas planetarias y perturbaciones gravitacionales bajo la ley de gravitación universal de Newton.
   - Integración numérica mediante métodos Verlet / Runge-Kutta de 4to orden para preservar la energía del sistema.
2. **Péndulos Dobles y Sistemas Caóticos:**
   - Visualización de la extrema sensibilidad a las condiciones iniciales (Efecto Mariposa).
   - Generación de trayectorias de fase y mapas de Poincaré.
3. **Mecánica de Partículas y Colisiones:**
   - Conservación del momento lineal y colisiones elásticas/inelásticas en dos dimensiones.
   - Simulación de gases ideales y distribución de velocidades de Maxwell-Boltzmann.
4. **Campos Electrostáticos y Líneas de Fuerza:**
   - Cálculo del potencial eléctrico y renderizado dinámico de líneas de campo para distribuciones de carga discretas.

---

## 💻 Arquitectura de Simulación

- **Bucle de Simulación de Paso Fijo (Fixed Timestep Loop):** Garantiza estabilidad numérica independiente de la tasa de refresco de la pantalla (evita problemas de tunneling a bajos FPS).
- **Renderizado por Capas:** Separación del lienzo de cálculo físico del lienzo de dibujado de estelas y partículas.
- **Diseño Responsive y Minimalista:** Interfaz fluida adaptable a dispositivos móviles y pantallas de escritorio.

---

## 🛠️ Ejecución Local

```bash
# 1. Clonar el repositorio
git clone https://github.com/juanxaviercasa/mundos-simulados.git
cd mundos-simulados

# 2. Servir con cualquier servidor HTTP local
python -m http.server 8080
# o bien: npx serve .
```

Abre `http://localhost:8080` en tu navegador para interactuar con las simulaciones.

---

## 👨‍💻 Autor

**Juan Xavier Cabello** — Educador Matemático, Diseñador de Productos Digitales y Desarrollador Web Full-Stack.  
[LinkedIn](https://www.linkedin.com/in/xaviercabello/) · [GitHub](https://github.com/juanxaviercasa)
