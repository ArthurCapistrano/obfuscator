from sqlalchemy.sql import text
from .connection import DatabaseConnection


def setup_database(db_conn: DatabaseConnection) -> None:
    """Garante que o banco de dados especificado exista.

    Args:
        db_conn (DatabaseConnection): Conexão com o banco de dados.

    Returns:
        None

    Raises:
        Exception: Se ocorrer um erro ao criar/verificar o banco.
    """
    print(f"Verificando/Criando banco de dados: '{db_conn.db}'...")

    try:
        with db_conn.connect(engine=db_conn.get_server_engine()) as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_conn.db};"))
        print(f"Banco de dados '{db_conn.db}' verificado/criado com sucesso.")
    except Exception as e:
        print(f"Erro ao configurar banco de dados '{db_conn.db}': {e}")
        raise
