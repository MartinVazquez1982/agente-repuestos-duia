from schemas.state import AgentState
from langchain_core.messages import AIMessage

def request_new_products(state: AgentState) -> AgentState:
    """
    Solicita al usuario que especifique nuevos productos para realizar otra búsqueda.
    """
    mensaje = "✅ Perfecto, vamos a realizar una nueva búsqueda.\n\n"
    mensaje += "Por favor, indícame qué productos necesitas:\n\n"
    mensaje += "💡 **Consejo:** Sé lo más específico posible (marca, modelo, características)\n"
    mensaje += "   para obtener mejores resultados."
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }

