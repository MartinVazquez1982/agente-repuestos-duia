from langchain_core.messages import AIMessage, BaseMessage
from chains.chain_administrator import ChainAdministrator
from schemas.state import AgentState


def extract_products_info(state: AgentState) -> AgentState:
    """
    Usa la chain de extracción estructurada para identificar todos los productos
    descritos por el usuario en los mensajes.
    MERGEA con productos anteriores que ya tienen información completa.
    """
    messages: list[BaseMessage] = state['messages']
    existing_requests = state.get('product_requests', [])
        
    # Solo invocamos con el último mensaje o la colección de mensajes
    try:
        # Usamos la cadena de extracción que retorna ProductList
        product_list_obj = ChainAdministrator().get('extraction_chain').invoke({"messages": messages})
        
        # Convertir a la nueva estructura de seguimiento
        new_product_requests = []
        for product_name in product_list_obj.products:
            new_product_requests.append({
                "name": product_name,
                "info_needed": True,  # Inicialmente se asume que se necesita más info
                "details": {},
                "info_solicitada": ["descripción detallada", "marca", "modelo/número de parte"]
            })
        
        # MERGEAR: mantener productos que ya estaban completos (info_needed=False)
        productos_previos_completos = [
            p for p in existing_requests 
            if not p.get("info_needed", True)
        ]
        
        if productos_previos_completos:
            for p in productos_previos_completos:
                print(f"      - {p.get('name', 'sin nombre')}")
        
        # Combinar: primero los completos previos, luego los nuevos
        product_requests = productos_previos_completos + new_product_requests
        
        return {
            "product_requests": product_requests,
            "product_description": product_list_obj.products  # Mantenemos por si se usa en otra parte
        }
    
    except Exception as e:
        # En caso de error, mantener productos existentes o volver a solicitar información
        return {
            "product_requests": existing_requests if existing_requests else [],
            "messages": [AIMessage(content="❌ Lo siento, no pude identificar los repuestos que necesitas. ¿Podrías ser más específico?")]
        }