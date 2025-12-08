from sentence_transformers import SentenceTransformer
from langchain_core.messages import AIMessage
from db.mongo import MongoCollectionManager
from schemas.state import AgentState
from schemas.repuesto import Repuesto

def semantic_search_internal(state: AgentState) -> AgentState:
    """
    Búsqueda semántica SOLO en inventario INTERNO.
    Verifica qué productos fueron encontrados y cuáles no.
    Combina búsqueda semántica + verificación de stock en un solo paso.
    """    
    product_requests = state.get("product_requests", [])
    
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    todos_repuestos = []
    codigos_unicos_global = set()
    codigos_encontrados_global = []
    productos_sin_resultados = []
    resultados_por_codigo = {}  # Para el reranking
    mensaje_productos = ""
    
    for idx, product_req in enumerate(product_requests, 1):
        product_query = product_req.get("name", "")
        
        if not product_query:
            continue
                
        query_embedding = model.encode(product_query).tolist()
        
        # Pipeline con FILTRO INTERNO
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index_repuestos",
                    "path": "embedding_vector",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": 5
                }
            },
            {
                "$project": {
                    "id_repuesto": 1,
                    "repuesto_descripcion": 1,
                    "categoria": 1,
                    "marca": 1,
                    "modelo": 1,
                    "proveedor_tipo": 1,
                    "proveedor_nombre": 1,
                    "stock_disponible": 1,
                    "costo_unitario": 1,
                    "lead_time_dias": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        try:
            resultados_raw = list(MongoCollectionManager().get_collection().aggregate(pipeline))
            
            # Filtrar por proveedor_tipo DESPUÉS de la búsqueda
            resultados = [r for r in resultados_raw if r.get('proveedor_tipo') == 'INTERNAL']
            
            if not resultados or len(resultados) == 0:
                print(f"   ❌ No encontrado en inventario interno\n")
                productos_sin_resultados.append({
                    "idx": idx,
                    "name": product_query,
                    "product_req": product_req
                })
                mensaje_productos += f"**{idx}. {product_query}**\n   ❌ No disponible internamente\n\n"
                continue
            
            # Filtrar por stock disponible y score
            resultados_con_stock = [
                r for r in resultados 
                if r.get('score', 0) >= 0.50 and r.get('stock_disponible', 0) > 0
            ]
            
            if not resultados_con_stock:
                print(f"   ⚠️  Encontrado pero sin stock disponible\n")
                productos_sin_resultados.append({
                    "idx": idx,
                    "name": product_query,
                    "product_req": product_req
                })
                mensaje_productos += f"**{idx}. {product_query}**\n   ⚠️  Sin stock interno\n\n"
                continue
            
            
            mensaje_productos += f"**{idx}. {product_query}**\n"
            
            for i, r in enumerate(resultados_con_stock[:3], 1):  # Top 3
                if '_id' in r:
                    r['_id'] = str(r['_id'])
                
                repuesto = Repuesto(
                    id_repuesto=r['id_repuesto'],
                    repuesto_descripcion=r['repuesto_descripcion'],
                    marca=r.get('marca', 'N/A'),
                    modelo=r.get('modelo', 'N/A'),
                    categoria=r.get('categoria', 'N/A'),
                    score=r.get('score', 0)
                )
                
                todos_repuestos.append(repuesto)
                
                if repuesto.id_repuesto not in codigos_unicos_global:
                    codigos_encontrados_global.append(repuesto.id_repuesto)
                    codigos_unicos_global.add(repuesto.id_repuesto)
                
                # Guardar en formato para reranking
                codigo = repuesto.id_repuesto
                if codigo not in resultados_por_codigo:
                    resultados_por_codigo[codigo] = []
                resultados_por_codigo[codigo].append(r)
                
                stock = r.get('stock_disponible', 0)
                proveedor = r.get('proveedor_nombre', 'N/A')                
                mensaje_productos += f"   {i}. **{repuesto.id_repuesto} ({repuesto.marca})** - Stock: {stock}\n"
            
            mensaje_productos += "\n"
                    
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
            productos_sin_resultados.append({
                "idx": idx,
                "name": product_query,
                "product_req": product_req
            })
    
    # Preparar mensaje
    mensaje = "🔍 **Resultados de búsqueda interna:**\n\n"
    mensaje += mensaje_productos
    
    if productos_sin_resultados:
        mensaje += f"────────────────────────────────\n"
        mensaje += f"⚠️  **{len(productos_sin_resultados)} producto(s) no disponible(s) internamente**\n"
        mensaje += f"🌐 Buscando en proveedores externos..."
    else:
        mensaje += "✅ Todos los productos disponibles internamente"
    
    return {
        "messages": [AIMessage(content=mensaje)],
        "codigos_repuestos": codigos_encontrados_global,
        "repuestos_encontrados": todos_repuestos,
        "productos_sin_match_interno": productos_sin_resultados,
        "resultados_internos": resultados_por_codigo,  # Para el reranking
        "info_completa": True
    }
    
def semantic_search_external(state: AgentState) -> AgentState:
    """
    Búsqueda semántica SOLO en proveedores EXTERNOS.
    Solo busca productos que NO se encontraron internamente.
    """
        
    productos_sin_match = state.get("productos_sin_match_interno", [])
    
    if not productos_sin_match:
        print("✅ Todos los productos se encontraron internamente\n")
        return {}
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    repuestos_externos = list(state.get("repuestos_encontrados", []))
    codigos_existentes = set(state.get("codigos_repuestos", []))
    codigos_externos = []
    resultados_externos_por_codigo = {}  # Para el reranking
    mensaje_externos = ""
    
    for item in productos_sin_match:
        product_query = item.get("name", "")
        idx = item.get("idx", "")
                
        query_embedding = model.encode(product_query).tolist()
        
        # Pipeline con FILTRO EXTERNO
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index_repuestos",
                    "path": "embedding_vector",
                    "queryVector": query_embedding,
                    "numCandidates": 100,
                    "limit": 5
                }
            },
            {
                "$project": {
                    "id_repuesto": 1,
                    "repuesto_descripcion": 1,
                    "categoria": 1,
                    "marca": 1,
                    "modelo": 1,
                    "proveedor_tipo": 1,
                    "proveedor_nombre": 1,
                    "costo_unitario": 1,
                    "lead_time_dias": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        try:
            resultados_raw = list(MongoCollectionManager().get_collection().aggregate(pipeline))
            
            # Filtrar por proveedor_tipo DESPUÉS de la búsqueda
            resultados = [r for r in resultados_raw if r.get('proveedor_tipo') == 'EXTERNAL']
            
            if not resultados:
                print(f"   ❌ No encontrado en externos\n")
                mensaje_externos += f"**{idx}. {product_query}**\n   ❌ No disponible\n\n"
                continue
            
            # Filtrar por score
            resultados_validos = [r for r in resultados if r.get('score', 0) >= 0.50]
                        
            mensaje_externos += f"**{idx}. {product_query}**\n"
            
            for i, r in enumerate(resultados_validos[:3], 1):  # Top 3
                if '_id' in r:
                    r['_id'] = str(r['_id'])
                
                repuesto = Repuesto(
                    id_repuesto=r['id_repuesto'],
                    repuesto_descripcion=r['repuesto_descripcion'],
                    marca=r.get('marca', 'N/A'),
                    modelo=r.get('modelo', 'N/A'),
                    categoria=r.get('categoria', 'N/A'),
                    score=r.get('score', 0)
                )
                
                repuestos_externos.append(repuesto)
                
                if repuesto.id_repuesto not in codigos_existentes:
                    codigos_externos.append(repuesto.id_repuesto)
                    codigos_existentes.add(repuesto.id_repuesto)
                
                # Guardar en formato para reranking
                codigo = repuesto.id_repuesto
                if codigo not in resultados_externos_por_codigo:
                    resultados_externos_por_codigo[codigo] = []
                resultados_externos_por_codigo[codigo].append(r)
                
                proveedor = r.get('proveedor_nombre', 'N/A')
                lead_time = r.get('lead_time_dias', 'N/A')                
                mensaje_externos += f"   {i}. **{repuesto.id_repuesto} ({repuesto.marca})** - {proveedor}\n"
            
            mensaje_externos += "\n"
                    
        except Exception as e:
            print(f"   ❌ Error: {e}\n")
    
    # Combinar códigos
    todos_codigos = list(state.get("codigos_repuestos", [])) + codigos_externos
    
    mensaje = "🌐 **Búsqueda en proveedores externos:**\n\n"
    mensaje += mensaje_externos
    mensaje += f"────────────────────────────────\n"
    mensaje += f"✅ {len(codigos_externos)} producto(s) adicional(es) encontrado(s) externamente"
    
    return {
        "messages": [AIMessage(content=mensaje)],
        "codigos_repuestos": todos_codigos,
        "repuestos_encontrados": repuestos_externos,
        "resultados_externos": resultados_externos_por_codigo  # Para el reranking
    }