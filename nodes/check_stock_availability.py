from schemas.state import AgentState
from langchain_core.messages import AIMessage
from chains.chain_administrator import ChainAdministrator

def check_stock_availability(state: AgentState) -> AgentState:
    """
    Verifica si hay stock disponible en opciones internas/externas; genera mensaje con LLM si no hay stock.
    """
    resultados_internos = state.get("resultados_internos", {})
    resultados_externos = state.get("resultados_externos", {})
    
    # Verificar si hay stock en alguna opción
    tiene_stock = False
    
    # Verificar internos
    for idx, opciones in resultados_internos.items():
        for opcion in opciones:
            stock = opcion.get('stock_disponible', 0)
            if stock > 0:
                tiene_stock = True
                break
        if tiene_stock:
            break
    
    # Si no hay stock en internos, verificar externos
    if not tiene_stock:
        for idx, opciones in resultados_externos.items():
            for opcion in opciones:
                stock = opcion.get('stock_disponible', 0)
                if stock > 0:
                    tiene_stock = True
                    break
            if tiene_stock:
                break
    
    if not tiene_stock:
        # No hay stock disponible en ninguna opción
        product_requests = state.get("product_requests", [])
        productos_buscados = [p.get("name", "producto") for p in product_requests]
        
        # Formatear lista de productos
        productos_lista = "\n".join([f"{i}. {producto}" for i, producto in enumerate(productos_buscados, 1)])
        
        # Usar el LLM para generar el mensaje
        no_stock_chain = ChainAdministrator().get('no_stock_chain')
        response = no_stock_chain.invoke({
            "productos_solicitados": productos_lista
        })
        
        mensaje = response.content if hasattr(response, 'content') else str(response)
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "tiene_stock_disponible": False
        }
    
    # Hay stock disponible, continuar con el flujo normal
    return {
        "tiene_stock_disponible": True
    }

