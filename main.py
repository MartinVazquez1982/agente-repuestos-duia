import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from chains.chain_administrator import ChainAdministrator
from db.mongo import MongoCollectionManager
from agent import generate_agent
from langchain_core.messages import AIMessage, HumanMessage

if __name__ == "__main__":
    load_dotenv()

    # Verificar que la API key está configurada
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY no encontrada en .env")

    # Inicializar el LLM de Groq
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0.1,
        api_key=api_key
    )
    
    chain_administrator = ChainAdministrator()
    chain_administrator.generate(llm)
    
    mongo_db = MongoCollectionManager()
    mongo_db.initialize()
    
    graph = generate_agent()
    
    print("="*60)
    print("🔧 SISTEMA DE BÚSQUEDA DE REPUESTOS")
    print("="*60)
    print("\nBienvenido al sistema de búsqueda de repuestos.")
    print("El agente te ayudará a encontrar el repuesto que necesitas.")
    print("\nPuedes escribir 'salir' en cualquier momento para terminar.\n")
    print("-"*60)
    
    config = {"configurable": {"thread_id": "1"}}
    
    #mensaje_usuario = input("\n👤 Tú: ")
    mensaje_usuario = "Necesito un Rodamiento rígido de bolas modelo 6204 2RS y dos Kits reparación válvula"
    
    # Estado inicial con todos los campos
    estado_inicial = {
        "messages": [HumanMessage(mensaje_usuario)],
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
    
    result = graph.invoke(estado_inicial, config)
    
    # Loop de conversación
    while True:
        # Mostrar solo NUEVOS mensajes del agente (AIMessage)
        mensajes_actuales = result.get("messages", [])
        
        # Buscar el último AIMessage (mensaje del agente)
        ultimo_mensaje_agente = None
        for msg in reversed(mensajes_actuales):
            if isinstance(msg, AIMessage):
                ultimo_mensaje_agente = msg.content
                break
        
        if ultimo_mensaje_agente:
            print(f"\n🤖 Agente: {ultimo_mensaje_agente}")
        
        # Verificar si hay un interrupt (Human in the Loop)
        snapshot = graph.get_state(config)
        proximos_nodos = snapshot.next if hasattr(snapshot, 'next') else []
        
        # Si el grafo está pausado después de human_in_the_loop
        if proximos_nodos and "process_selection" in proximos_nodos:
            # Loop hasta obtener una selección válida
            while True:
                print(f"\n{'─'*60}")
                nuevo_mensaje = input("\n👤 Tu selección: ").strip()
                
                if nuevo_mensaje.lower() in ["salir", "exit", "quit"]:
                    print("\n👋 Conversación terminada")
                    break
                
                # Actualizar el estado sin reiniciar
                graph.update_state(config, {
                    "messages": [HumanMessage(content=nuevo_mensaje)]
                })
                
                # Continuar desde donde se pausó (None = continuar, no reiniciar)
                result = graph.invoke(None, config)
                
                # Verificar si el usuario seleccionó productos válidos
                repuestos_seleccionados = result.get("repuestos_seleccionados", False)
                
                if repuestos_seleccionados:
                    # Selección exitosa o cancelación, salir del loop
                    break
                else:
                    # Respuesta inválida, mostrar el mensaje del AGENTE y re-preguntar
                    mensajes_actuales = result.get("messages", [])
                    # Filtrar solo AIMessages (mensajes del agente)
                    for msg in reversed(mensajes_actuales):
                        if isinstance(msg, AIMessage):
                            print(f"\n🤖 Agente: {msg.content}")
                            break
                    # Continuar el loop para pedir nueva entrada
            
            # Después de selección válida, continuar con el flujo
            continue
        
        # Verificar si se completó el pedido (hay selecciones)
        selecciones = result.get("selecciones_usuario")
        if selecciones is not None:
            if len(selecciones) > 0:
                print(f"\n{'='*60}")
                print("✅ Pedido procesado exitosamente")
                print(f"   Productos seleccionados: {len(selecciones)}")
                
                # Mostrar resumen
                internos = [s for s in selecciones if s['tipo'] == 'INTERNO']
                externos = [s for s in selecciones if s['tipo'] == 'EXTERNO']
                
                if internos:
                    print(f"   • Internos: {len(internos)}")
                if externos:
                    print(f"   • Externos: {len(externos)}")
                
                print(f"{'='*60}\n")
            else:
                print("\n❌ Pedido cancelado por el usuario\n")
            break
        
        # Si no hay información completa, pedir más detalles
        if result.get("info_completa") == False:
            print(f"\n{'─'*60}")
            nuevo_mensaje = input("\n👤 Tú: ").strip()
            
            if nuevo_mensaje.lower() in ["salir", "exit", "quit"]:
                print("\n👋 Conversación terminada")
                break
            
            # Para el caso de pedir más info, sí necesitamos pasar el mensaje
            result = graph.invoke({
                "messages": [HumanMessage(content=nuevo_mensaje)]
            }, config)
            continue
        
        # Si llegamos aquí sin break, algo salió mal o terminó el flujo
        break
    
    