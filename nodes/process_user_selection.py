from schemas.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage
from chains.chain_administrator import ChainAdministrator
from schemas.structure_outputs import UserSelectionIntent

def process_user_selection(state: AgentState) -> AgentState:
    """
    Procesa la selección del usuario usando LLM para interpretar su intención.
    Valida que los códigos seleccionados estén en el ranking.
    Determina si son productos internos o externos.
    """
    messages = state.get("messages", [])
    codigos_disponibles = state.get("codigos_repuestos", [])
    resultados_internos = state.get("resultados_internos", {})
    resultados_externos = state.get("resultados_externos", {})
    
    # Obtener el último mensaje del usuario
    user_message = None
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_message = msg.content.strip()
            break
    
    if not user_message:
        return {
            "messages": [AIMessage(content="❌ No recibí tu selección. ¿Podrías responder de nuevo?")],
            "repuestos_seleccionados": False
        }
    
    
    # Usar LLM para interpretar la intención del usuario
    try:
        interpretation = ChainAdministrator().get("selection_interpretation_chain").invoke({
            "codigos_disponibles": ", ".join(codigos_disponibles),
            "user_message": user_message
        })
        
    except Exception as e:
        print(f"❌ Error al interpretar con LLM: {e}")
        # Fallback a regex simple
        import re
        codigos_mencionados = re.findall(r'R-\d{4}', user_message.upper())
        if codigos_mencionados:
            interpretation = UserSelectionIntent(
                accion="seleccionar_codigos",
                codigos_seleccionados=codigos_mencionados,
                confianza=0.7,
                razon="Fallback a regex"
            )
        else:
            interpretation = UserSelectionIntent(
                accion="no_entendido",
                codigos_seleccionados=[],
                confianza=0.3,
                razon="Error en interpretación"
            )
    
    # Procesar según la acción interpretada
    if interpretation.accion == "cancelar":
        print(f"❌ Usuario canceló el pedido")
        
        mensaje = "❌ **Pedido cancelado**\n\n"
        mensaje += "Entendido, no se procesará ningún pedido.\n"
        mensaje += "¿Hay algo más en lo que pueda ayudarte?"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "selecciones_usuario": [],
            "repuestos_seleccionados": True
        }
    
    elif interpretation.accion == "confirmar_todo":
        print(f"✅ Usuario confirmó todas las opciones")
        codigos_validos = codigos_disponibles
        
    elif interpretation.accion == "seleccionar_codigos":
        codigos_mencionados = interpretation.codigos_seleccionados
        print(f"📋 Códigos seleccionados: {codigos_mencionados}")
        
        # Validar que los códigos existan en el ranking
        codigos_invalidos = [c for c in codigos_mencionados if c not in codigos_disponibles]
        codigos_validos = [c for c in codigos_mencionados if c in codigos_disponibles]
        
        if codigos_invalidos:
            print(f"⚠️  Códigos inválidos: {codigos_invalidos}")
            
            mensaje = f"❌ **Códigos no válidos**\n\n"
            mensaje += f"Los siguientes códigos NO están en el ranking:\n"
            for codigo in codigos_invalidos:
                mensaje += f"   • **{codigo}**\n"
            
            mensaje += f"\n✅ **Opciones disponibles:**\n\n"
            for codigo in codigos_disponibles:
                info_interno = resultados_internos.get(codigo, [])
                info_externo = resultados_externos.get(codigo, [])
                
                if info_interno:
                    info = info_interno[0]
                    tipo = "INTERNO"
                elif info_externo:
                    info = info_externo[0]
                    tipo = "EXTERNO"
                else:
                    continue
                
                desc = info.get('repuesto_descripcion', 'N/A')
                proveedor = info.get('proveedor_nombre', 'N/A')
                mensaje += f"   • **{codigo}** ({tipo})\n"
                mensaje += f"      └─ {desc}\n"
                mensaje += f"      └─ {proveedor}\n\n"
            
            mensaje += "Por favor selecciona códigos válidos del ranking."
            return {
                "messages": [AIMessage(content=mensaje)],
                "repuestos_seleccionados": False
            }
        
        if not codigos_validos:
            mensaje = "❓ No detecté ningún código válido. Por favor especifica uno de los códigos del ranking."
            return {
                "messages": [AIMessage(content=mensaje)],
                "repuestos_seleccionados": False
            }
    
    else:  # no_entendido
        print(f"❓ No se pudo interpretar la respuesta")
        mensaje = "❓ **No entendí tu respuesta**\n\n"
        mensaje += "Por favor indica:\n"
        mensaje += "• **'confirmar'** - Para proceder con todas las opciones\n"
        mensaje += "• **'cancelar'** - Para no hacer pedido\n"
        mensaje += f"• **[código]** - Para seleccionar específicos\n\n"
        mensaje += "**Códigos disponibles:**\n"
        for codigo in codigos_disponibles:
            mensaje += f"   • {codigo}\n"
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "repuestos_seleccionados": False
        }
    
    
    mensaje_final = "✅ **Pedido confirmado**\n\n"
    
    tiene_internos = False
    tiene_externos = False
    
    for codigo in codigos_validos:
        info_interno = resultados_internos.get(codigo, [])
        info_externo = resultados_externos.get(codigo, [])
        
        if info_interno:
            tipo = "INTERNO"
            info = info_interno[0]
            tiene_internos = True
        elif info_externo:
            tipo = "EXTERNO"
            info = info_externo[0]
            tiene_externos = True
        else:
            continue
        
        desc = info.get('repuesto_descripcion', 'N/A')
        marca = info.get('marca', 'N/A')
        proveedor = info.get('proveedor_nombre', 'N/A')
                
        mensaje_final += f"📦 **{codigo}** - {tipo}\n"
        mensaje_final += f"   └─ {desc}\n"
        mensaje_final += f"   └─ Marca: {marca}\n"
        mensaje_final += f"   └─ Proveedor: {proveedor}\n\n"
    
    # Determinar tipo de orden
    if tiene_internos and tiene_externos:
        tipo_orden = "both"
    elif tiene_internos:
        tipo_orden = "internal_only"
    else:
        tipo_orden = "external_only"
        
    mensaje_final += "─" * 60 + "\n"
    mensaje_final += "🔄 Procesando tu pedido...\n"
    
    return {
        "messages": [AIMessage(content=mensaje_final)],
        "selecciones_usuario": [{"codigo": c, "tipo": tipo_orden} for c in codigos_validos],
        "repuestos_seleccionados": True,
        "tipo_orden": tipo_orden
    }