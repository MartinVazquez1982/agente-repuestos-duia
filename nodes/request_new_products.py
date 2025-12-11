from schemas.state import AgentState
from langchain_core.messages import AIMessage

def request_new_products(state: AgentState) -> AgentState:
    """
    Nodo que pide al usuario que indique los nuevos productos para buscar.
    Este nodo se ejecuta después de que el usuario confirmó que quiere hacer una nueva búsqueda.
    """
    mensaje = "✅ Perfecto, vamos a realizar una nueva búsqueda.\n\n"
    mensaje += "Por favor, indícame qué productos necesitas:\n\n"
    mensaje += "💡 **Consejo:** Sé lo más específico posible (marca, modelo, características)\n"
    mensaje += "   para obtener mejores resultados."
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }

