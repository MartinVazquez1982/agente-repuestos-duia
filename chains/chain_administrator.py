from typing import Dict, Any, Optional

from chains.chain_generator.identify_product_chain import generate_identify_product_chain
from chains.chain_generator.ranking_chain import generate_ranking_chain
from chains.chain_generator.validation_chain import generate_validation_chain
from chains.chain_generator.verify_product_chain import generate_verify_product_chain
from chains.chain_generator.selection_interpretation_chain import generate_selection_interpretation_chain
from chains.chain_generator.no_stock_chain import generate_no_stock_chain
from chains.chain_generator.interpret_no_stock_response_chain import generate_interpret_no_stock_response_chain


class ChainAdministrator:
    """
    Clase Singleton para generar y almacenar todas las cadenas (chains) de LangChain.
    Asegura que las cadenas se inicialicen una sola vez.
    """
    _instance = None
    _chains: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        """Asegura que solo se cree una instancia de la clase."""
        if cls._instance is None:
            cls._instance = super(ChainAdministrator, cls).__new__(cls)
        return cls._instance

    def generate(self, llm):
        """
        Genera todas las cadenas (chains) si aún no han sido generadas.
        Requiere el modelo LLM como argumento.
        (El contenido de este método permanece igual que en la respuesta anterior)
        """
        if self._chains:
            print("Las cadenas ya fueron generadas. Usando la instancia existente.")
            return

        print("Generando las cadenas...")

        self._chains['extraction_chain'] = generate_identify_product_chain(llm)
        self._chains['validation_chain'] = generate_validation_chain(llm)
        self._chains['ranking_chain'] = generate_ranking_chain(llm)
        self._chains['verify_product_chain'] = generate_verify_product_chain(llm)
        self._chains['selection_interpretation_chain'] = generate_selection_interpretation_chain(llm)
        self._chains['no_stock_chain'] = generate_no_stock_chain(llm)
        self._chains['interpret_no_stock_response_chain'] = generate_interpret_no_stock_response_chain(llm)
        
                        
        print("Generación de cadenas completada.")
        
    def get(self, key: Optional[str] = None) -> Any:
        """
        Retorna una cadena específica por su clave, o todas las cadenas si no se 
        proporciona una clave.

        :param key: Clave (nombre) de la cadena a obtener (ej: 'validation_chain').
        :return: La cadena de LangChain solicitada o el diccionario completo de cadenas.
        :raises KeyError: Si la clave solicitada no existe.
        :raises RuntimeError: Si las cadenas no han sido generadas.
        """
        if not self._chains:
            raise RuntimeError("Las cadenas no han sido generadas. Llama a .generate(llm) primero.")
        
        if key is None:
            # Si no se proporciona clave, retorna todo el diccionario
            return self._chains
        
        # Si se proporciona clave, retorna solo esa cadena o levanta un error
        if key not in self._chains:
            raise KeyError(f"La clave de cadena '{key}' no existe. Claves disponibles: {list(self._chains.keys())}")
            
        return self._chains[key]