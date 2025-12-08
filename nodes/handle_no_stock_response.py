from schemas.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage

def handle_no_stock_response(state: AgentState) -> AgentState:
    """
    Procesa la respuesta del usuario cuando no hay stock disponible.
    Determina si el usuario quiere hacer una nueva búsqueda o cancelar.
    """
    messages = state.get("messages", [])
    
    # Obtener el último mensaje del usuario
    user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content.strip().lower()
            break
    
    if not user_message:
        return {
            "messages": [AIMessage(content="❌ No recibí tu respuesta. ¿Podrías responder de nuevo?")],
            "reiniciar_busqueda": False
        }
    
    # Detectar intención del usuario
    palabras_afirmativas = ['si', 'sí', 'nueva', 'busqueda', 'búsqueda', 'otro', 'otros', 'diferente', 'ok', 'dale', 'bueno']
    palabras_negativas = ['no', 'cancelar', 'cancel', 'salir', 'exit', 'terminar', 'nada']
    
    quiere_nueva_busqueda = any(palabra in user_message for palabra in palabras_afirmativas)
    quiere_cancelar = any(palabra in user_message for palabra in palabras_negativas)
    
    if quiere_nueva_busqueda and not quiere_cancelar:
        # Usuario quiere hacer una nueva búsqueda
        mensaje = "\n" + "✅"*40 + "\n"
        mensaje += "🔄 **NUEVA BÚSQUEDA**\n"
        mensaje += "✅"*40 + "\n\n"
        mensaje += "Perfecto, vamos a realizar una nueva búsqueda.\n\n"
        mensaje += "Por favor, indícame qué productos necesitas:\n\n"
        mensaje += "💡 **Consejo:** Sé lo más específico posible (marca, modelo, características)\n"
        mensaje += "   para obtener mejores resultados.\n"
        
        return {
            "messages": [AIMessage(content=mensaje)],
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
    
    elif quiere_cancelar:
        # Usuario quiere cancelar
        mensaje = "\n" + "👋"*40 + "\n"
        mensaje += "❌ **BÚSQUEDA CANCELADA**\n"
        mensaje += "👋"*40 + "\n\n"
        mensaje += "Entendido. La búsqueda ha sido cancelada.\n\n"
        mensaje += "📋 **Recomendaciones:**\n"
        mensaje += "   • Consulta con el área de compras sobre fechas de reposición\n"
        mensaje += "   • Considera productos alternativos o equivalentes\n"
        mensaje += "   • Vuelve a intentar más tarde cuando haya stock disponible"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "reiniciar_busqueda": False
        }
    
    else:
        # Respuesta ambigua
        mensaje = "❓ No entendí tu respuesta.\n\n"
        mensaje += "Por favor indica:\n"
        mensaje += "• **'sí'** - Para realizar una nueva búsqueda\n"
        mensaje += "• **'no'** - Para cancelar\n"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "reiniciar_busqueda": False
        }

