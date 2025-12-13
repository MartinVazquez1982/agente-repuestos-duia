from schemas.state import AgentState
from langchain_core.messages import AIMessage

def human_in_the_loop_selection(state: AgentState) -> AgentState:
    """
    Presenta el ranking generado por LLM al usuario y solicita su selección de productos.
    """
    recomendaciones = state.get("recomendaciones_llm", "")
    
    # El LLM ya generó el ranking completo con la pregunta incluida
    mensaje = "📋 **Resumen del ranking:**\n\n"
    mensaje += recomendaciones
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }