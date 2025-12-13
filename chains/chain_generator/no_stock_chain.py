from langchain_core.prompts import ChatPromptTemplate


def generate_no_stock_chain(llm):
    """
    Crea chain para generar mensaje informativo cuando no hay stock disponible de productos solicitados.
    """
    # Leer el prompt desde el archivo
    with open('system_prompts/no_stock_prompt.txt', 'r', encoding='utf-8') as f:
        prompt_template = f.read()
    
    # Crear el prompt template
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # Crear y retornar la cadena
    chain = prompt | llm
    
    return chain

