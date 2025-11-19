# Agente para automatización de búsqueda de repuestos

## 📋 Descripción

Sistema inteligente basado en **LangGraph** y **Groq** que automatiza la búsqueda, ranking y pedido de repuestos para una empresa distribuidora.

---

## 🚀 Instalación

### 1. Requisitos previos
- Python 3.10 o superior
- pip actualizado

### 2. Clonar el repositorio
```bash
git clone https://github.com/MartinVazquez1982/agente-repuestos-duia.git
cd agente-repuestos-duia
```

### 3. Crear entorno virtual (recomendado)
```bash
# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\Activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Configurar API Key de Groq
Crear un archivo `.env` en la raíz del proyecto con tu API key:

```env
GROQ_API_KEY=tu_clave_de_groq_aqui
```

> 💡 **Obtener API Key:** Regístrate en [console.groq.com](https://console.groq.com) y crea una nueva API key gratuita.

---

## 📓 Uso

### Ejecutar el notebook principal
```bash
# Abrir con Jupyter
jupyter notebook agente_repuestos.ipynb

# O con VS Code
code agente_repuestos.ipynb
```

### Estructura del proyecto
```
agente-repuestos-duia/
├── agente_repuestos.ipynb      # Notebook principal del TP
├── requirements.txt            # Dependencias
├── .env.example                # Template de variables de entorno
├── .env                        # Variables de entorno
└── README.md                   # Este archivo
```

---

## 🛠️ Dependencias principales

| Paquete | Versión | Propósito |
|---------|---------|-----------|
| `langchain` | 1.0.8 | Framework para LLMs |
| `langgraph` | 1.0.3 | Orquestación de agentes |
| `langchain-groq` | 1.0.1 | Integración con Groq |
| `python-dotenv` | - | Gestión de variables de entorno |

---

## 👥 Autores

- **David Burckhardt**
- **Martin Vazquez Arispe**
- **Martin Caballero**