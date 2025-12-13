from langchain_core.prompts import ChatPromptTemplate


def generate_interpret_no_stock_response_chain(llm):
    """
    Crea chain para interpretar respuesta del usuario ante falta de stock (nueva búsqueda o cancelar).
    """
    # Leer el prompt desde el archivo
    with open('system_prompts/interpret_no_stock_response_prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Crear el prompt template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Crear y retornar la cadena
    chain = prompt | llm
    
    return chain

