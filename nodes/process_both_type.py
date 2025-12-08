from schemas.state import AgentState
from nodes.process_internal_order import process_internal_order
from nodes.generate_external_email import generate_external_email

def process_both_types(state: AgentState) -> AgentState:
    """
    Procesa tanto productos INTERNOS como EXTERNOS.
    Llama a ambas funciones que hacen print directo.
    """
    # Procesar internos (hace print)
    process_internal_order(state)
    
    # Procesar externos (hace print)
    generate_external_email(state)
    
    # No retorna mensaje, el resumen lo hará schedule_delivery
    return {}