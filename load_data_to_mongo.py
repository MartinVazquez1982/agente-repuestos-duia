"""
Script para cargar datos del CSV a MongoDB con embeddings vectoriales.
Genera embeddings usando sentence-transformers y los almacena en MongoDB Atlas.
"""
import os
import pandas as pd
from dotenv import load_dotenv
from pymongo import MongoClient
from sentence_transformers import SentenceTransformer

# Cargar variables de entorno
load_dotenv()

# Configuración
MONGO_URI = os.getenv("MONGO_URI")
CSV_FILE = "repuestos.csv"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

print("="*80)
print("🔄 CARGA DE DATOS A MONGODB CON EMBEDDINGS")
print("="*80)

# 1. Conectar a MongoDB
print("\n📡 Conectando a MongoDB...")
client = MongoClient(MONGO_URI)
db = client["repuestos_db"]
collection = db["repuestos"]

# 2. Limpiar colección existente
print("🗑️  Limpiando colección existente...")
result = collection.delete_many({})
print(f"   ✅ Eliminados {result.deleted_count} documentos")

# 3. Cargar CSV
print(f"\n📂 Cargando datos desde {CSV_FILE}...")
df = pd.read_csv(CSV_FILE, on_bad_lines='warn', engine='python')
print(f"   ✅ Cargadas {len(df)} filas")

# 4. Cargar modelo de embeddings
print(f"\n🤖 Cargando modelo de embeddings: {MODEL_NAME}...")
model = SentenceTransformer(MODEL_NAME)
print("   ✅ Modelo cargado")

# 5. Generar embeddings y preparar documentos
print("\n🔢 Generando embeddings...")
documentos = []

for idx, row in df.iterrows():
    # Crear texto para embedding (descripción + marca + modelo + categoría)
    texto_embedding = f"{row['repuesto_descripcion']} {row['marca']} {row['modelo']} {row['categoria']}"
    
    # Generar embedding
    embedding = model.encode(texto_embedding).tolist()
    
    # Crear documento
    documento = {
        "id_repuesto": row["id_repuesto"],
        "repuesto_descripcion": row["repuesto_descripcion"],
        "categoria": row["categoria"],
        "marca": row["marca"],
        "modelo": row["modelo"],
        "proveedor_tipo": row["proveedor_tipo"],
        "proveedor_id": row["proveedor_id"],
        "proveedor_nombre": row["proveedor_nombre"],
        "proveedor_rating": int(row["proveedor_rating"]),
        "costo_unitario": float(row["costo_unitario"]),
        "moneda": row["moneda"],
        "stock_disponible": int(row["stock_disponible"]),
        "lead_time_dias": int(row["lead_time_dias"]),
        "ubicacion_stock": row["ubicacion_stock"],
        "cantidad_minima_pedido": int(row["cantidad_minima_pedido"]),
        "tiempo_vida_estimado_hrs": int(row["tiempo_vida_estimado_hrs"]),
        "nota": row["nota"],
        "embedding_vector": embedding
    }
    
    documentos.append(documento)
    
    if (idx + 1) % 10 == 0:
        print(f"   Procesados {idx + 1}/{len(df)} documentos...")

print(f"   ✅ {len(documentos)} documentos preparados con embeddings")

# 6. Insertar en MongoDB
print("\n💾 Insertando documentos en MongoDB...")
result = collection.insert_many(documentos)
print(f"   ✅ Insertados {len(result.inserted_ids)} documentos")

# 7. Verificar algunos documentos
print("\n🔍 Verificando datos insertados...")
total_docs = collection.count_documents({})
print(f"   Total de documentos en la colección: {total_docs}")

# Contar por tipo de proveedor
internos = collection.count_documents({"proveedor_tipo": "INTERNAL"})
externos = collection.count_documents({"proveedor_tipo": "EXTERNAL"})
print(f"   • Productos INTERNOS: {internos}")
print(f"   • Productos EXTERNOS: {externos}")

# Mostrar algunos productos solo externos
print("\n📦 Productos que solo existen externamente (nuevos):")
productos_externos_unicos = [
    "R-0101", "R-0102", "R-0103", "R-0104", "R-0105",
    "R-0106", "R-0107", "R-0108", "R-0109", "R-0110"
]

for codigo in productos_externos_unicos[:5]:  # Mostrar solo los primeros 5
    doc = collection.find_one({"id_repuesto": codigo})
    if doc:
        print(f"   ✅ {codigo}: {doc['repuesto_descripcion'][:60]}... (stock: {doc['stock_disponible']})")

print("\n" + "="*80)
print("✅ CARGA COMPLETADA EXITOSAMENTE")
print("="*80)
print("\n💡 Nota: Asegúrate de tener creado el índice vectorial en MongoDB Atlas:")
print("   Nombre: vector_index_repuestos")
print("   Campo: embedding_vector")
print("   Dimensiones: 384")
print("   Similitud: cosine")
print("="*80)

