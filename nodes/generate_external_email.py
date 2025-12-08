from schemas.state import AgentState
from langchain_core.messages import AIMessage

def generate_external_email(state: AgentState) -> AgentState:
    """
    Genera email automatizado para proveedores EXTERNOS.
    Formaliza el pedido de productos.
    """
    selecciones = state.get("selecciones_usuario", [])
    externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
    
    if not externos:
        return {
            "messages": [AIMessage(content="⚠️ No hay productos externos para procesar")]
        }
    
    
    # Agrupar por proveedor
    por_proveedor = {}
    for prod in externos:
        proveedor = prod.get('proveedor', 'Proveedor Desconocido')
        if proveedor not in por_proveedor:
            por_proveedor[proveedor] = []
        por_proveedor[proveedor].append(prod)
    
    mensaje = "═" * 80 + "\n"
    mensaje += "📧 **EMAILS GENERADOS PARA PROVEEDORES**\n"
    mensaje += "═" * 80 + "\n\n"
    
    for proveedor, productos in por_proveedor.items():
        mensaje += "─" * 80 + "\n"
        mensaje += f"**PARA: {proveedor}**\n"
        mensaje += "─" * 80 + "\n\n"
        
        # Formato de email
        mensaje += "```\n"
        mensaje += f"Para: {proveedor}\n"
        mensaje += "Asunto: Solicitud de Cotización y Pedido - Repuestos Industriales\n\n"
        mensaje += "Estimado proveedor,\n\n"
        mensaje += "Por medio de la presente, solicitamos cotización y disponibilidad para los siguientes repuestos:\n\n"
        
        total_proveedor = 0
        
        mensaje += "DETALLE DEL PEDIDO:\n"
        mensaje += "-" * 60 + "\n\n"
        
        for i, prod in enumerate(productos, 1):
            precio = prod.get('precio', 0)
            lead_time = prod.get('lead_time', 'N/A')
            
            total_proveedor += precio
            
            mensaje += f"{i}. Código: {prod['codigo']}\n"
            mensaje += f"   Descripción: {prod['descripcion']}\n"
            mensaje += f"   Cantidad solicitada: 1 unidad\n"
            mensaje += f"   Precio estimado: ${precio:.2f}\n"
            mensaje += f"   Lead time estimado: {lead_time} días\n\n"
        
        mensaje += "-" * 60 + "\n"
        mensaje += f"TOTAL ESTIMADO: ${total_proveedor:.2f}\n\n"
        
        mensaje += "INFORMACIÓN ADICIONAL:\n"
        mensaje += "- Forma de pago: A convenir\n"
        mensaje += "- Plazo de entrega: Según disponibilidad\n"
        mensaje += "- Dirección de entrega: A coordinar\n\n"
        
        mensaje += "Por favor, confirmen:\n"
        mensaje += "1. Disponibilidad de los productos\n"
        mensaje += "2. Precio final actualizado\n"
        mensaje += "3. Tiempo de entrega real\n"
        mensaje += "4. Condiciones comerciales\n\n"
        
        mensaje += "Quedamos a la espera de su pronta respuesta.\n\n"
        mensaje += "Saludos cordiales,\n"
        mensaje += "Departamento de Compras\n"
        mensaje += "```\n\n"
        
        mensaje += f"✅ Email preparado para: **{proveedor}**\n"
        mensaje += f"📊 Productos solicitados: {len(productos)}\n"
        mensaje += f"💰 Total estimado: ${total_proveedor:.2f}\n\n"
    
    mensaje += "═" * 80 + "\n"
    mensaje += f"📧 **{len(por_proveedor)} email(s) generado(s) exitosamente**\n"
    mensaje += "═" * 80 + "\n\n"
    
    mensaje += "🔔 **PRÓXIMOS PASOS:**\n"
    mensaje += "1. Revisar y enviar emails a proveedores\n"
    mensaje += "2. Esperar confirmación de disponibilidad\n"
    mensaje += "3. Negociar condiciones comerciales\n"
    mensaje += "4. Formalizar pedido\n"
    mensaje += "5. Coordinar logística de entrega\n"
        
    return {
        "messages": [AIMessage(content=mensaje)]
    }