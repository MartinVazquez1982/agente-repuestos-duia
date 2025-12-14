from schemas.state import AgentState
from nodes.process_internal_order import process_internal_order
from nodes.generate_external_email import generate_external_email

def process_both_types(state: AgentState) -> AgentState:
    """
    Procesa productos INTERNOS y EXTERNOS llamando a ambas funciones de impresión.
    """
    # Procesar internos
    process_internal_order(state)
    
    # Procesar externos
    generate_external_email(state)
    
    # No retorna mensaje, el resumen lo hará schedule_delivery
    return {}