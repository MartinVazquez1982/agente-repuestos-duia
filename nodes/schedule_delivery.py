from datetime import datetime, timedelta
from schemas.state import AgentState
from langchain_core.messages import AIMessage

def schedule_delivery(state: AgentState) -> AgentState:
    """
    1. Imprime la agenda de entrega (print directo)
    2. Genera mensaje final del agente resumiendo todo el proceso
    """
    selecciones = state.get("selecciones_usuario", [])
    
    if not selecciones:
        return {
            "messages": [AIMessage(content="❌ No hay productos para agendar")]
        }
    
    # Calcular lead time máximo
    lead_times = []
    for producto in selecciones:
        lead_time = producto.get('lead_time', 1)
        if isinstance(lead_time, (int, float)):
            lead_times.append(int(lead_time))
    
    # Lead time máximo (mínimo 1 día)
    max_lead_time = max(lead_times) if lead_times else 7
    
    # Calcular fechas
    fecha_actual = datetime.now()
    fecha_estimada = fecha_actual + timedelta(days=max_lead_time)
    
    # Separar por tipo
    internos = [s for s in selecciones if s.get('tipo') == 'INTERNO']
    externos = [s for s in selecciones if s.get('tipo') == 'EXTERNO']
    
    # PRINT DIRECTO de la agenda
    print("\n" + "═" * 80)
    print("📅 AGENDANDO FECHA DE ENTREGA EN SISTEMA DE SEGUIMIENTO...")
    print("═" * 80 + "\n")
    print(f"⏰ Fecha de registro: {fecha_actual.strftime('%d/%m/%Y %H:%M')}")
    print(f"📦 FECHA ESTIMADA DE ENTREGA: {fecha_estimada.strftime('%d/%m/%Y')}")
    print(f"⏱️  Lead time máximo: {max_lead_time} día{'s' if max_lead_time != 1 else ''}\n")
    print("✅ Fecha agendada exitosamente en el sistema")
    print("═" * 80 + "\n")
    
    # GENERAR MENSAJE DEL AGENTE (sin LLM, template simple)
    mensaje = _generar_resumen_final(internos, externos, fecha_estimada, max_lead_time)
    
    return {
        "messages": [AIMessage(content=mensaje)]
    }


def _generar_resumen_final(internos, externos, fecha_estimada, max_lead_time):
    """
    Genera el resumen final sin necesidad de LLM.
    Template simple con la información del pedido.
    """
    mensaje = "✅ **Proceso completado exitosamente**\n\n"
    mensaje += "📋 **Resumen de acciones realizadas:**\n\n"
    
    # Resumen de productos internos
    if internos:
        mensaje += f"✅ **Orden de compra interna generada** para {len(internos)} producto{'s' if len(internos) != 1 else ''}\n"
        codigos_internos = [p.get('codigo', 'N/A') for p in internos]
        mensaje += f"   • Códigos: {', '.join(codigos_internos)}\n"
        
        # Calcular valor total internos
        total_internos = sum(p.get('precio', 0) for p in internos)
        mensaje += f"   • Valor: ${total_internos:.2f}\n\n"
    
    # Resumen de productos externos
    if externos:
        mensaje += f"✅ **Email de cotización enviado** a proveedores externos para {len(externos)} producto{'s' if len(externos) != 1 else ''}\n"
        codigos_externos = [p.get('codigo', 'N/A') for p in externos]
        mensaje += f"   • Códigos: {', '.join(codigos_externos)}\n"
        
        # Mostrar proveedores únicos
        proveedores = list(set(p.get('proveedor', 'N/A') for p in externos))
        mensaje += f"   • Proveedores: {', '.join(proveedores)}\n\n"
    
    # Fecha de entrega
    mensaje += f"✅ **Fecha de entrega agendada:** {fecha_estimada.strftime('%d/%m/%Y')}\n"
    mensaje += f"   • Tiempo estimado: {max_lead_time} día{'s' if max_lead_time != 1 else ''}\n\n"
    
    # Valor total
    total_general = sum(p.get('precio', 0) for p in (internos + externos))
    mensaje += f"💰 **Valor total del pedido:** ${total_general:.2f}\n\n"
    
    # Próximos pasos
    mensaje += "🔔 **Próximos pasos:**\n"
    if internos:
        mensaje += "   • Los productos internos están siendo preparados en almacén\n"
    if externos:
        mensaje += "   • Esperando confirmación de disponibilidad de proveedores externos\n"
    mensaje += "   • Recibirás notificaciones automáticas sobre el estado del pedido\n"
    mensaje += "   • El tracking estará disponible en tu panel de seguimiento"
    
    return mensaje
