from typing import List, Dict

def format_options_for_llm(codigo: str, opciones: List[Dict]) -> str:
    """
    Formatea las opciones de un repuesto para que el LLM las rankee.
    Presenta TODAS las opciones sin orden previo.
    """
    if not opciones:
        return f"REPUESTO: {codigo}\nNo hay opciones disponibles.\n"
    
    # Información del repuesto (de la primera opción)
    primera = opciones[0]
    
    texto = f"═══════════════════════════════════════════════════════════════\n"
    texto += f"REPUESTO: {codigo}\n"
    texto += f"═══════════════════════════════════════════════════════════════\n"
    texto += f"Descripción: {primera.get('repuesto_descripcion', 'N/A')}\n"
    texto += f"Categoría: {primera.get('categoria', 'N/A')}\n"
    texto += f"Marca: {primera.get('marca', 'N/A')}\n"
    texto += f"Modelo: {primera.get('modelo', 'N/A')}\n"
    texto += f"Vida útil estimada: {primera.get('tiempo_vida_estimado_hrs', 'N/A')} horas\n"
    texto += f"\n"
    texto += f"OPCIONES DISPONIBLES ({len(opciones)} total):\n"
    texto += f"───────────────────────────────────────────────────────────────\n"
    
    for i, opcion in enumerate(opciones, 1):
        tipo_emoji = "🏢" if opcion["tipo"] == "INTERNO" else "🌐"
        
        texto += f"\nOpción {i}: {tipo_emoji} {opcion.get('proveedor_nombre', 'N/A')}\n"
        texto += f"  • Tipo: {opcion['tipo']}\n"
        texto += f"  • Proveedor ID: {opcion.get('proveedor_id', 'N/A')}\n"
        texto += f"  • Rating: {opcion.get('proveedor_rating', 0)}/5 estrellas\n"
        texto += f"  • Precio: {opcion.get('moneda', '')} {opcion.get('costo_unitario', 'N/A')}\n"
        texto += f"  • Stock disponible: {opcion.get('stock_disponible', 0)} unidades\n"
        texto += f"  • Lead time: {opcion.get('lead_time_dias', 'N/A')} días\n"
        texto += f"  • Ubicación: {opcion.get('ubicacion_stock', 'N/A')}\n"
        texto += f"  • Cantidad mínima de pedido: {opcion.get('cantidad_minima_pedido', 'N/A')} unidades\n"
        
        if opcion.get('nota'):
            texto += f"  • Nota importante: {opcion.get('nota')}\n"
    
    texto += f"\n"
    
    return texto