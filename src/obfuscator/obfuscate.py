import pandas as pd
import json
import hashlib
from faker import Faker
from sqlalchemy.sql import text
from database.connection import DatabaseConnection
from database.utils import setup_database


fake = Faker()

def load_rules(rules_path: str) -> dict:
    """Carrega as regras de ofuscação a partir de um arquivo JSON.

    Args:
        rules_path (str): Caminho completo para o arquivo JSON com as regras.

    Returns:
        dict: Dicionário contendo as regras de ofuscação.
    """
    print(f"Carregando regras de ofuscação de '{rules_path}'...")
    try:
        with open(rules_path, "r") as f:
            rules = json.load(f)
        print("Regras de ofuscação carregadas com sucesso.")
        return rules
    except Exception as e:
        print(f"Erro ao carregar regras de ofuscação: {e}")
        raise


def obfuscate_value(value, method: str, first_name_cache: dict) -> str:
    """Aplica o método de ofuscação em um único valor.

    Args:
        value: Valor original a ser ofuscado.
        method (str): Tipo de ofuscação a ser aplicada.
        first_name_cache (dict): Cache para armazenar nomes gerados e reutilizados.

    Returns:
        str: Valor ofuscado.
    """
    if method == "preserve":
        return value
    if method == "sha256":
        return hashlib.sha256(str(value).encode()).hexdigest()
    if method == "first_name":
        first_name_cache["value"] = fake.first_name()
        return first_name_cache["value"]
    if method == "last_name":
        return fake.last_name()
    if method == "email_from_name":
        name = first_name_cache.get("value", fake.first_name())
        return f"{name.lower()}{fake.random_int(1, 99)}@{fake.free_email_domain()}"
    if method == "phone_number":
        return fake.phone_number()
    if method == "street_address":
        return fake.street_address()
    if method == "city":
        return fake.city()
    if method == "state_abbr":
        return fake.state_abbr()
    if method == "zipcode":
        return fake.zipcode()
    if method == "country":
        return fake.country()
    if method == "date_of_birth":
        return fake.date_of_birth(minimum_age=18, maximum_age=65)
    if method == "gender":
        return fake.random_element(elements=("Male", "Female", "Other"))
    if method == "job":
        return fake.job()
    return value


def obfuscate_row(row: pd.Series, rules: dict) -> pd.Series:
    """Aplica as regras de ofuscação em uma linha do DataFrame.

    Args:
        row (pd.Series): Linha do DataFrame original.
        rules (dict): Regras de ofuscação.

    Returns:
        pd.Series: Linha ofuscada.
    """
    try:
        seed = int(row.get("Applicant ID", 0))
    except ValueError:
        seed = hash(row.get("Applicant ID", 0))
    
    fake.seed_instance(seed)
    new_row = row.copy()
    first_name_cache = {}

    for col, method in rules.items():
        if col in new_row:
            new_row[col] = obfuscate_value(new_row[col], method, first_name_cache)

    return new_row


def read_source_table(db_conn: DatabaseConnection, table_name: str) -> pd.DataFrame:
    """Lê os dados de uma tabela no banco de origem.

    Args:
        db_conn (DatabaseConnection): Conexão com o banco de origem.
        table_name (str): Nome da tabela a ser lida.

    Returns:
        pd.DataFrame: DataFrame com os dados da tabela.
    """
    print(f"Lendo dados da tabela '{table_name}' do banco '{db_conn.db}'...")
    with db_conn.connect() as conn:
        df = pd.read_sql_table(table_name, con=conn)
    print(f"Leitura concluída: {len(df)} registros.")
    return df


def save_to_destination(db_conn: DatabaseConnection, df: pd.DataFrame, table_name: str) -> None:
    """Salva o DataFrame no banco de destino.

    Args:
        db_conn (DatabaseConnection): Conexão com o banco de destino.
        df (pd.DataFrame): Dados ofuscados.
        table_name (str): Nome da tabela de destino.

    Returns:
        None
    """
    print(f"Salvando dados ofuscados na tabela '{table_name}' do banco '{db_conn.db}'...")
    with db_conn.connect() as conn:
        df.to_sql(table_name, con=conn, if_exists="replace", index=False)
    print("Dados salvos com sucesso.")


def main() -> None:
    print("Iniciando processo de ofuscação...")

    origin_db = DatabaseConnection(prefix="ORIGIN")
    dest_db = DatabaseConnection(prefix="DESTINATION")

    setup_database(dest_db)

    rules_path = "/opt/airflow/src/obfuscator/rules.json"
    rules = load_rules(rules_path)

    df = read_source_table(origin_db, "recruitment_data")
    obfuscated_df = df.apply(lambda row: obfuscate_row(row, rules), axis=1)
    print("Ofuscação aplicada com sucesso.")

    save_to_destination(dest_db, obfuscated_df, "recruitment_data")
    print("Pipeline de ofuscação concluído com sucesso.")


if __name__ == "__main__":
    main()
