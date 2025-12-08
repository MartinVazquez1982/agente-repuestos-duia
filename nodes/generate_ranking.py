from chains.chain_administrator import ChainAdministrator
from schemas.state import AgentState

def generate_ranking(state: AgentState) -> AgentState:
    """
    Genera ranking usando SOLO el LLM.
    """
    from utils import format_options_for_llm
    
    product_requests = state.get("product_requests", [])
    resultados_internos = state.get("resultados_internos", {})
    resultados_externos = state.get("resultados_externos", {})
    
    # Preparar información para el LLM
    opciones_para_llm = []
    
    for idx, product_req in enumerate(product_requests, 1):
        product_name = product_req.get("name", f"Producto {idx}")
        internos = resultados_internos.get(idx, [])
        externos = resultados_externos.get(idx, [])
        
        # Combinar todas las opciones
        todas_opciones = []
        
        for opcion in internos:
            todas_opciones.append({**opcion, "tipo": "INTERNO"})
        for opcion in externos:
            todas_opciones.append({**opcion, "tipo": "EXTERNO"})
            
        if todas_opciones:
            # Formatear para el LLM con nombre del producto solicitado
            opciones_para_llm.append(
                format_options_for_llm(f"PRODUCTO {idx}: {product_name}", todas_opciones)
            )
    
    if not opciones_para_llm:
        print("⚠️ No hay opciones para rankear\n")
        return {
            "recomendaciones_llm": "No hay opciones disponibles."
        }
    
    # Crear el texto completo para el LLM
    opciones_texto = "\n\n".join(opciones_para_llm)
    print(f"Estas son las opciones!! {opciones_texto}")
    
    try:
        # Invocar el LLM para que haga el ranking
        recomendaciones = ChainAdministrator().get("ranking_chain").invoke({"opciones_texto": opciones_texto})
        recomendaciones_texto = recomendaciones.content
        
    except Exception as e:
        print(f"❌ Error al obtener ranking del LLM: {e}\n")
        recomendaciones_texto = "Error al generar ranking automático."
    
    return {
        "recomendaciones_llm": recomendaciones_texto
    }