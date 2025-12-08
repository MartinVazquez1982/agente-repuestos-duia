from schemas.state import AgentState

def process_internal_order(state: AgentState) -> AgentState:
    """
    Imprime orden de compra interna para productos INTERNOS.
    NO agrega mensajes al state, solo hace print directo.
    """
    selecciones = state.get("selecciones_usuario", [])
    internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
    
    if not internos:
        return {}
    
    # Agrupar por almacén
    por_almacen = {}
    for prod in internos:
        almacen = prod.get('proveedor', 'Almacén General')
        if almacen not in por_almacen:
            por_almacen[almacen] = []
        por_almacen[almacen].append(prod)
    
    # PRINT DIRECTO (no mensaje al state)
    print("\n" + "═" * 80)
    print("🖨️  IMPRIMIENDO ORDEN DE COMPRA INTERNA...")
    print("═" * 80 + "\n")
    
    total_general = 0
    
    for almacen, productos in por_almacen.items():
        print(f"🏢 ALMACÉN: {almacen}")
        print("─" * 80)
        
        for i, prod in enumerate(productos, 1):
            precio = prod.get('precio', 0)
            stock = prod.get('stock', 'N/A')
            lead_time = prod.get('lead_time', 1)
            total_general += precio
            
            print(f"\n{i}. {prod['codigo']} - {prod['descripcion']}")
            print(f"   📦 Cantidad: 1 unidad")
            print(f"   💰 Valor: ${precio:.2f}")
            print(f"   📊 Stock disponible: {stock} unidades")
            print(f"   ⏱️  Preparación: {lead_time} día{'s' if lead_time != 1 else ''}")
        
        print()
    
    print(f"💰 VALOR TOTAL: ${total_general:.2f}")
    print("✅ Orden de compra interna generada")
    print("═" * 80 + "\n")
    
    # No retorna mensaje, el resumen lo hará schedule_delivery
    return {}