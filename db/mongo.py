import os
from pymongo import MongoClient
from pymongo.collection import Collection
from typing import Optional

class MongoCollectionManager:
    """
    Singleton que gestiona conexión a MongoDB y retorna la collection 'repuestos' de forma única.
    """
    _instance = None
    _collection: Optional[Collection] = None

    def __new__(cls, *args, **kwargs):
        """Asegura que solo se cree una instancia de la clase."""
        if cls._instance is None:
            cls._instance = super(MongoCollectionManager, cls).__new__(cls)
        return cls._instance

    def initialize(self):
        """
        Establece conexión con MongoDB y asigna collection; solo se ejecuta en la primera llamada.
        """
        if self._collection is not None:
            print("Conexión a MongoDB ya inicializada. Usando la collection existente.")
            return

        print("Inicializando conexión a MongoDB...")
        
        # 1. Obtener URI
        MONGO_URI = os.getenv("MONGO_URI")

        if not MONGO_URI:
            raise ValueError("MONGO_URI no encontrada en las variables de entorno.")

        # 2. Conexión al Cliente
        # MongoClient maneja el pooling de conexiones por defecto.
        try:
            client = MongoClient(MONGO_URI)
            
            # 3. Acceder a DB y Collection
            db = client["repuestos_db"]
            self._collection = db.repuestos
            
            # Opcional: Probar la conexión (ping)
            client.admin.command('ping')
            print("Conexión exitosa a MongoDB y collection 'repuestos' establecida.")
            
        except Exception as e:
            print(f"Error al conectar con MongoDB: {e}")
            self._collection = None
            raise

    def get_collection(self) -> Collection:
        """
        Retorna instancia de collection 'repuestos'; inicializa conexión si aún no existe.
        """
        if self._collection is None:
            # Si no se ha inicializado, intenta hacerlo (puede levantar un ValueError)
            self.initialize()
        
        if self._collection is None:
             raise RuntimeError("La collection no pudo ser obtenida. Revisa la inicialización.")

        return self._collection