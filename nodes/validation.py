from schemas.state import AgentState
from chains.chain_administrator import ChainAdministrator

def classify_request(state: AgentState) -> AgentState:
    """
    Clasifica con LLM si el mensaje es solicitud de repuestos o conversación general.
    """
    messages = state['messages']
    validation_result_object = ChainAdministrator().get('validation_chain').invoke({"messages": messages})
    
    return {"validation_result": validation_result_object}

def set_val_message(state: AgentState) -> AgentState:
    """
    Retorna el mensaje de validación al usuario desde el resultado de clasificación.
    """
    return {"messages": [state['validation_result'].message]}