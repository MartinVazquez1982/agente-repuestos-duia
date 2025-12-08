from langchain_core.prompts import ChatPromptTemplate
from schemas.structure_outputs import ProductInfoVerification

def generate_verify_product_chain(llm):
    VERIFY_PRODUCT_INFO_PROMPT = """
    Eres un experto en repuestos industriales. Analiza si la siguiente descripción de producto tiene información SUFICIENTE para realizar una búsqueda precisa en un catálogo.

    Descripción del producto: "{product_name}"

    Información necesaria para búsqueda efectiva:
    - Tipo de repuesto (rodamiento, filtro, bomba, correa, etc.) - REQUERIDO
    - Marca (SKF, Bosch, FAG, Parker, etc.) - OPCIONAL pero recomendado
    - Modelo o número de parte (6204-2RS, HF35554, etc.) - OPCIONAL pero recomendado

    Si tiene al menos el TIPO DE REPUESTO claramente identificado, la información es suficiente para intentar una búsqueda por similitud semántica.

    Ejemplos:
    - "rodamiento" → info_completa: true (tipo claro)
    - "filtro Bosch" → info_completa: true (tipo + marca)
    - "repuesto" → info_completa: false (muy vago, no se identifica tipo)
    - "algo para motor" → info_completa: false (no hay tipo específico)
    - "rodamiento SKF 6204-2RS" → info_completa: true (tipo + marca + modelo, ideal)

    Responde en formato JSON estructurado.
    """

    verify_info_prompt = ChatPromptTemplate.from_messages([
        ("system", VERIFY_PRODUCT_INFO_PROMPT),
    ])

    return verify_info_prompt | llm.with_structured_output(ProductInfoVerification)