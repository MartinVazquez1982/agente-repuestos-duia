from schemas.structure_outputs import ProductList
from langchain_core.prompts import ChatPromptTemplate

def generate_identify_product_chain(llm):
    """
    Crea chain para extraer productos del mensaje del usuario con salida estructurada (ProductList).
    """
    with open('system_prompts/identify_products.txt', 'r', encoding='utf-8') as f:
        IDENTIFY_PRODUCTS_PROMPT = f.read()

    prompt = ChatPromptTemplate.from_messages([
        ("system", IDENTIFY_PRODUCTS_PROMPT),
        ("placeholder", "{messages}")
    ])

    return prompt | llm.with_structured_output(ProductList)