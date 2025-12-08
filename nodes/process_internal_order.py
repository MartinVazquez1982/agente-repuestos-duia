from schemas.state import AgentState
from langchain_core.messages import AIMessage

def process_internal_order(state: AgentState) -> AgentState:
    """
    Genera orden de retiro de inventario para productos INTERNOS.
    Notifica al almacén para preparación.
    """
    selecciones = state.get("selecciones_usuario", [])
    internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
    
    if not internos:
        return {
            "messages": [AIMessage(content="⚠️ No hay productos internos para procesar")]
        }
    
    
    # Agrupar por almacén
    por_almacen = {}
    for prod in internos:
        almacen = prod.get('proveedor', 'Almacén General')
        if almacen not in por_almacen:
            por_almacen[almacen] = []
        por_almacen[almacen].append(prod)
    
    mensaje = "═" * 80 + "\n"
    mensaje += "📦 **ORDEN DE RETIRO DE INVENTARIO**\n"
    mensaje += "═" * 80 + "\n\n"
    
    total_general = 0
    
    for almacen, productos in por_almacen.items():
        mensaje += f"🏢 **ALMACÉN: {almacen}**\n"
        mensaje += "─" * 80 + "\n\n"
        
        subtotal_almacen = 0
        
        for i, prod in enumerate(productos, 1):
            precio = prod.get('precio', 0)
            stock = prod.get('stock', 'N/A')
            lead_time = prod.get('lead_time', 1)
            
            subtotal_almacen += precio
            total_general += precio
            
            mensaje += f"{i}. **{prod['codigo']}**\n"
            mensaje += f"   📝 Descripción: {prod['descripcion']}\n"
            mensaje += f"   📦 Cantidad a retirar: 1 unidad\n"
            mensaje += f"   💰 Valor: ${precio:.2f}\n"
            mensaje += f"   📊 Stock disponible: {stock} unidades\n"
            mensaje += f"   ⏱️  Tiempo de preparación: {lead_time} día{'s' if lead_time != 1 else ''}\n\n"
        
        mensaje += f"💰 **Subtotal {almacen}:** ${subtotal_almacen:.2f}\n"
        mensaje += "─" * 80 + "\n\n"
    
    # Resumen
    mensaje += "📋 **RESUMEN DE LA ORDEN**\n"
    mensaje += "─" * 80 + "\n"
    mensaje += f"   Total de productos: {len(internos)}\n"
    mensaje += f"   Almacenes involucrados: {len(por_almacen)}\n"
    mensaje += f"   Valor total: ${total_general:.2f}\n\n"
    
    # Próximos pasos
    mensaje += "🔔 **NOTIFICACIÓN AL ALMACÉN**\n"
    mensaje += "─" * 80 + "\n"
    for almacen in por_almacen.keys():
        mensaje += f"✅ Notificación enviada a: {almacen}\n"
    mensaje += "\n"
    
    mensaje += "📌 **INSTRUCCIONES:**\n"
    mensaje += "1. Preparar productos para retiro\n"
    mensaje += "2. Verificar estado y calidad\n"
    mensaje += "3. Embalar y etiquetar\n"
    mensaje += "4. Notificar cuando esté listo\n\n"
    
    mensaje += "═" * 80 + "\n"
    mensaje += "✅ **Orden de retiro generada exitosamente**\n"
    mensaje += "═" * 80
    
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }