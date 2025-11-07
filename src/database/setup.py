import pandas as pd
from database.connection import DatabaseConnection
from database.utils import setup_database

def load_origin_data(db_conn: DatabaseConnection) -> None:
    """Carrega os dados de origem no banco de dados.
    Args:
        db_conn (DatabaseConnection): Conexão com o banco de dados.
    
    Returns:
        None

    Raises:
        Exception: Se ocorrer um erro durante o carregamento dos dados.
    """

    csv_path = "/opt/airflow/data/raw/recruitment_data.csv" 
    
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