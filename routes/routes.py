from schemas.state import AgentState

def route_classification(state: AgentState) -> str:
    """
    Ruta de clasificación.
    """
    if state['validation_result'].is_parts_request:
        return "continue"
    else:
        return "end"
    
def route_after_extraction_check(state: AgentState) -> str:
    """
    Decide si continuar con semantic_search o pedir más info.
    """
    if state.get("info_completa", False):
        return "semantic_search"  # ← Todos completos, buscar
    else:
        return "request_more_info"  # ← Alguno incompleto, pedir más info
    
def need_external_search(state: AgentState) -> str:
    """
    Decide si se necesita búsqueda externa.
    """
    productos_sin_match = state.get("productos_sin_match_interno", [])
    
    if productos_sin_match and len(productos_sin_match) > 0:
        return "search_external"
    else:
        return "reranking"
    
def route_after_selection(state: AgentState) -> str:
    """
    Decide si proceder con el pedido o terminar.
    """
    selecciones = state.get("selecciones_usuario", [])
    
    if selecciones and len(selecciones) > 0:
        return "process_order"  # Procesar pedido
    else:
        return "end"  # Terminar (usuario canceló o no hay selección)
    
def route_by_product_type(state: AgentState) -> str:
    """
    Decide el flujo según el tipo de productos seleccionados.
    - Solo INTERNOS → process_internal_order
    - Solo EXTERNOS → generate_external_email
    - MIXTOS → process_both (ambos procesos)
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