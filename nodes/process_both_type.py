from schemas.state import AgentState
from langchain_core.messages import AIMessage
from nodes.process_internal_order import process_internal_order
from nodes.generate_external_email import generate_external_email

def process_both_types(state: AgentState) -> AgentState:
    """
    Procesa tanto productos INTERNOS como EXTERNOS.
    Genera orden interna Y emails externos.
    """
    # Procesar internos
    result_interno = process_internal_order(state)
    mensaje_interno = result_interno["messages"][0].content
    
    # Procesar externos
    result_externo = generate_external_email(state)
    mensaje_externo = result_externo["messages"][0].content
    
    # Combinar mensajes
    mensaje_completo = mensaje_interno + "\n\n" + mensaje_externo
    
    return {
        "messages": [AIMessage(content=mensaje_completo)]
    }