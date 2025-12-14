from schemas.state import AgentState
from langchain_core.messages import AIMessage, HumanMessage
from chains.chain_administrator import ChainAdministrator
from schemas.structure_outputs import UserSelectionIntent

def find_codigo_in_results(codigo: str, resultados_por_producto: dict) -> tuple:
    """
    Busca un código en resultados agrupados; retorna (info_opcion, idx_producto) o (None, None).
    """
    for idx_producto, opciones in resultados_por_producto.items():
        for opcion in opciones:
            if opcion.get('id_repuesto') == codigo:
                return opcion, idx_producto
    return None, None

def process_user_selection(state: AgentState) -> AgentState:
    """
    Interpreta selección del usuario con LLM, valida códigos y determina tipo de orden (interno/externo/mixto).
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
        # Fallback a regex simple con cantidades
        import re
        # Patrón: captura cantidad (opcional) + código
        # Ejemplos: "3 R-0001", "R-0001 x5", "R-0001 (10)", "5 unidades de R-0001"
        patron = r'(?:(\d+)\s*(?:unidades?\s+(?:de|del)\s+|del\s+|x\s*)?)?([Rr]-\d{4})(?:\s*[x×]\s*(\d+)|\s*\((\d+)\)|(?:\s+por\s+(\d+)))?'
        matches = re.findall(patron, user_message)
        
        productos_seleccionados = []
        for match in matches:
            cantidad_antes, codigo, cantidad_x, cantidad_paren, cantidad_por = match
            codigo = codigo.upper()
            
            # Determinar cantidad de cualquier formato
            cantidad = 1
            if cantidad_antes:
                cantidad = int(cantidad_antes)
            elif cantidad_x:
                cantidad = int(cantidad_x)
            elif cantidad_paren:
                cantidad = int(cantidad_paren)
            elif cantidad_por:
                cantidad = int(cantidad_por)
            
            productos_seleccionados.append({
                "codigo": codigo,
                "cantidad": max(1, cantidad)  # Asegurar mínimo 1
            })
        
        if productos_seleccionados:
            from schemas.structure_outputs import ProductSelection
            interpretation = UserSelectionIntent(
                accion="seleccionar_codigos",
                productos_seleccionados=[ProductSelection(**p) for p in productos_seleccionados],
                confianza=0.7,
                razon="Fallback a regex"
            )
        else:
            interpretation = UserSelectionIntent(
                accion="no_entendido",
                productos_seleccionados=[],
                confianza=0.3,
                razon="Error en interpretación"
            )
    
    # Procesar según la acción interpretada
    if interpretation.accion == "cancelar":   
        mensaje = "❌ **Pedido cancelado**\n\n"
        mensaje += "Entendido, no se procesará ningún pedido."
        
        return {
            "messages": [AIMessage(content=mensaje)],
            "selecciones_usuario": [],
            "repuestos_seleccionados": True
        }
    
    elif interpretation.accion == "confirmar_todo":
        # Crear productos_seleccionados con cantidad = 1 para todos
        from schemas.structure_outputs import ProductSelection
        productos_seleccionados = [
            ProductSelection(codigo=cod, cantidad=1) for cod in codigos_disponibles
        ]
        
    elif interpretation.accion == "seleccionar_codigos":
        productos_mencionados = interpretation.productos_seleccionados
        
        # Validar que los códigos existan en el ranking
        codigos_mencionados = [p.codigo for p in productos_mencionados]
        codigos_invalidos = [c for c in codigos_mencionados if c not in codigos_disponibles]
        productos_validos = [p for p in productos_mencionados if p.codigo in codigos_disponibles]
        
        if codigos_invalidos:
            mensaje = f"❌ **Códigos no válidos**\n\n"
            mensaje += f"Los siguientes códigos NO están en el ranking:\n"
            for codigo in codigos_invalidos:
                mensaje += f"   • **{codigo}**\n"
            
            mensaje += f"\n✅ **Opciones disponibles:**\n\n"
            for codigo in codigos_disponibles:
                # Buscar el código en los resultados internos o externos
                info_interno, _ = find_codigo_in_results(codigo, resultados_internos)
                info_externo, _ = find_codigo_in_results(codigo, resultados_externos)
                
                if info_interno:
                    info = info_interno
                    tipo = "INTERNO"
                elif info_externo:
                    info = info_externo
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
        
        if not productos_validos:
            mensaje = "❓ No detecté ningún código válido. Por favor especifica uno de los códigos del ranking."
            return {
                "messages": [AIMessage(content=mensaje)],
                "repuestos_seleccionados": False
            }
        
        productos_seleccionados = productos_validos
    
    else:  # no_entendido
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
    selecciones_detalladas = []
    
    for producto in productos_seleccionados:
        codigo = producto.codigo
        cantidad = producto.cantidad
        
        # Buscar el código en los resultados internos o externos
        info_interno, idx_interno = find_codigo_in_results(codigo, resultados_internos)
        info_externo, idx_externo = find_codigo_in_results(codigo, resultados_externos)
        
        if info_interno:
            tipo = "INTERNO"
            info = info_interno
            tiene_internos = True
        elif info_externo:
            tipo = "EXTERNO"
            info = info_externo
            tiene_externos = True
        else:
            continue
        
        desc = info.get('repuesto_descripcion', 'N/A')
        marca = info.get('marca', 'N/A')
        proveedor = info.get('proveedor_nombre', 'N/A')
        stock = info.get('stock_disponible', 0)
                
        mensaje_final += f"📦 **{codigo}** x{cantidad} - {tipo}\n"
        mensaje_final += f"   └─ {desc}\n"
        mensaje_final += f"   └─ Marca: {marca}\n"
        mensaje_final += f"   └─ Proveedor: {proveedor}\n"
        
        # Advertencia de stock si es interno
        if tipo == "INTERNO" and stock < cantidad:
            mensaje_final += f"   ⚠️  Stock disponible: {stock}/{cantidad} unidades (insuficiente)\n"
        elif tipo == "INTERNO":
            mensaje_final += f"   ✅ Stock disponible: {stock}/{cantidad} unidades\n"
        
        mensaje_final += "\n"
        
        # Guardar selección detallada
        selecciones_detalladas.append({
            "codigo": codigo,
            "cantidad": cantidad,
            "tipo": tipo,
            "descripcion": desc,
            "marca": marca,
            "proveedor": proveedor,
            "precio": info.get('costo_unitario', 0),
            "stock": info.get('stock_disponible', 0),
            "lead_time": info.get('lead_time_dias', 0)
        })
    
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
        "selecciones_usuario": selecciones_detalladas,
        "repuestos_seleccionados": True,
        "tipo_orden": tipo_orden
    }