from langchain_core.prompts import ChatPromptTemplate


def generate_interpret_no_stock_response_chain(llm):
    """
    Genera una cadena para interpretar la respuesta del usuario cuando no hay stock.
    
    Args:
        llm: El modelo de lenguaje a utilizar
        
    Returns:
        Una cadena de LangChain configurada para interpretar respuestas
    """
    # Leer el prompt desde el archivo
    with open('prompts/interpret_no_stock_response_prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Crear el prompt template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Crear y retornar la cadena
    chain = prompt | llm
    
    return chain

