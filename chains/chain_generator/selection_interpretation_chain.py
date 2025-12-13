from langchain_core.prompts import ChatPromptTemplate
from schemas.structure_outputs import UserSelectionIntent


def generate_selection_interpretation_chain(llm):
    INTERPRET_SELECTION_PROMPT = """
    Eres un asistente experto en interpretar las respuestas de usuarios en un sistema de pedidos de repuestos.

    El usuario está viendo un ranking de productos y debe seleccionar cuál(es) desea ordenar.

    OPCIONES DISPONIBLES EN EL RANKING:
    {codigos_disponibles}

    RESPUESTA DEL USUARIO:
    "{user_message}"

    Tu tarea es interpretar qué quiere hacer el usuario:

    1. **confirmar_todo**: Si dice que quiere todos los productos, confirma, acepta, procede con todo, etc.
    Ejemplos: "sí", "confirmar", "ok", "todos", "adelante", "proceder"

    2. **seleccionar_codigos**: Si menciona códigos específicos (formato R-XXXX) con o sin cantidades.
    Ejemplos: 
    - "R-0001" → [{{codigo: "R-0001", cantidad: 1}}]
    - "3 unidades del R-0001" → [{{codigo: "R-0001", cantidad: 3}}]
    - "R-0001 x5 y R-0002" → [{{codigo: "R-0001", cantidad: 5}}, {{codigo: "R-0002", cantidad: 1}}]
    - "10 del R-0001 y 2 del R-0002" → [{{codigo: "R-0001", cantidad: 10}}, {{codigo: "R-0002", cantidad: 2}}]
    - "R-0001 (5)" → [{{codigo: "R-0001", cantidad: 5}}]
    
    IMPORTANTE para extracción de cantidades:
    - Busca números ANTES o DESPUÉS del código
    - Formatos comunes: "5 R-0001", "R-0001 x5", "R-0001 (3)", "3 unidades de R-0001", "R-0001 por 10"
    - Si NO hay cantidad especificada, usa cantidad = 1
    - SIEMPRE incluye el campo cantidad (mínimo 1)

    3. **cancelar**: Si rechaza, cancela, no quiere nada.
    Ejemplos: "no", "cancelar", "no gracias", "rechazar"

    4. **no_entendido**: Si la respuesta es ambigua o no se puede interpretar claramente.

    REGLAS IMPORTANTES:
    - Sé PERMISIVO: si el usuario menciona un código (R-XXXX), interpreta como selección
    - Extrae TODOS los códigos con sus cantidades
    - Si hay códigos, la acción es 'seleccionar_codigos' (no 'confirmar_todo')
    - Usa alta confianza (>0.8) si la intención es clara
    - SIEMPRE retorna productos_seleccionados con estructura: [{{codigo: str, cantidad: int}}, ...]

    Responde en formato JSON estructurado con productos_seleccionados.
    """

    selection_prompt = ChatPromptTemplate.from_messages([
        ("system", INTERPRET_SELECTION_PROMPT),
    ])

    return selection_prompt | llm.with_structured_output(UserSelectionIntent)