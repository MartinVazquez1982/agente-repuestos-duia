from schemas.state import AgentState

def generate_external_email(state: AgentState) -> AgentState:
    """
    Imprime emails de cotización para proveedores EXTERNOS agrupados por proveedor (solo print, sin mensajes al state).
    """
    selecciones = state.get("selecciones_usuario", [])
    externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
    
    if not externos:
        return {}
    
    # Agrupar por proveedor
    por_proveedor = {}
    for prod in externos:
        proveedor = prod.get('proveedor', 'Proveedor Desconocido')
        if proveedor not in por_proveedor:
            por_proveedor[proveedor] = []
        por_proveedor[proveedor].append(prod)
    
    # PRINT DIRECTO (no mensaje al state)
    print("\n" + "═" * 80)
    print("📧 IMPRIMIENDO EMAIL PARA PROVEEDORES EXTERNOS (No es respuesta del agente al usuario)...")
    print("═" * 80 + "\n")
    
    for proveedor, productos in por_proveedor.items():
        print(f"📬 DESTINATARIO: {proveedor}")
        print("─" * 80)
        print("ASUNTO: Solicitud de Cotización - Repuestos Industriales\n")
        
        total_proveedor = 0
        
        for i, prod in enumerate(productos, 1):
            precio = prod.get('precio', 0)
            cantidad = prod.get('cantidad', 1)
            lead_time = prod.get('lead_time', 'N/A')
            
            valor_total = precio * cantidad
            total_proveedor += valor_total
            
            print(f"{i}. {prod['codigo']} - {prod['descripcion']}")
            print(f"   Cantidad solicitada: {cantidad} unidad{'es' if cantidad != 1 else ''}")
            print(f"   Precio unitario referencia: ${precio:.2f}")
            print(f"   Subtotal: ${valor_total:.2f}")
            print(f"   Lead time estimado: {lead_time} días\n")
        
        print(f"💰 Total estimado: ${total_proveedor:.2f}")
        print(f"✅ Email generado para: {proveedor}\n")
    
    print(f"📧 {len(por_proveedor)} email(s) generado(s) exitosamente")
    print("═" * 80 + "\n")
    
    # No retorna mensaje, el resumen lo hará schedule_delivery
    return {}