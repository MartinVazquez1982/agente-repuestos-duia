from typing import List, Dict

def format_options_for_llm(producto_label: str, opciones: List[Dict]) -> str:
    """
    Formatea opciones de repuestos en texto estructurado para presentación al LLM en el ranking.
    """
    if not opciones:
        return f"{producto_label}\nNo hay opciones disponibles.\n"
    
    # Información del repuesto (de la primera opción)
    primera = opciones[0]
    
    texto = f"═══════════════════════════════════════════════════════════════\n"
    texto += f"{producto_label}\n"
    texto += f"═══════════════════════════════════════════════════════════════\n"
    texto += f"\n"
    texto += f"OPCIONES DISPONIBLES ({len(opciones)} total):\n"
    texto += f"───────────────────────────────────────────────────────────────\n"
    
    for i, opcion in enumerate(opciones, 1):
        tipo_emoji = "🏢" if opcion["tipo"] == "INTERNO" else "🌐"
        
        texto += f"\nOpción {i}: {tipo_emoji} {opcion.get('proveedor_nombre', 'N/A')}\n"
        texto += f"  • Código: {opcion.get('id_repuesto', 'N/A')}\n"
        texto += f"  • Descripción: {opcion.get('repuesto_descripcion', 'N/A')}\n"
        texto += f"  • Categoría: {opcion.get('categoria', 'N/A')}\n"
        texto += f"  • Marca: {opcion.get('marca', 'N/A')}\n"
        texto += f"  • Modelo: {opcion.get('modelo', 'N/A')}\n"
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