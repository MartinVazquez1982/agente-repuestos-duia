from langchain_core.prompts import ChatPromptTemplate


def generate_no_stock_chain(llm):
    """
    Genera una cadena para crear mensajes cuando no hay stock disponible.
    
    Args:
        llm: El modelo de lenguaje a utilizar
        
    Returns:
        Una cadena de LangChain configurada para generar mensajes de sin stock
    """
    # Leer el prompt desde el archivo
    with open('prompts/no_stock_prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Crear el prompt template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Crear y retornar la cadena
    chain = prompt | llm
    
    return chain

