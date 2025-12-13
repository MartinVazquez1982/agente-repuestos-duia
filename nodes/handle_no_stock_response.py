from schemas.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage
from chains.chain_administrator import ChainAdministrator

def handle_no_stock_response(state: AgentState) -> AgentState:
    """
    Interpreta con LLM respuesta del usuario ante falta de stock (nueva búsqueda o cancelar).
    """
    messages = state.get("messages", [])
    
    # Obtener el último mensaje del usuario
    user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content.strip()
            break
    
    if not user_message:
        return {
            "messages": [AIMessage(content="❌ No recibí tu respuesta. ¿Podrías responder de nuevo?")],
            "reiniciar_busqueda": False
        }
    
    # Usar el LLM para interpretar la intención del usuario
    interpret_chain = ChainAdministrator().get('interpret_no_stock_response_chain')
    response = interpret_chain.invoke({
        "user_response": user_message
    })
    
    intencion = response.content.strip() if hasattr(response, 'content') else str(response).strip()
    
    if "NUEVA_BUSQUEDA" in intencion.upper():
        # Usuario quiere hacer una nueva búsqueda
        return {
            "reiniciar_busqueda": True,
            # Limpiar estado anterior
            "product_requests": [],
            "codigos_repuestos": None,
            "repuestos_encontrados": None,
            "productos_sin_match_interno": None,
            "resultados_internos": {},
            "resultados_externos": {},
            "recomendaciones_llm": None,
            "tiene_stock_disponible": None
        }
    
    elif "CANCELAR" in intencion.upper():
        # Usuario quiere cancelar
        mensaje = "Entendido. La búsqueda ha sido cancelada.\n\n"
        mensaje += "📋 **Recomendaciones:**\n"
        mensaje += "   • Consulta con el área de compras sobre fechas de reposición\n"
        mensaje += "   • Considera productos alternativos o equivalentes\n"
        mensaje += "   • Vuelve a intentar más tarde cuando haya stock disponible"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "reiniciar_busqueda": False
        }
    
    else:
        # Respuesta ambigua (el LLM no pudo determinar)
        mensaje = "❓ No entendí tu respuesta.\n\n"
        mensaje += "Por favor indica:\n"
        mensaje += "• **'sí'** - Para realizar una nueva búsqueda\n"
        mensaje += "• **'no'** - Para cancelar"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "reiniciar_busqueda": False
        }

