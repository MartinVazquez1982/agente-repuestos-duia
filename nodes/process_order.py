from schemas.state import AgentState
from langchain_core.messages import AIMessage

def process_order(state: AgentState) -> AgentState:
    """
    Genera resumen detallado de orden con productos internos/externos, precios y tiempos de entrega.
    """
    selecciones = state.get("selecciones_usuario", [])
    
    if not selecciones:
        return {
            "messages": [AIMessage(content="❌ No hay productos seleccionados para procesar")]
        }
        
    # Separar por tipo
    internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
    externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
    
    # Agrupar externos por proveedor
    externos_por_proveedor = {}
    for ext in externos:
        prov = ext.get('proveedor', 'Desconocido')
        if prov not in externos_por_proveedor:
            externos_por_proveedor[prov] = []
        externos_por_proveedor[prov].append(ext)
    
    mensaje = "═" * 80 + "\n"
    mensaje += "📋 **ORDEN DE COMPRA GENERADA**\n"
    mensaje += "═" * 80 + "\n\n"
    
    # PRODUCTOS INTERNOS
    if internos:
        mensaje += "🏢 **PRODUCTOS INTERNOS (Almacén)**\n"
        mensaje += "─" * 80 + "\n"
        
        total_interno = 0
        lead_time_max_interno = 0
        
        for i, prod in enumerate(internos, 1):
            precio = prod.get('precio', 0)
            stock = prod.get('stock', 'N/A')
            lead_time = prod.get('lead_time', 0)
            
            total_interno += precio
            if isinstance(lead_time, (int, float)):
                lead_time_max_interno = max(lead_time_max_interno, int(lead_time))
            
            mensaje += f"{i}. **{prod['codigo']}** - {prod['descripcion']}\n"
            mensaje += f"   • Almacén: {prod['proveedor']}\n"
            mensaje += f"   • Cantidad: 1\n"
            mensaje += f"   • Precio unitario: ${precio:.2f}\n"
            mensaje += f"   • Stock disponible: {stock}\n"
            mensaje += f"   • Subtotal: ${precio:.2f}\n\n"
        
        mensaje += f"📊 **Total INTERNO:** ${total_interno:.2f}\n"
        mensaje += f"⏱️  **Disponibilidad:** Inmediata ({lead_time_max_interno} día{'s' if lead_time_max_interno != 1 else ''})\n\n"
        mensaje += "─" * 80 + "\n\n"
    
    # PRODUCTOS EXTERNOS
    if externos:
        mensaje += "🌐 **PRODUCTOS EXTERNOS (Proveedores)**\n"
        mensaje += "─" * 80 + "\n"
        
        total_externo = 0
        lead_time_max_externo = 0
        
        for proveedor, productos in externos_por_proveedor.items():
            mensaje += f"**PROVEEDOR: {proveedor}**\n"
            mensaje += "─" * 80 + "\n"
            
            for i, prod in enumerate(productos, 1):
                precio = prod.get('precio', 0)
                lead_time = prod.get('lead_time', 0)
                
                total_externo += precio
                if isinstance(lead_time, (int, float)):
                    lead_time_max_externo = max(lead_time_max_externo, int(lead_time))
                
                mensaje += f"{i}. **{prod['codigo']}** - {prod['descripcion']}\n"
                mensaje += f"   • Cantidad: 1\n"
                mensaje += f"   • Precio unitario: ${precio:.2f}\n"
                mensaje += f"   • Subtotal: ${precio:.2f}\n"
                mensaje += f"   • Lead time: {lead_time} días\n\n"
            
        mensaje += f"📊 **Total EXTERNO:** ${total_externo:.2f}\n"
        mensaje += f"⏱️  **Lead time estimado:** {lead_time_max_externo} días\n\n"
        mensaje += "─" * 80 + "\n\n"
    
    # RESUMEN FINANCIERO
    total_general = sum(p.get('precio', 0) for p in selecciones)
    
    mensaje += "💰 **RESUMEN FINANCIERO**\n"
    mensaje += "─" * 80 + "\n"
    if internos:
        total_int = sum(p.get('precio', 0) for p in internos)
        mensaje += f"   Productos internos: ${total_int:.2f}\n"
    if externos:
        total_ext = sum(p.get('precio', 0) for p in externos)
        mensaje += f"   Productos externos: ${total_ext:.2f}\n"
    mensaje += "   " + "─" * 30 + "\n"
    mensaje += f"   **TOTAL ESTIMADO:**    **${total_general:.2f}**\n\n"
    
    # TIEMPOS DE ENTREGA
    mensaje += "📅 **TIEMPOS DE ENTREGA**\n"
    mensaje += "─" * 80 + "\n"
    if internos:
        lead_interno = max((int(p.get('lead_time', 0)) for p in internos if isinstance(p.get('lead_time'), (int, float))), default=1)
        almacen = internos[0].get('proveedor', 'Almacén')
        mensaje += f"   • Internos: {lead_interno} día{'s' if lead_interno != 1 else ''} ({almacen})\n"
    if externos:
        lead_externo = max((int(p.get('lead_time', 0)) for p in externos if isinstance(p.get('lead_time'), (int, float))), default=0)
        mensaje += f"   • Externos: {lead_externo} días\n"
    
    lead_max = max(
        max((int(p.get('lead_time', 0)) for p in internos if isinstance(p.get('lead_time'), (int, float))), default=0) if internos else 0,
        max((int(p.get('lead_time', 0)) for p in externos if isinstance(p.get('lead_time'), (int, float))), default=0) if externos else 0
    )
    mensaje += f"   • **Lead time máximo:** {lead_max} días\n\n"
    
    # PRÓXIMOS PASOS
    mensaje += "🔔 **PRÓXIMOS PASOS**\n"
    mensaje += "─" * 80 + "\n"
    paso = 1
    if internos:
        mensaje += f"{paso}. ✅ Reservar productos internos en almacén\n"
        paso += 1
    if externos:
        mensaje += f"{paso}. 📧 Enviar orden de compra a proveedor{'es' if len(externos_por_proveedor) > 1 else ''} externo{'s' if len(externos_por_proveedor) > 1 else ''}\n"
        paso += 1
    mensaje += f"{paso}. 📦 Coordinar logística de entrega\n"
    mensaje += f"{paso+1}. 💳 Procesar pago: ${total_general:.2f}\n\n"
    
    mensaje += "═" * 80 + "\n"
    mensaje += "✅ **Orden lista para procesar**\n"
    mensaje += "═" * 80
    
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }