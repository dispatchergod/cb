import psycopg2
from config import host, user, password, db_name


def db_query(func, **kwargs):
    result = None
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        connection.autocommit = True

        with connection.cursor() as cursor:
            result = func(cursor, **kwargs)

    except Exception as ex:
        print(f"[ERROR] {ex}")
    finally:
        if connection:
            connection.close()
            print(f"[INFO] Connection closed")
    return result


# args = table, fields, values
def add_data(cursor, **kwargs):
    # format for fields: [field1, field2, ...]
    query_fields = ", ".join([field for field in kwargs['fields']])
    # format for values: [value1, value2, ...]
    query_values = ", ".join([f"'{value}'" for value in kwargs['values']])

    cursor.execute(
        f"INSERT INTO {kwargs['table']} ({query_fields})"
        f" VALUES ({query_values})"
    )

    print(f"[INFO] Data added successfully")


def get_all_data(cursor, **kwargs):
    cursor.execute(
        f"SELECT * FROM {kwargs['table']} "
    )
    fetched_data = cursor.fetchall()
    print(f"[INFO] User data: {fetched_data}")
    return fetched_data


def search_data(cursor, **kwargs):
    # kwargs = table, fields, condition
    query_fields = ", ".join([field for field in kwargs['fields']])
    cursor.execute(
        f"SELECT {query_fields} FROM {kwargs['table']}"
        f" WHERE {kwargs['condition']}"
    )
    fetched_data = cursor.fetchall()
    print(f"[INFO] Data: {fetched_data}")
    return fetched_data


def get_data(cursor, **kwargs):
    query = kwargs["query"]
    cursor.execute(query)
    # print(f"[INFO] User data: {cursor.fetchall()}")
    return cursor.fetchall()
