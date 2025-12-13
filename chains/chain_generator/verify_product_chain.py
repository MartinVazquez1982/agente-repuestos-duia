from langchain_core.prompts import ChatPromptTemplate
from schemas.structure_outputs import ProductInfoVerification

def generate_verify_product_chain(llm):
    """
    Crea chain para verificar si descripción de producto tiene info suficiente para búsqueda efectiva.
    """
    VERIFY_PRODUCT_INFO_PROMPT = """
    Eres un experto en repuestos industriales e instrumentación. Analiza si la siguiente descripción de producto tiene información SUFICIENTE para realizar una búsqueda precisa en un catálogo.

    Descripción del producto: "{product_name}"

    Información necesaria para búsqueda efectiva:
    - Tipo de producto (repuesto, instrumento, equipo, herramienta) - REQUERIDO
    - Ejemplos válidos: rodamiento, filtro, bomba, correa, sensor, cámara termográfica, tacómetro, analizador, medidor, calibrador, endoscopio
    - Marca (SKF, Bosch, FLIR, Testo, Mitutoyo, etc.) - OPCIONAL pero recomendado
    - Modelo o número de parte (6204-2RS, E8-XT, TESTO-470, etc.) - OPCIONAL pero recomendado

    Si tiene al menos el TIPO DE PRODUCTO claramente identificado, la información es suficiente para intentar una búsqueda por similitud semántica.

    Ejemplos:
    - "rodamiento" → info_completa: true (tipo claro)
    - "filtro Bosch" → info_completa: true (tipo + marca)
    - "cámara termográfica FLIR" → info_completa: true (tipo + marca)
    - "tacómetro láser Testo" → info_completa: true (tipo + marca)
    - "analizador de vibraciones SKF" → info_completa: true (tipo + marca)
    - "repuesto" → info_completa: false (muy vago, no se identifica tipo)
    - "algo para motor" → info_completa: false (no hay tipo específico)
    - "rodamiento SKF 6204-2RS" → info_completa: true (tipo + marca + modelo, ideal)

    Responde en formato JSON estructurado.
    """

    verify_info_prompt = ChatPromptTemplate.from_messages([
        ("system", VERIFY_PRODUCT_INFO_PROMPT),
    ])

    return verify_info_prompt | llm.with_structured_output(ProductInfoVerification)