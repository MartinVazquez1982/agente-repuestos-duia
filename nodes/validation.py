from schemas.state import AgentState
from chains.chain_administrator import ChainAdministrator

def classify_request(state: AgentState) -> AgentState:
    """
    Clasifica la solicitud del usuario.
    """
    messages = state['messages']
    validation_result_object = ChainAdministrator().get('validation_chain').invoke({"messages": messages})
    
    return {"validation_result": validation_result_object}

def set_val_message(state: AgentState) -> AgentState:
    """
    Establece el mensaje de validación.
    """
    return {"messages": [state['validation_result'].message]}