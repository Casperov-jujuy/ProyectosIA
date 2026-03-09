# 🎯 CV Optimizer con IA — Formato Harvard

> Sube tu CV en PDF, indicá el puesto al que apuntás, y la IA lo reescribe y genera un nuevo PDF optimizado en formato Harvard, listo para ATS y para impresionar a reclutadores.

---

## 📌 ¿Qué hace este proyecto?

**CV Optimizer** es una aplicación web full-stack que automatiza la optimización de currículums vitae utilizando inteligencia artificial. El usuario sube su CV actual en PDF, especifica el puesto o la descripción del trabajo al que quiere aplicar, y la aplicación:

1. Extrae el texto del PDF original.
2. Envía el contenido a la IA (Google Gemini) junto con la descripción del puesto.
3. La IA reescribe el CV con lenguaje poderoso, orientado a logros, y optimizado para sistemas ATS (Applicant Tracking Systems).
4. Genera automáticamente un nuevo PDF en **formato Harvard** profesional listo para descargar.

---

## 🛠️ Herramientas y Tecnologías

### Frontend
| Herramienta | Versión | Uso |
|---|---|---|
| **Next.js** | 16.1.6 | Framework React para la interfaz web |
| **React** | 19.2.3 | Biblioteca de UI |
| **TypeScript** | ^5 | Tipado estático |
| **Tailwind CSS** | ^4 | Estilos y diseño visual |
| **Lucide React** | ^0.563.0 | Íconos SVG |

### Backend
| Herramienta | Versión | Uso |
|---|---|---|
| **Python** | 3.10+ | Lenguaje del servidor |
| **FastAPI** | latest | API REST de alto rendimiento |
| **Uvicorn** | latest | Servidor ASGI para ejecutar FastAPI |
| **Google Generative AI (Gemini)** | latest | Motor de IA para reescribir el CV |
| **pdfminer.six** | latest | Extracción de texto desde PDFs |
| **fpdf2** | latest | Generación del nuevo PDF en formato Harvard |
| **python-dotenv** | latest | Manejo de variables de entorno |
| **python-multipart** | latest | Soporte para subida de archivos |

---

## 📁 Estructura del Proyecto

```
CvsArmado/
├── backend/
│   ├── main.py              # API FastAPI + lógica de IA + generador de PDF
│   ├── requirements.txt     # Dependencias Python
│   ├── .env                 # Variables de entorno (GEMINI_API_KEY)
│   └── .env.example         # Ejemplo de configuración
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Página principal de la aplicación
│   │   ├── layout.tsx       # Layout global
│   │   └── globals.css      # Estilos globales
│   ├── package.json         # Dependencias Node.js
│   └── next.config.ts       # Configuración de Next.js
└── start_project.bat        # Script para iniciar ambos servidores (Windows)
```

---

## ⚙️ Cómo funciona — Paso a Paso

### Flujo técnico

```
Usuario sube PDF + descripción del puesto
        │
        ▼
[Frontend Next.js]
  Envía formulario multipart/form-data
        │
        ▼
[Backend FastAPI — POST /api/optimize]
  1. Extrae texto del PDF con pdfminer
  2. Arma el prompt para Gemini
        │
        ▼
[Google Gemini 2.5 Flash]
  Reescribe el CV y devuelve JSON estructurado
  con: nombre, resumen, educación, skills,
       experiencia, carta de presentación, referencias
        │
        ▼
[Backend — Generador PDF]
  Construye el PDF A4 con formato Harvard
  usando fpdf2 (fuente Times, márgenes, secciones)
        │
        ▼
[Frontend]
  Descarga automática del PDF optimizado
```

### Estructura del JSON que genera la IA

La IA devuelve un JSON con el siguiente esquema, que luego se usa para armar el PDF:

```json
{
  "name": "Nombre Completo",
  "job_title": "Título del Puesto",
  "contact_info": "Email | Teléfono | LinkedIn | Portfolio",
  "summary": "Resumen profesional de 3-4 oraciones optimizado para ATS.",
  "education": [...],
  "skills": { "Categoría": "Skill A, Skill B" },
  "experience": [...],
  "cover_letter": { ... },
  "references": [...]
}
```

---

## 🚀 Instalación y Configuración

### 1. Clonar el repositorio

```bash
git clone <URL-del-repositorio>
cd CvsArmado
```

### 2. Configurar el Backend (Python)

```bash
cd backend

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

Crear el archivo `.env` dentro de la carpeta `backend/`:

```env
GEMINI_API_KEY=tu_clave_de_api_de_google_gemini
```

> Podés obtener tu clave gratuita en [Google AI Studio](https://aistudio.google.com/apikey).

### 3. Configurar el Frontend (Node.js)

```bash
cd frontend

# Instalar dependencias
npm install
```

### 4. Iniciar el proyecto

#### Opción A — Script automático (Windows)
Hacé doble clic en `start_project.bat` en la raíz del proyecto. Este script levanta el backend y el frontend automáticamente.

#### Opción B — Inicio manual

En una terminal (backend):
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

En otra terminal (frontend):
```bash
cd frontend
npm run dev
```

### 5. Abrir la aplicación

Abrí tu navegador en: **[http://localhost:3000](http://localhost:3000)**

---

## 🧠 ¿Cómo usarlo?

1. **Subí tu CV** en formato PDF usando el botón de carga.
2. **Escribí la descripción del puesto** o el título del trabajo al que querés aplicar (puede ser el texto completo del aviso laboral).
3. Hacé clic en **"Optimizar CV"**.
4. Esperá unos segundos mientras la IA procesa tu CV.
5. El PDF optimizado en formato Harvard **se descargará automáticamente**.

---

## 📄 Sobre el Formato Harvard

El PDF generado sigue el estándar **Harvard CV**, caracterizado por:

- Tipografía **Times New Roman** clásica y elegante.
- Nombre centrado en la parte superior con jerarquía visual clara.
- Secciones bien definidas: Resumen, Educación, Habilidades, Experiencia, Carta de Presentación y Referencias.
- Habilidades organizadas en **dos columnas por categoría**.
- Numeración de páginas automática.
- Carta de presentación incluida en una página separada.

---

## 🔑 Variables de Entorno

| Variable | Descripción | Requerida |
|---|---|---|
| `GEMINI_API_KEY` | Clave de API de Google Gemini | ✅ Sí |

---

## 📦 Dependencias principales

### Backend (`requirements.txt`)
```
fastapi
uvicorn
python-multipart
google-genai
pdfminer.six
fpdf2
python-dotenv
```

### Frontend (`package.json`)
```
next, react, react-dom, lucide-react
tailwindcss, typescript
```

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abrí un Issue antes de enviar un Pull Request para discutir los cambios propuestos.

---

## 📝 Licencia

Este proyecto es de uso personal/educativo. Consultá al autor para otros usos.
