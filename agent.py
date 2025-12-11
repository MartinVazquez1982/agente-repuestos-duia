from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from nodes.extract_products_info import extract_products_info
from nodes.check_product_info_completeness import check_product_info_completeness
from nodes.semantic_search import semantic_search_internal, semantic_search_external
from nodes.generate_ranking import generate_ranking
from nodes.validation import classify_request, set_val_message
from nodes.human_in_the_loop_selection import human_in_the_loop_selection
from nodes.process_user_selection import process_user_selection
from nodes.process_order import process_order
from nodes.process_internal_order import process_internal_order
from nodes.generate_external_email import generate_external_email
from nodes.process_both_type import process_both_types
from nodes.schedule_delivery import schedule_delivery
from nodes.check_stock_availability import check_stock_availability
from nodes.handle_no_stock_response import handle_no_stock_response
from nodes.request_new_products import request_new_products
from routes.routes import (
    route_classification,
    route_after_extraction_check,
    need_external_search,
    route_after_selection,
    route_by_product_type,
    route_after_stock_check,
    route_after_no_stock_response
)
from schemas.state import AgentState


def generate_agent():
    memory = MemorySaver()

    # Definimos el grafo
    graph_builder = StateGraph(AgentState)

    # Agrego los nodos al grafo
    graph_builder.add_node("validation", classify_request)
    graph_builder.add_node("set_val_message", set_val_message)
    # Nodos para extracción y verificación
    graph_builder.add_node("extract_products_info", extract_products_info) 
    graph_builder.add_node("check_product_info_completeness", check_product_info_completeness) 
    # Nodos de búsqueda semántica
    graph_builder.add_node("semantic_search_internal", semantic_search_internal)
    graph_builder.add_node("semantic_search_external", semantic_search_external)
    # Nodo de ranking
    graph_builder.add_node("reranking", generate_ranking)

    # Conecto los nodos
    graph_builder.add_edge(START, "validation")

    # Desde validation: si es pedido de repuestos → extract_products_info
    graph_builder.add_conditional_edges(
        "validation",
        route_classification,
        {
            "continue": "extract_products_info",
            "end": "set_val_message"
        }
    )

    graph_builder.add_edge("set_val_message", END)

    # Desde extracción → verificar
    graph_builder.add_edge("extract_products_info", "check_product_info_completeness")

    # Desde verificación: si info completa → semantic_search_internal, si no → END
    graph_builder.add_conditional_edges(
        "check_product_info_completeness",
        route_after_extraction_check,
        {
            "semantic_search": "semantic_search_internal",  # Ir directo a búsqueda interna
            "request_more_info": END
        }
    )

    # Desde semantic_search_internal: decidir si buscar externamente o verificar stock
    graph_builder.add_conditional_edges(
        "semantic_search_internal",
        need_external_search,
        {
            "search_external": "semantic_search_external",
            "reranking": "check_stock_availability"  # Ambos caminos pasan por verificación de stock
        }
    )

    # Desde semantic_search_external → check_stock_availability
    graph_builder.add_edge("semantic_search_external", "check_stock_availability")
    
    # Desde check_stock_availability → decidir si continuar o informar sin stock
    graph_builder.add_conditional_edges(
        "check_stock_availability",
        route_after_stock_check,
        {
            "continue_ranking": "reranking",
            "no_stock": "handle_no_stock_response"
        }
    )
    
    # Desde handle_no_stock_response → decidir si pedir nuevos productos o terminar
    graph_builder.add_conditional_edges(
        "handle_no_stock_response",
        route_after_no_stock_response,
        {
            "restart": "request_new_products",  # Ir a pedir nuevos productos
            "end": END
        }
    )
    
    # Desde request_new_products → extract_products_info (con interrupt para esperar respuesta)
    graph_builder.add_edge("request_new_products", "extract_products_info")
    
    # Agregar interrupt ANTES de handle_no_stock_response para esperar respuesta del usuario

    # Nodo de Human in the Loop
    graph_builder.add_node("human_in_the_loop", human_in_the_loop_selection)
    graph_builder.add_node("process_selection", process_user_selection)
    graph_builder.add_node("process_order", process_order)
    graph_builder.add_node("process_internal_order", process_internal_order)
    graph_builder.add_node("generate_external_email", generate_external_email)
    graph_builder.add_node("process_both_types", process_both_types)
    graph_builder.add_node("schedule_delivery", schedule_delivery)
    graph_builder.add_node("check_stock_availability", check_stock_availability)
    graph_builder.add_node("handle_no_stock_response", handle_no_stock_response)
    graph_builder.add_node("request_new_products", request_new_products)

    # Conexiones actualizadas
    graph_builder.add_edge("reranking", "human_in_the_loop")

    # Aquí usamos interrupt_before para detener la ejecución y esperar input del usuario
    # El grafo se detendrá ANTES de process_selection para que el usuario responda
    graph_builder.add_edge("human_in_the_loop", "process_selection")

    graph_builder.add_conditional_edges(
        "process_selection",
        route_after_selection,
        {
            "process_order": "process_order",  # DEPRECATED: solo para mostrar resumen
            "end": END  # Usuario canceló
        }
    )

    # Routing condicional según tipo de productos
    graph_builder.add_conditional_edges(
        "process_order",
        route_by_product_type,
        {
            "internal_only": "process_internal_order",  # Solo productos internos
            "external_only": "generate_external_email",  # Solo productos externos
            "both": "process_both_types",  # Ambos tipos
            "end": END
        }
    )

    # Después de cada tipo de procesamiento, ir a schedule_delivery
    graph_builder.add_edge("process_internal_order", "schedule_delivery")
    graph_builder.add_edge("generate_external_email", "schedule_delivery")
    graph_builder.add_edge("process_both_types", "schedule_delivery")
    
    # Después de agendar, terminar
    graph_builder.add_edge("schedule_delivery", END)

    # Compilar el grafo
    graph = graph_builder.compile(
        checkpointer=memory,
        interrupt_before=["handle_no_stock_response"],  # Pausa ANTES de procesar respuesta sin stock
        interrupt_after=["human_in_the_loop", "request_new_products"]  # Pausa DESPUÉS de mostrar ranking y pedir nuevos productos
    )
    
    return graph
