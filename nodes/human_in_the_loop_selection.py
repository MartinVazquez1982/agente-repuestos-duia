from schemas.state import AgentState
from langchain_core.messages import AIMessage

def human_in_the_loop_selection(state: AgentState) -> AgentState:
    """
    Presenta el ranking al usuario y solicita su selección.
    Este nodo se ejecuta DESPUÉS del reranking.
    """
    recomendaciones = state.get("recomendaciones_llm", "")
    codigos = state.get("codigos_repuestos", [])
    
    # Mostrar el ranking (ya fue mostrado por el nodo anterior)
    mensaje = "📋 **Resumen del ranking:**\n\n"
    mensaje += recomendaciones + "\n\n"
    mensaje += "─" * 60 + "\n\n"
    mensaje += "🤔 **¿Deseas proceder con alguna de estas opciones?**\n\n"
    mensaje += "Por favor indica:\n"
    mensaje += "• **'sí'** o **'confirmar'** - Para proceder con las mejores opciones\n"
    mensaje += "• **'no'** o **'cancelar'** - Para cancelar el pedido\n"
    mensaje += "• **[código(s)]** - Para seleccionar específicos (ej: 'R-0001, R-0005')\n"
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }