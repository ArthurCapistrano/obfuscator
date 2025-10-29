import os

from sqlalchemy import create_engine, Connection


class DatabaseConnection:
    def __init__(self, prefix: str):
        self.host = os.getenv(f"{prefix}_DB_HOST")
        self.port = os.getenv(f"{prefix}_DB_PORT")
        self.user = os.getenv(f"{prefix}_DB_USER")
        self.password = os.getenv(f"{prefix}_DB_PASSWORD")
        self.db = os.getenv(f"{prefix}_DB_NAME")

    def get_server_engine(self):
        return create_engine(
            f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}"
        )
    def get_db_engine(self):
        return create_engine(
            f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"
        )

    def connect(self, engine= None) -> Connection:
        """Estabelece uma conexão com o banco de dados.

        Args:
            engine (Engine, optional): O mecanismo de banco de dados a ser usado. Padrão é None.

        Returns:
            Connection: A conexão com o banco de dados.
        """   
        
        if engine is None:
            engine = self.get_db_engine()
        return engine.connect()
