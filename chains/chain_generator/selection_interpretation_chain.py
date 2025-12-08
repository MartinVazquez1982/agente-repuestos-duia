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

    2. **seleccionar_codigos**: Si menciona códigos específicos (formato R-XXXX).
    Ejemplos: "R-0001", "quiero el R-0007", "dame R-0002 y R-0005"
    IMPORTANTE: Extrae SOLO los códigos que están en el formato R-XXXX

    3. **cancelar**: Si rechaza, cancela, no quiere nada.
    Ejemplos: "no", "cancelar", "no gracias", "rechazar"

    4. **no_entendido**: Si la respuesta es ambigua o no se puede interpretar claramente.

    IMPORTANTE:
    - Sé PERMISIVO: si el usuario menciona un código (R-XXXX), interpreta como selección aunque la frase no sea perfecta
    - Extrae TODOS los códigos en formato R-XXXX que encuentres en el mensaje
    - Si hay códigos, la acción es 'seleccionar_codigos' (no 'confirmar_todo')
    - Usa alta confianza (>0.8) si la intención es clara

    Responde en formato JSON estructurado.
    """

    selection_prompt = ChatPromptTemplate.from_messages([
        ("system", INTERPRET_SELECTION_PROMPT),
    ])

    return selection_prompt | llm.with_structured_output(UserSelectionIntent)