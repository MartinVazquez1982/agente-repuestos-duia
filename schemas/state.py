from typing import TypedDict, Optional, List, Dict, Annotated
from langgraph.graph.message import add_messages
from schemas.structure_outputs import ValidationRequest, ConversationResult
from schemas.repuesto import Repuesto

#Definimos el esquema mejorado
class AgentState(TypedDict):
    validation_result: ValidationRequest
    conversation_result: Optional[ConversationResult]  # Resultado del análisis conversacional
    messages: Annotated[list, add_messages]
    product_description: List[str]
    product_requests: Optional[List[Dict]]  # Lista de productos con tracking de info completa
    codigos_repuestos: Optional[List[str]]  # Lista de códigos únicos (R-XXXX)
    repuestos_encontrados: Optional[List[Repuesto]]  # Lista de objetos Repuesto con todas las variantes
    productos_sin_match_interno: Optional[List[Dict]]  # Productos que no se encontraron internamente
    info_completa: bool  # Si tenemos toda la información necesaria

    # Query optimizada para búsqueda semántica
    optimized_query: Optional[str]  # Query reformulada por el LLM

    # Resultados de búsqueda semántica
    semantic_results: Optional[List[Dict]]  # Candidatos de búsqueda semántica

    # Resultados de la búsqueda interna (agrupados por índice de producto solicitado)
    resultados_internos: Optional[Dict[int, List[Dict]]]  
    
    # Resultados de la búsqueda externa (agrupados por índice de producto solicitado)
    resultados_externos: Optional[Dict[int, List[Dict]]]

    # Análisis de disponibilidad por código
    disponibilidad: Optional[Dict[str, str]]  # {"R-0001": "full", "R-0002": "none"}
    codigos_para_externos: Optional[List[str]]

    # Reranking
    recomendaciones_llm: Optional[str]
    
    # Human in the loop
    selecciones_usuario: Optional[List[Dict]]  # Selecciones del usuario después del ranking
    repuestos_seleccionados: bool  # True cuando el usuario ha seleccionado productos válidos
    
    # Control de stock
    tiene_stock_disponible: Optional[bool]  # True si hay stock en alguna opción
    reiniciar_busqueda: Optional[bool]  # True si el usuario quiere hacer una nueva búsqueda