import os


def generate_db_conn_string():
    """

    :return:
    """
    if os.environ['ENV'] == 'development':
        db_name = os.environ['DB_NAME_DEV']
        db_user = os.environ['DB_USER_DEV']
        db_pass = os.environ['DB_PASS_DEV']
        db_host = os.environ['DB_HOST_DEV']
        db_port = os.environ['DB_PORT_DEV']
    # Do we want to parse a DB URL here instead?
    else:
        db_name = os.environ['DB_NAME_PROD']
        db_user = os.environ['DB_USER_PROD']
        db_pass = os.environ['DB_PASS_PROD']
        db_host = os.environ['DB_HOST_PROD']
        db_port = os.environ['DB_PORT_PROD']

    connection_string = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"

    return connection_string

