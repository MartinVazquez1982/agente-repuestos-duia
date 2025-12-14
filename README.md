# Sistema Inteligente de Gestión de Repuestos

## Descripción General

Sistema de automatización basado en **LangGraph** y **LLMs** que optimiza el proceso de búsqueda, ranking y gestión de pedidos de repuestos industriales. El sistema integra búsqueda semántica vectorial, toma de decisiones inteligente y flujo conversacional para asistir a usuarios en la selección óptima de repuestos de inventarios internos y proveedores externos.

---

## Arquitectura y Estrategia

### Enfoque Técnico

El sistema implementa una arquitectura basada en **grafos de estado** (LangGraph) que permite:

1. **Flujo conversacional flexible**: El agente puede manejar múltiples iteraciones con el usuario, solicitando información faltante o clarificaciones.

2. **Búsqueda semántica híbrida**: Combina búsqueda vectorial (embeddings) con búsqueda exacta por código, permitiendo encontrar productos similares incluso con descripciones imprecisas.

3. **Ranking inteligente multi-criterio**: Utiliza LLM para evaluar opciones considerando precio, disponibilidad, lead time, rating de proveedores y tipo de producto (interno/externo).

4. **Human-in-the-Loop**: Implementa puntos de interrupción estratégicos donde el usuario revisa y confirma opciones antes de procesar pedidos.

5. **Gestión de estado persistente**: Usa checkpointing para mantener conversaciones multi-turno y recuperar el contexto en cualquier punto.

### Arquitectura del Grafo

![Texto Alternativo](diagram.png)

### Componentes Principales

#### 1. Nodos de Procesamiento

- **`validation`**: Clasifica la intención del usuario (pedido vs consulta general)
- **`extract_products_info`**: Extrae productos con LLM usando salida estructurada
- **`check_product_info_completeness`**: Valida si cada producto tiene información suficiente
- **`semantic_search_internal/external`**: Búsqueda vectorial en MongoDB Atlas
- **`check_stock_availability`**: Verifica disponibilidad vs cantidad solicitada
- **`generate_ranking`**: Genera ranking con LLM considerando múltiples criterios
- **`human_in_the_loop_selection`**: Presenta opciones y espera selección del usuario
- **`process_user_selection`**: Interpreta selección con LLM y valida códigos
- **`process_order`**: Genera resumen detallado de la orden
- **`schedule_delivery`**: Calcula fechas y genera confirmación final

#### 2. Chains (Cadenas LLM)

Implementadas con patrón Singleton en `ChainAdministrator`:

- **`extraction_chain`**: Extracción estructurada de productos (Pydantic)
- **`validation_chain`**: Clasificación de intención
- **`verify_product_chain`**: Verificación de completitud de información
- **`ranking_chain`**: Generación de ranking multi-criterio
- **`selection_interpretation_chain`**: Interpretación de selección del usuario
- **`no_stock_chain`**: Generación de mensaje cuando no hay stock
- **`interpret_no_stock_response_chain`**: Interpretación de respuesta sin stock

#### 3. Base de Datos

**MongoDB Atlas** con:
- **Búsqueda vectorial**: Índice `vector_index_repuestos` para similitud semántica
- **Embeddings**: Generados con `sentence-transformers/all-MiniLM-L6-v2`
- **Schema**: Campos de producto, proveedor, stock, precios y metadatos

#### 4. Routing Condicional

Decisiones inteligentes basadas en el estado:
- `route_classification`: Pedido vs consulta
- `route_after_extraction_check`: ¿Info completa?
- `need_external_search`: ¿Buscar en externos?
- `route_after_stock_check`: ¿Hay stock disponible?
- `route_by_product_type`: Interno/Externo/Mixto
- `route_after_selection`: Procesar vs cancelar

---

## Instalación

### Requisitos Previos

- Python 3.10+
- MongoDB Atlas (cuenta gratuita)
- API Key de Groq (gratuita)

### Configuración Paso a Paso

**1. Clonar el repositorio**
```bash
git clone https://github.com/MartinVazquez1982/agente-repuestos-duia.git
cd agente-repuestos-duia
```

**2. Crear entorno virtual**
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno**

Crear archivo `.env` en la raíz:
```env
GROQ_API_KEY=tu_api_key_de_groq
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/
```

Obtener credenciales o utilizar las que se encuentran en el mensaje de la entrega:
- **Groq API**: [console.groq.com](https://console.groq.com)
- **MongoDB Atlas**: [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)

**5. Cargar datos a MongoDB**
```bash
python load_data_to_mongo.py
```

Este script:
- Lee `repuestos.csv`
- Genera embeddings con `sentence-transformers`
- Carga documentos a MongoDB Atlas
- Crea índice vectorial automáticamente

---

### Alternativa (Docker)

El proyecto cuenta con un dockerfile para que sea posible ejecutarlo desde un contenedor para no depender de compatibilidad con el SO. Para ellos continuar con los siguientes pasos:

**1. Creación de la imagen (Demora varios minutos)**
```bash
docker build -t "nombre para imagen" .
```

**2. Ejecutar el contenedor**
```bash
docker run -it "nombre para imagen"
```

Es importante que no utilicen la opción `-d` dado que ejecuta el contenedor en segundo plano y la opción se utiliza `-it` para poder utilizar la consola dado que es la fomrma de interactuar con el agente.

## Uso del Sistema

### Modo CLI (Command Line)

```bash
python main.py
```

**Flujo de ejemplo:**

```
Usuario: "Necesito 25 rodamientos SKF 6204-2RS y una cámara termográfica FLIR E8-XT"

[Agente extrae productos y verifica información]
[Realiza búsqueda semántica en inventario interno]
[Si stock insuficiente, busca en proveedores externos]
[Genera ranking considerando precio, disponibilidad, lead time]

Agente: "Encontré las siguientes opciones:

PRODUCTO 1: Rodamiento SKF 6204-2RS (25 unidades)
  Opción 1 (Interno): R-0101 - Stock: 30/25 ✓
  Opción 2 (Externo): R-0101 - Proveedor XYZ - Lead time: 5 días

PRODUCTO 2: Cámara termográfica FLIR E8-XT
  Opción 1 (Externo): R-0532 - Proveedor ABC - Lead time: 7 días

¿Qué opciones deseas ordenar? Responde con los códigos."

Usuario: "R-0101 y R-0532"

[Agente procesa selección y genera orden]
[Separa productos internos y externos]
[Calcula tiempos de entrega y costos]
```

### Modo Notebook

```bash
jupyter notebook notebooks/agente_repuestos.ipynb
```

Permite ejecución interactiva celda por celda para debugging y análisis.

---

## Estructura del Proyecto

```
agente-repuestos-duia/
├── agent.py                          # Definición del grafo LangGraph
├── main.py                           # Punto de entrada CLI
├── utils.py                          # Funciones auxiliares
├── load_data_to_mongo.py            # Script de carga de datos
├── repuestos.csv                     # Dataset de repuestos
├── requirements.txt                  # Dependencias Python
├── .env                              # Variables de entorno
│
├── nodes/                            # Nodos del grafo
│   ├── extract_products_info.py
│   ├── check_product_info_completeness.py
│   ├── semantic_search.py
│   ├── generate_ranking.py
│   ├── validation.py
│   ├── human_in_the_loop_selection.py
│   ├── process_user_selection.py
│   ├── process_order.py
│   ├── process_internal_order.py
│   ├── generate_external_email.py
│   ├── process_both_type.py
│   ├── schedule_delivery.py
│   ├── check_stock_availability.py
│   ├── handle_no_stock_response.py
│   └── request_new_products.py
│
├── routes/                           # Funciones de routing condicional
│   └── routes.py
│
├── chains/                           # Chains LLM
│   ├── chain_administrator.py        # Singleton de chains
│   └── chain_generator/
│       ├── identify_product_chain.py
│       ├── validation_chain.py
│       ├── verify_product_chain.py
│       ├── ranking_chain.py
│       ├── selection_interpretation_chain.py
│       ├── no_stock_chain.py
│       └── interpret_no_stock_response_chain.py
│
├── schemas/                          # Schemas Pydantic
│   ├── state.py                      # AgentState (estado del grafo)
│   ├── repuesto.py                   # Schema de repuesto
│   └── structure_outputs.py         # Outputs estructurados
│
├── db/                               # Gestión de base de datos
│   └── mongo.py                      # Singleton de MongoDB
│
├── system_prompts/                   # Templates de prompts del sistema
│   ├── identify_products.txt
│   ├── intention_classifier_prompt.txt
│   ├── no_stock_prompt.txt
│   ├── reranking_prompt.txt
│   └── interpret_no_stock_response_prompt.txt
│
└── notebooks/                        # Notebooks Jupyter
    └── agente_repuestos.ipynb
```

---

## Tecnologías Utilizadas

| Tecnología | Versión | Propósito |
|-----------|---------|-----------|
| **LangChain** | 1.0.8 | Framework para aplicaciones LLM |
| **LangGraph** | 1.0.3 | Orquestación de agentes con grafos de estado |
| **Groq** | 1.0.1 | Inferencia LLM de alta velocidad |
| **MongoDB Atlas** | 4.10.1 | Base de datos con búsqueda vectorial |
| **Sentence Transformers** | 3.3.0 | Generación de embeddings semánticos |
| **Pydantic** | 2.12.4 | Validación de datos y schemas |
| **Python-dotenv** | 1.2.1 | Gestión de variables de entorno |

### Modelo LLM

- **Modelo**: `openai/gpt-oss-120b` (vía Groq)
- **Temperature**: 0.1 (respuestas determinísticas)
- **Velocidad**: ~500 tokens/segundo (inference optimizada)

### Modelo de Embeddings

- **Modelo**: `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensión**: 384
- **Propósito**: Búsqueda semántica por similitud coseno

---

## Características Avanzadas

### 1. Búsqueda Semántica Inteligente

- **Tolerancia a errores**: Encuentra productos incluso con descripciones imprecisas
- **Búsqueda híbrida**: Combina vectorial (semántica) y exacta (por código)
- **Score threshold**: Filtra resultados con similitud < 0.5

### 2. Gestión de Stock Dinámica

- **Verificación por cantidad**: Compara stock disponible vs solicitado
- **Cascada interna-externa**: Busca externamente si stock insuficiente
- **Opciones mixtas**: Muestra internos (parciales) + externos

### 3. Human-in-the-Loop Estratégico

- **Interrupciones controladas**: Pausas en puntos críticos de decisión
- **Validación de selección**: Interpreta respuesta del usuario con LLM
- **Manejo de errores**: Re-pregunta si selección inválida

### 4. Checkpointing y Persistencia

- **Estado recuperable**: Cada nodo actualiza el estado persistente
- **Multi-turno**: Soporta conversaciones largas sin perder contexto
- **Thread ID**: Identifica sesiones únicas de usuario

---

## Casos de Uso

En el archivo `agente_prompt_prueba.txt` cuenta con 5 casos de prueba para el agente

---

## Patrones de Diseño Implementados

### 1. Singleton Pattern

**Aplicado en**:
- `ChainAdministrator`: Única instancia de chains LLM
- `MongoCollectionManager`: Única conexión a MongoDB

**Beneficio**: Evita re-inicialización costosa de modelos y conexiones.

### 2. State Machine Pattern

**Aplicado en**: LangGraph (grafo de estados)

**Beneficio**: Flujo claro y predecible con transiciones explícitas.

### 3. Chain of Responsibility

**Aplicado en**: Cadenas de LangChain

**Beneficio**: Composición flexible de procesamiento LLM.

### 4. Strategy Pattern

**Aplicado en**: Routing condicional

**Beneficio**: Diferentes estrategias según contexto (interno/externo/mixto).

---

## Autores

- **David Burckhardt**
- **Martin Vazquez Arispe**
- **Martin Caballero**

---

## Licencia

Este proyecto fue desarrollado como trabajo práctico académico.