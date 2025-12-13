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

class ProductItem(BaseModel):
    descripcion: str = Field(
        description="Descripción del producto sin incluir la cantidad"
    )
    cantidad: int = Field(
        default=1,
        ge=1,  # Greater than or equal to 1
        description="Cantidad solicitada del producto. SIEMPRE debe ser >= 1. Por defecto 1 si no se especifica."
    )

class ProductList(BaseModel):
    products: List[ProductItem] = Field(
        default=[],
        description="Lista de productos con sus descripciones y cantidades solicitadas"
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

class ProductSelection(BaseModel):
    """
    Representa un producto seleccionado con su cantidad.
    """
    codigo: str = Field(
        description="Código del producto (formato R-XXXX)"
    )
    cantidad: int = Field(
        default=1,
        ge=1,
        description="Cantidad solicitada. Por defecto 1 si no se especifica."
    )

class UserSelectionIntent(BaseModel):
    """
    Interpretación de la intención del usuario al seleccionar productos.
    """
    accion: str = Field(
        description="La acción que el usuario quiere realizar: 'confirmar_todo', 'seleccionar_codigos', 'cancelar', 'no_entendido'"
    )
    productos_seleccionados: List[ProductSelection] = Field(
        default=[],
        description="Lista de productos con sus cantidades. Formato: [{codigo: 'R-XXXX', cantidad: N}, ...]"
    )
    confianza: float = Field(
        description="Nivel de confianza en la interpretación (0.0 a 1.0)"
    )
    razon: str = Field(
        description="Breve explicación de por qué se interpretó así"
    )