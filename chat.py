import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

# --- Función de Lógica de Conversación ---

def get_llm_response(chat_history):
    # Aquí iría la lógica para obtener la respuesta del LLM/Grafo.
    # Si estuvieras usando LangGraph:
    # 1. Recuperarías el 'graph' y la 'config' de st.session_state.
    # 2. Invocarías el grafo: result = graph.invoke(..., config)
    # 3. Extraerías el último mensaje: result.get("messages")[-1].content
    
    # Por simplicidad, vamos a simular una respuesta
    if chat_history and chat_history[-1].content:
         return f"Respuesta simulada a: {chat_history[-1].content}"
    return "Respuesta simulada."

# --- Función para Resetear el Estado ---

def reset_conversation():
    """Reinicia la historia del chat y cualquier otro estado relevante."""
    # 1. Resetea la historia de la conversación
    st.session_state.chat_history = [
        AIMessage(content="¡Hola! Soy un asistente. ¿En qué puedo ayudarte hoy? (Conversación Reiniciada)")
    ]
    
    # 2. Si tuvieras un LangGraph real, aquí también deberías:
    #    a) Llamar a la función para generar un nuevo grafo si es necesario.
    #    b) Borrar el thread_id o cualquier estado específico del grafo de session_state.
    #    Ejemplo: del st.session_state["graph_state"] 
    
    # Nota: st.rerun() es necesario para recargar la página y reflejar el cambio.
    st.rerun()

# --- Interfaz de Streamlit ---

st.set_page_config(page_title="🤖 Chatbot Simple", layout="centered")
st.title("🤖 Chatbot Simple con Streamlit y LangChain")

# =========================================================
# 1. Botón de Reinicio en la Barra Lateral
# =========================================================

# Creamos una sección de herramientas en la barra lateral
st.sidebar.header("Opciones de Chat")

# Agregamos el botón, llamando a la función `reset_conversation` cuando se presiona.
if st.sidebar.button("🔄 Nuevo Chat (Resetear Grafo)"):
    reset_conversation()

# =========================================================

# 2. Inicializar la historia de la conversación en st.session_state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="¡Hola! Soy un asistente. ¿En qué puedo ayudarte hoy?")
    ]
    
# 3. Mostrar la historia de la conversación
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)

# 4. Manejar la nueva entrada del usuario
user_query = st.chat_input("Escribe tu mensaje aquí...")

if user_query is not None and user_query != "":
    # Mostrar el mensaje del usuario inmediatamente
    with st.chat_message("user"):
        st.markdown(user_query)

    # Agregar el mensaje del usuario a la historia
    st.session_state.chat_history.append(HumanMessage(content=user_query))

    # Obtener la respuesta del LLM
    with st.chat_message("assistant"):
        with st.spinner("Pensando..."):
            ai_response = get_llm_response(st.session_state.chat_history)
            st.markdown(ai_response)

    # Agregar la respuesta del LLM a la historia
    st.session_state.chat_history.append(AIMessage(content=ai_response))