from pydantic import BaseModel, Field
from typing import List

class ValidationRequest(BaseModel):
    is_parts_request: bool = Field(
        default=False,
        description="True si la consulta es una solicitud de repuestos o piezas. False si es una pregunta general o spam."
    )
    message: str = Field(
        default="",
        description="Mensaje del agente. Si es un pedido de repuestos, debe incluir los pasos siguientes. Indicar al cliente que debe se deben realizar consultas sobre repuestos."
    )

class ConversationResult(BaseModel):
    """
    Resultado del análisis conversacional.
    """
    enough_info: bool = Field(
        description="True si hay suficiente información para proceder con la búsqueda, False si se necesita más información"
    )
    message: str = Field(
        description="Mensaje para el usuario (pregunta si enough_info=False, confirmación si enough_info=True)"
    )

class ProductList(BaseModel):
    products: list[str] = Field(
        default=[],
        description="Es una lista con las descripciones que realizo el cliente de los productos que solicita"
    )


class ProductInfoVerification(BaseModel):
    """
    Resultado de la verificación de información de un producto.
    """
    info_completa: bool = Field(
        description="True si hay suficiente información para buscar (al menos tipo de repuesto identificado)"
    )
    razon: str = Field(
        description="Explicación breve de por qué sí o no tiene información suficiente"
    )
    info_faltante: List[str] = Field(
        default=[],
        description="Lista de campos que faltan o necesitan más detalle"
    )

class UserSelectionIntent(BaseModel):
    """
    Interpretación de la intención del usuario al seleccionar productos.
    """
    accion: str = Field(
        description="La acción que el usuario quiere realizar: 'confirmar_todo', 'seleccionar_codigos', 'cancelar', 'no_entendido'"
    )
    codigos_seleccionados: List[str] = Field(
        default=[],
        description="Lista de códigos de productos mencionados (formato R-XXXX). Vacío si confirmó todo o canceló."
    )
    confianza: float = Field(
        description="Nivel de confianza en la interpretación (0.0 a 1.0)"
    )
    razon: str = Field(
        description="Breve explicación de por qué se interpretó así"
    )