from sentence_transformers import SentenceTransformer
import torch
import numpy as np

# 1. Cargar el Modelo de Embedding
# Usamos un modelo ligero y eficiente de Hugging Face
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)
print(f"Modelo {model_name} cargado exitosamente.")

# 2. Datos de Ejemplo (Tu Catálogo de Repuestos)
# En un escenario real, esto se cargaría desde tu base de datos o archivo CSV.
catalogo_descripciones = [
    "Junta tórica de motor, sellado de alta temperatura, para eje principal de 10mm.",
    "Biela de acero reforzado, serie 500, para motores de alta potencia.",
    "Filtro de aceite sintético, compatible con motores diésel M-300.",
    "Sello para el eje principal del motor. Material Vitón. Diámetro interno 10mm."
]

# 3. Generar los Embeddings (Vectores)
# El método .encode() es el encargado de generar los vectores.
# 'convert_to_tensor=True' es útil si planeas hacer cálculos con PyTorch/GPU.
# Si solo vas a guardar los vectores, puedes usar 'convert_to_numpy=True'
embeddings = model.encode(
    catalogo_descripciones,
    convert_to_tensor=False, # Devuelve una matriz de NumPy
    show_progress_bar=True
)

# 4. Inspeccionar los Resultados
print("-" * 50)
print(f"Descripciones vectorizadas: {len(catalogo_descripciones)}")
print(f"Forma del tensor de Embeddings: {embeddings.shape}")
print(f"Dimensión de cada vector (embedding): {embeddings.shape[1]}")
print("-" * 50)

# El primer embedding (vector) para el primer repuesto
print("Primer embedding (primeros 5 valores):")
print(embeddings[0][:5])
print("-" * 50)

# 5. Aplicación: Búsqueda de Similitud
# Puedes usar estos embeddings para calcular la similitud del coseno (Cosine Similarity).

# Solicitud del Agente (Query)
solicitud = "Necesito el sello del eje de la máquina que aguante calor."
solicitud_embedding = model.encode([solicitud], convert_to_tensor=True)

# Conversión de los embeddings del catálogo a tensor para el cálculo
catalogo_embeddings_tensor = torch.from_numpy(embeddings)

# Cálculo de Similitud del Coseno
# Se usa la función de similitud del coseno entre la solicitud y cada elemento del catálogo.
from torch.nn.functional import cosine_similarity
similarities = cosine_similarity(solicitud_embedding, catalogo_embeddings_tensor)
similarities_np = similarities.cpu().numpy()

# 6. Ranking de Similitud
ranking = np.argsort(-similarities_np) # Orden descendente

print(f"Solicitud: '{solicitud}'")
print("\nRanking de Repuestos (por Similitud Semántica):")

for i, idx in enumerate(ranking):
    print(f"  {i+1}. Similitud: {similarities_np[idx]:.4f} -> {catalogo_descripciones[idx]}")