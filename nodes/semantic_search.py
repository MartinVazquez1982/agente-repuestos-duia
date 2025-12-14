from sentence_transformers import SentenceTransformer
from langchain_core.messages import AIMessage
from db.mongo import MongoCollectionManager
from schemas.state import AgentState
from schemas.repuesto import Repuesto

def semantic_search_internal(state: AgentState) -> AgentState:
    """
    Realiza búsqueda vectorial en inventario INTERNO y verifica stock vs cantidad solicitada por producto.
    """    
    product_requests = state.get("product_requests", [])
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    todos_repuestos = []
    codigos_unicos_global = set()
    codigos_encontrados_global = []
    productos_sin_resultados = []
    resultados_por_producto = {}  # Para el reranking - agrupado por índice de producto
    mensaje_productos = ""
    
    for idx, product_req in enumerate(product_requests, 1):
        product_query = product_req.get("name", "")
        cantidad_solicitada = product_req.get("cantidad", 1)  # Obtener cantidad solicitada
        
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
                productos_sin_resultados.append({
                    "idx": idx,
                    "name": product_query,
                    "product_req": product_req,
                    "cantidad_solicitada": cantidad_solicitada
                })
                mensaje_productos += f"**{idx}. {product_query} (x{cantidad_solicitada})**\n   ❌ No disponible internamente\n\n"
                continue
            
            # ═══════════════════════════════════════════════════════
            # VERIFICAR STOCK vs CANTIDAD SOLICITADA
            # ═══════════════════════════════════════════════════════
            
            # Filtrar por score mínimo
            resultados_validos = [r for r in resultados if r.get('score', 0) >= 0.5]
            
            # Clasificar por suficiencia de stock
            resultados_stock_suficiente = []
            resultados_stock_insuficiente = []
            resultados_sin_stock = []
            
            for r in resultados_validos:
                stock_disponible = r.get('stock_disponible', 0)
                
                if stock_disponible >= cantidad_solicitada:
                    resultados_stock_suficiente.append(r)
                elif stock_disponible > 0:
                    resultados_stock_insuficiente.append(r)
                else:
                    resultados_sin_stock.append(r)
            
            # DECISIÓN: ¿Hay suficiente stock en al menos UNA opción?
            if resultados_stock_suficiente:
                # ✅ HAY STOCK SUFICIENTE - Mostrar solo internos
                
                mensaje_productos += f"**{idx}. {product_query} (x{cantidad_solicitada})**\n"
                
                for i, r in enumerate(resultados_stock_suficiente[:3], 1):  # Top 3
                    if '_id' in r:
                        r['_id'] = str(r['_id'])
                    
                    repuesto = Repuesto(
                        id_repuesto=r['id_repuesto'],
                        repuesto_descripcion=r['repuesto_descripcion'],
                        marca=str(r.get('marca', 'N/A')),
                        modelo=str(r.get('modelo', 'N/A')),
                        categoria=str(r.get('categoria', 'N/A')),
                        score=r.get('score', 0)
                    )
                    
                    todos_repuestos.append(repuesto)
                    
                    if repuesto.id_repuesto not in codigos_unicos_global:
                        codigos_encontrados_global.append(repuesto.id_repuesto)
                        codigos_unicos_global.add(repuesto.id_repuesto)
                    
                    # Guardar en formato para reranking - AGRUPAR POR PRODUCTO SOLICITADO
                    if idx not in resultados_por_producto:
                        resultados_por_producto[idx] = []
                    resultados_por_producto[idx].append(r)
                    
                    stock = r.get('stock_disponible', 0)
                    proveedor = r.get('proveedor_nombre', 'N/A')
                    mensaje_productos += f"   {i}. **{repuesto.id_repuesto} ({repuesto.marca})** - Stock: {stock}/{cantidad_solicitada} ✅\n"
                
                mensaje_productos += "\n"
            
            else:
                # ⚠️ STOCK INSUFICIENTE O SIN STOCK - Buscar en externos                
                codigos_para_externos = []
                
                # ═══════════════════════════════════════════════════════
                # AGREGAR opciones internas con stock insuficiente al ranking
                # ═══════════════════════════════════════════════════════
                if resultados_stock_insuficiente:
                    
                    for r in resultados_stock_insuficiente:
                        if '_id' in r:
                            r['_id'] = str(r['_id'])
                        
                        # Agregar a repuestos_encontrados
                        repuesto = Repuesto(
                            id_repuesto=r['id_repuesto'],
                            repuesto_descripcion=r['repuesto_descripcion'],
                            marca=str(r.get('marca', 'N/A')),
                            modelo=str(r.get('modelo', 'N/A')),
                            categoria=str(r.get('categoria', 'N/A')),
                            score=r.get('score', 0)
                        )
                        todos_repuestos.append(repuesto)
                        
                        if repuesto.id_repuesto not in codigos_unicos_global:
                            codigos_encontrados_global.append(repuesto.id_repuesto)
                            codigos_unicos_global.add(repuesto.id_repuesto)
                        
                        # Agregar a resultados_internos para el ranking
                        if idx not in resultados_por_producto:
                            resultados_por_producto[idx] = []
                        resultados_por_producto[idx].append(r)
                        
                        # Agregar código para búsqueda externa
                        codigo = r.get('id_repuesto')
                        if codigo and codigo not in codigos_para_externos:
                            codigos_para_externos.append(codigo)
                
                # Extraer códigos de productos sin stock
                for r in resultados_sin_stock:
                    codigo = r.get('id_repuesto')
                    if codigo and codigo not in codigos_para_externos:
                        codigos_para_externos.append(codigo)
                
                # Mostrar lo que hay (aunque sea insuficiente)
                mensaje_productos += f"**{idx}. {product_query} (x{cantidad_solicitada})**\n"
                
                if resultados_stock_insuficiente:
                    mensaje_productos += f"   ⚠️  Stock insuficiente en interno:\n"
                    for i, r in enumerate(resultados_stock_insuficiente[:2], 1):
                        stock = r.get('stock_disponible', 0)
                        codigo = r.get('id_repuesto', 'N/A')
                        mensaje_productos += f"      • {codigo}: Solo {stock}/{cantidad_solicitada} disponibles\n"
                else:
                    mensaje_productos += f"   ❌ Sin stock disponible\n"
                
                mensaje_productos += f"   🔍 Buscando opciones externas...\n\n"
                
                # Agregar a productos sin resultados (para búsqueda externa)
                productos_sin_resultados.append({
                    "idx": idx,
                    "name": product_query,
                    "product_req": product_req,
                    "cantidad_solicitada": cantidad_solicitada,
                    "codigos_sin_stock": codigos_para_externos,
                    "stock_insuficiente": len(resultados_stock_insuficiente) > 0
                })
                # No hacer continue - seguir el flujo para agregar el mensaje
                
            mensaje_productos += "\n"
                    
        except Exception as e:
            productos_sin_resultados.append({
                "idx": idx,
                "name": product_query,
                "product_req": product_req,
                "cantidad_solicitada": cantidad_solicitada
            })
    
    # Preparar mensaje
    mensaje = "🔍 **Resultados de búsqueda interna:**\n\n"
    mensaje += mensaje_productos
    
    if productos_sin_resultados:
        mensaje += f"────────────────────────────────\n"
        mensaje += f"⚠️  **{len(productos_sin_resultados)} producto(s) requiere(n) búsqueda externa**\n"
        mensaje += f"🌐 Buscando en proveedores externos..."
    else:
        mensaje += "✅ Todos los productos con stock suficiente internamente"
    
    return {
        "messages": [AIMessage(content=mensaje)],
        "codigos_repuestos": codigos_encontrados_global,
        "repuestos_encontrados": todos_repuestos,
        "productos_sin_match_interno": productos_sin_resultados,
        "resultados_internos": resultados_por_producto,  # Para el reranking - agrupado por producto
        "info_completa": True
    }
    
def semantic_search_external(state: AgentState) -> AgentState:
    """
    Búsqueda híbrida en proveedores EXTERNOS: por código (si disponible) o semántica (fallback).
    """
        
    productos_sin_match = state.get("productos_sin_match_interno", [])
    
    if not productos_sin_match:
        return {}
    
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    repuestos_externos = list(state.get("repuestos_encontrados", []))
    codigos_existentes = set(state.get("codigos_repuestos", []))
    codigos_externos = []
    resultados_externos_por_producto = {}  # Para el reranking - agrupado por producto
    mensaje_externos = ""
    
    for item in productos_sin_match:
        product_query = item.get("name", "")
        idx = item.get("idx", "")
        cantidad_solicitada = item.get("cantidad_solicitada", 1)  # Obtener cantidad
        codigos_sin_stock = item.get("codigos_sin_stock", [])
        stock_insuficiente = item.get("stock_insuficiente", False)
                
        # BÚSQUEDA HÍBRIDA: Por código si existe, sino semántica
        if codigos_sin_stock:
            # ═══════════════════════════════════════════════════════
            # CASO A: BÚSQUEDA POR CÓDIGO (más precisa y rápida)
            # ═══════════════════════════════════════════════════════
            
            resultados = []
            for codigo in codigos_sin_stock:
                pipeline = [
                    {
                        "$match": {
                            "id_repuesto": codigo,
                            "proveedor_tipo": "EXTERNAL"
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
                            "lead_time_dias": 1
                        }
                    }
                ]
                
                try:
                    resultados_codigo = list(MongoCollectionManager().get_collection().aggregate(pipeline))
                    resultados.extend(resultados_codigo)

                except Exception as e:
                    print(f"      ❌ Error buscando {codigo}: {e}")
            
            # Asignar score=1.0 para búsquedas por código (match exacto)
            for r in resultados:
                r['score'] = 1.0
                
        else:
            # ═══════════════════════════════════════════════════════
            # CASO B: BÚSQUEDA SEMÁNTICA (fallback sin código)
            # ═══════════════════════════════════════════════════════
            
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
            except Exception as e:
                resultados = []
        
        # ═══════════════════════════════════════════════════════
        # PROCESAMIENTO DE RESULTADOS (común para ambos casos)
        # ═══════════════════════════════════════════════════════
        try:
            if not resultados:
                mensaje_externos += f"**{idx}. {product_query} (x{cantidad_solicitada})**\n   ❌ No disponible\n\n"
                continue
            
            # Filtrar por score (búsqueda por código ya tiene score=1.0)
            resultados_validos = [r for r in resultados if r.get('score', 0) >= 0.50]
            
            if not resultados_validos:
                mensaje_externos += f"**{idx}. {product_query} (x{cantidad_solicitada})**\n   ❌ No disponible\n\n"
                continue
                                    
            # Indicar tipo de búsqueda y estado de stock en el mensaje
            tipo_busqueda = "🔢 Por código" if codigos_sin_stock else "🔍 Semántica"
            estado_stock = "⚠️ Stock insuficiente" if stock_insuficiente else "❌ Sin stock"
            mensaje_externos += f"**{idx}. {product_query} (x{cantidad_solicitada})** - {estado_stock}\n"
            mensaje_externos += f"   {tipo_busqueda} - Opciones externas:\n"
            
            for i, r in enumerate(resultados_validos[:3], 1):  # Top 3
                if '_id' in r:
                    r['_id'] = str(r['_id'])
                
                repuesto = Repuesto(
                    id_repuesto=r['id_repuesto'],
                    repuesto_descripcion=r['repuesto_descripcion'],
                    marca=str(r.get('marca', 'N/A')),
                    modelo=str(r.get('modelo', 'N/A')),
                    categoria=str(r.get('categoria', 'N/A')),
                    score=r.get('score', 0)
                )
                
                repuestos_externos.append(repuesto)
                
                if repuesto.id_repuesto not in codigos_existentes:
                    codigos_externos.append(repuesto.id_repuesto)
                    codigos_existentes.add(repuesto.id_repuesto)
                
                # Guardar en formato para reranking - AGRUPAR POR PRODUCTO SOLICITADO
                if idx not in resultados_externos_por_producto:
                    resultados_externos_por_producto[idx] = []
                resultados_externos_por_producto[idx].append(r)
                
                proveedor = r.get('proveedor_nombre', 'N/A')
                lead_time = r.get('lead_time_dias', 'N/A')                
                mensaje_externos += f"   {i}. **{repuesto.id_repuesto} ({repuesto.marca})** - {proveedor}\n"
            
            mensaje_externos += "\n"
                    
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
    
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
        "resultados_externos": resultados_externos_por_producto  # Para el reranking - agrupado por producto
    }