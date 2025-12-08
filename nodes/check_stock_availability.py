from schemas.state import AgentState
from langchain_core.messages import AIMessage

def check_stock_availability(state: AgentState) -> AgentState:
    """
    Verifica si hay al menos una opción con stock disponible.
    Si no hay stock en ninguna opción, informa al usuario y pregunta si desea hacer otra búsqueda.
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
        
        mensaje = "\n" + "⚠️"*40 + "\n"
        mensaje += "❌ **SIN STOCK DISPONIBLE**\n"
        mensaje += "⚠️"*40 + "\n\n"
        
        mensaje += "Lo sentimos, actualmente **no tenemos stock disponible** para los productos solicitados:\n\n"
        
        for i, producto in enumerate(productos_buscados, 1):
            mensaje += f"   {i}. {producto}\n"
        
        mensaje += "\n" + "─"*80 + "\n\n"
        mensaje += "🔄 **OPCIONES DISPONIBLES:**\n\n"
        mensaje += "1. **Realizar una nueva búsqueda** con otros productos\n"
        mensaje += "2. **Cancelar** y esperar reposición de stock\n\n"
        mensaje += "─"*80 + "\n\n"
        mensaje += "💬 ¿Deseas realizar una **nueva búsqueda** con otros productos?\n\n"
        mensaje += "Por favor responde:\n"
        mensaje += "• **'sí'** o **'nueva búsqueda'** - Para buscar otros productos\n"
        mensaje += "• **'no'** o **'cancelar'** - Para finalizar\n"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "tiene_stock_disponible": False
        }
    
    # Hay stock disponible, continuar con el flujo normal
    return {
        "tiene_stock_disponible": True
    }

