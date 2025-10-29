import pandas as pd
from dotenv import load_dotenv
from database.connection import DatabaseConnection
from sqlalchemy.sql import text 
import os

# Load environment variables 
load_dotenv(".env")

def setup_database(db_conn: DatabaseConnection) -> None:
    """Configura o banco de dados de origem.

    Args:
        db_conn (DatabaseConnection): Conexão com o banco de dados.

    Returns:
        None

    Raises:
        Exception: Se ocorrer um erro durante a configuração do banco de dados.
    """

    print(f"Verificando/Criando banco de dados: '{db_conn.db}'...")
    
    with db_conn.connect(engine= db_conn.get_server_engine()) as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_conn.db};"))
    
    print(f"Banco de dados '{db_conn.db}' verificado/criado com sucesso.")

def load_origin_data(db_conn: DatabaseConnection) -> None:
    """Carrega os dados de origem no banco de dados.
    Args:
        db_conn (DatabaseConnection): Conexão com o banco de dados.
    Returns:
        None
    Raises:
        Exception: Se ocorrer um erro durante o carregamento dos dados.
    """

    csv_path = "data/raw/recruitment_data.csv"
    
    try:
        df = pd.read_csv(csv_path)
        print("Dados de origem carregados com sucesso.")
    except Exception as e:
        print(f"Erro ao carregar dados de origem: {e}")
        return
    
    with db_conn.connect() as conn:
        try:
            df.to_sql('recruitment_data', 
                      con=conn, 
                      if_exists='replace', 
                      index=False)
            print("Dados de origem inseridos na tabela 'recruitment_data' com sucesso.")
        except Exception as e:
            print(f"Erro ao inserir dados na tabela 'recruitment_data': {e}")

def main():
    # Setup Origin Database 
    origin_db = DatabaseConnection(prefix="ORIGIN")
    setup_database(origin_db)
    
    # Load Origin Data
    load_origin_data(origin_db)


if __name__ == "__main__":
    main()
