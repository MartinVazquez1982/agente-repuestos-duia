from pydantic import BaseModel, Field

class Repuesto(BaseModel):
    """
    Representa un repuesto identificado en la búsqueda semántica.
    Incluye código, descripción, marca, modelo y score de similitud.
    """
    id_repuesto: str = Field(
        description="Código único del repuesto (ej: R-0001)"
    )
    repuesto_descripcion: str = Field(
        description="Descripción del repuesto"
    )
    marca: str = Field(
        default="N/A",
        description="Marca del repuesto (SKF, FAG, Bosch, etc.)"
    )
    modelo: str = Field(
        default="N/A",
        description="Modelo o número de parte del repuesto"
    )
    categoria: str = Field(
        default="N/A",
        description="Categoría del repuesto (RODAMIENTO, FILTRO, etc.)"
    )
    score: float = Field(
        default=0.0,
        description="Score de similitud de la búsqueda semántica (0.0 a 1.0)"
    )
    
    def __str__(self) -> str:
        """Representación legible del repuesto"""
        return f"{self.id_repuesto} ({self.marca}): {self.repuesto_descripcion}"
    
    def get_unique_key(self) -> str:
        """Genera una clave única para identificar esta variante específica"""
        return f"{self.id_repuesto}_{self.marca}_{self.modelo}"
