from langchain_core.messages import AIMessage, BaseMessage
from chains.chain_administrator import ChainAdministrator
from schemas.state import AgentState

def check_product_info_completeness(state: AgentState) -> AgentState:
    """
    Valida con LLM si cada producto tiene info suficiente; retorna info_completa=True solo si todos están completos.
    """
    product_requests = state.get('product_requests', [])
    
    if not product_requests:
        return {
            "info_completa": False,
            "messages": [AIMessage(content="No se identificaron productos para buscar.")]
        }
    
    productos_incompletos = []
    productos_completos = []
    
    # Verificar CADA producto con el LLM
    for idx, product in enumerate(product_requests, 1):
        product_name = product.get("name", "")
        cantidad = product.get("cantidad", 1)
        
        try:
            # Invocar LLM para verificar este producto
            verificacion = ChainAdministrator().get('verify_product_chain').invoke({"product_name": product_name})
            
            # Actualizar el product_request con el resultado
            product["info_needed"] = not verificacion.info_completa
            product["verificacion"] = {
                "completa": verificacion.info_completa,
                "razon": verificacion.razon,
                "faltante": verificacion.info_faltante
            }
            
            if verificacion.info_completa:
                productos_completos.append({
                    "idx": idx,
                    "nombre": product_name,
                    "cantidad": cantidad,
                    "razon": verificacion.razon
                })

            else:
                productos_incompletos.append({
                    "idx": idx,
                    "nombre": product_name,
                    "cantidad": cantidad,
                    "razon": verificacion.razon,
                    "faltante": verificacion.info_faltante
                })
                
        except Exception as e:
            # Por defecto, marcar como incompleto si hay error
            product["info_needed"] = True
            productos_incompletos.append({
                "idx": idx,
                "nombre": product_name,
                "cantidad": cantidad,
                "razon": "Error al verificar",
                "faltante": ["detalles"]
            })
    
    # DECISIÓN: Si ALGÚN producto está incompleto → pedir más info
    if productos_incompletos:
        mensaje = "⚠️  Necesito más detalles sobre algunos productos:\n\n"
        
        for item in productos_incompletos:
            mensaje += f"**{item['idx']}. {item['nombre']}**\n"
            mensaje += f"   ❌ {item['razon']}\n"
            if item['faltante']:
                mensaje += f"   📝 Por favor especifica: {', '.join(item['faltante'])}\n"
            mensaje += "\n"
        
        mensaje += "💡 **Ejemplos de descripciones completas:**\n"
        mensaje += "   • 'Rodamiento rígido de bolas 6204'\n"
        mensaje += "   • 'Filtro de aceite Bosch'\n"
        mensaje += "   • 'Bomba centrífuga Parker'\n"
        mensaje += "   • 'Correa trapezoidal SKF'\n\n"
        mensaje += "Por favor, proporciona más detalles de los productos incompletos."
        
        return {
            "info_completa": False,
            "product_requests": product_requests,  # Actualizado con flags
            "messages": [AIMessage(content=mensaje)]
        }
    else:        
        mensaje = "✅ Perfecto, tengo información suficiente para buscar:\n\n"
        for item in productos_completos:
            mensaje += f"   {item['idx']}. {item['nombre']}\n"
        mensaje += "\n🔍 Iniciando búsqueda en el catálogo..."
        
        return {
            "info_completa": True,
            "product_requests": product_requests,
            "messages": [AIMessage(content=mensaje)]
        }
