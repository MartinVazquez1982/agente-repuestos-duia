from schemas.state import AgentState

def route_classification(state: AgentState) -> str:
    """
    Decide si continuar con extracción (pedido de repuestos) o terminar (conversación general).
    """
    if state['validation_result'].is_parts_request:
        return "continue"
    else:
        return "end"
    
def route_after_extraction_check(state: AgentState) -> str:
    """
    Decide si iniciar búsqueda semántica (info completa) o solicitar más detalles al usuario.
    """
    if state.get("info_completa", False):
        return "semantic_search"  # ← Todos completos, buscar
    else:
        return "request_more_info"  # ← Alguno incompleto, pedir más info
    
def need_external_search(state: AgentState) -> str:
    """
    Decide si buscar en proveedores externos (sin match interno) o continuar al ranking.
    """
    productos_sin_match = state.get("productos_sin_match_interno", [])
    
    if productos_sin_match and len(productos_sin_match) > 0:
        return "search_external"
    else:
        return "reranking"
    
def route_after_selection(state: AgentState) -> str:
    """
    Decide si procesar pedido (hay selecciones) o terminar (usuario canceló).
    """
    selecciones = state.get("selecciones_usuario", [])
    
    if selecciones and len(selecciones) > 0:
        return "process_order"  # Procesar pedido
    else:
        return "end"  # Terminar (usuario canceló o no hay selección)
    
def route_by_product_type(state: AgentState) -> str:
    """
    Enruta según tipo de productos: solo internos, solo externos, mixtos o terminar.
    """
    selecciones = state.get("selecciones_usuario", [])
    
    if not selecciones:
        return "end"
    
    internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
    externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
    
    tiene_internos = len(internos) > 0
    tiene_externos = len(externos) > 0
    
    if tiene_internos and tiene_externos:
        return "both"  # Tiene ambos tipos
    elif tiene_internos:
        return "internal_only"  # Solo internos
    elif tiene_externos:
        return "external_only"  # Solo externos
    else:
        return "end"

def route_after_stock_check(state: AgentState) -> str:
    """
    Decide si continuar al ranking (hay stock) o informar falta de stock.
    """
    tiene_stock = state.get("tiene_stock_disponible", True)
    
    if tiene_stock:
        return "continue_ranking"  # Hay stock, continuar con ranking
    else:
        return "no_stock"  # No hay stock, informar al usuario

def route_after_no_stock_response(state: AgentState) -> str:
    """
    Decide si reiniciar búsqueda (usuario acepta) o terminar (usuario cancela).
    """
    reiniciar = state.get("reiniciar_busqueda", False)
    
    if reiniciar:
        return "restart"  # Volver al inicio para nueva búsqueda
    else:
        return "end"  # Terminar el flujo