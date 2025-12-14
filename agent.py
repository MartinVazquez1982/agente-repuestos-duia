from graph import generate_graph
from langchain_core.messages import AIMessage, HumanMessage


class RepuestosAgent:
    
    ESTADO_INICIAL =  {
        "messages": [],
        "validation_result": None,
        "conversation_result": None,
        "product_description": [],
        "product_requests": [],
        "codigos_repuestos": None,
        "repuestos_encontrados": None,
        "productos_sin_match_interno": None,
        "selecciones_usuario": None,
        "repuestos_seleccionados": False,
        "info_completa": False,
        "optimized_query": None,
        "semantic_results": None,
        "resultados_internos": {},
        "resultados_externos": {},
        "disponibilidad": None,
        "codigos_para_externos": None,
        "recomendaciones_llm": None
    }
    
    def __init__(self):
        self.graph = generate_graph()
        self.first_message = True
        self.state = self.ESTADO_INICIAL.copy()
        self.config = {"configurable": {"thread_id": "1"}}
        self.result = None

    def get_next_message(self, message):
        if self.first_message:
            self.first_message = False
            self.state["messages"].append(HumanMessage(message))
            self.result = self.graph.invoke(self.state, self.config)
        else:
            snapshot = self.graph.get_state(self.config)
            proximos_nodos = snapshot.next if hasattr(snapshot, 'next') else []
            if self.result.get("info_completa") == False:
                if message.lower() in ["salir", "exit", "quit"]:
                    self.reset_agent()
                    return "\n👋 Conversación terminada"
                
                self.result = self.graph.invoke({
                    "messages": [HumanMessage(content=message)]
                }, self.config)
            
            elif proximos_nodos and "process_selection" in proximos_nodos:
                if message.lower() in ["salir", "exit", "quit"]:
                    self.reset_agent()
                    return "\n👋 Conversación terminada"
                
                self.graph.update_state(self.config, {
                    "messages": [HumanMessage(content=message)]
                })
                
                self.result = self.graph.invoke(None, self.config)
            
            elif proximos_nodos and "handle_no_stock_response" in proximos_nodos and self.result.get("tiene_stock_disponible") == False:
                if message.lower() in ["salir", "exit", "quit"]:
                    self.reset_agent()
                    return "\n👋 Conversación terminada"
                
                self.graph.update_state(self.config, {
                    "messages": [HumanMessage(content=message)]
                })
                
                self.result = self.graph.invoke(None, self.config)
            
            elif self.result.get("reiniciar_busqueda", False) and 
        
        complete, completion_message = self.is_conversation_complete(self.result)
        if complete:
            self.reset_agent()
            return completion_message
        
    def is_conversation_complete(self, result):
        selecciones = result.get("selecciones_usuario")
        if selecciones is not None:
            if len(selecciones) > 0:
                message = f"\n{'='*60}"
                message += "✅ Pedido procesado exitosamente"
                message += f"   Productos seleccionados: {len(selecciones)}"
                
                # Mostrar resumen
                internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
                externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
                
                if internos:
                    message += f"   • Internos: {len(internos)}"
                if externos:
                    message += f"   • Externos: {len(externos)}"
                
                message += f"{'='*60}\n"
            else:
                message += "\n❌ Pedido cancelado por el usuario\n"
            return True, message
        return False, None
            
    
    def reset_agent(self):
        self.agent.reset_state()
        self.result = None
        self.first_message = True
        self.state = self.ESTADO_INICIAL.copy()