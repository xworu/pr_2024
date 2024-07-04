import psycopg2
from psycopg2 import Error


def connect():
    try:
        connection = psycopg2.connect(
            user="postgres",
            password="postgres",
            host="db",
            port="5432",
            database="postgres"
        )
        return connection
    except (Exception, Error) as error:
        print("Ошибка при подключении к базе данных:", error)
        return None


def create_table():
    connection = connect()
    if connection is not None:
        try:
            cursor = connection.cursor()
            cursor.execute("DROP TABLE IF EXISTS data;")
            create_table_query = ('CREATE TABLE IF NOT EXISTS data('
                                  'id serial PRIMARY KEY, '
                                  'name varchar(256) NOT NULL, '
                                  'salary varchar(256) NOT NULL, '
                                  'experience varchar(256) NOT NULL, '
                                  'sorc varchar(1024) NOT NULL, '
                                  'link varchar(256) NOT NULL);')
            cursor.execute(create_table_query)
            connection.commit()
            print("Таблица успешно создана")
        except (Exception, Error) as error:
            print("Ошибка при создании таблицы:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()


def insert_data(query, name, salary, experience, sorc, link):
    connection = connect()
    if connection is not None:
        try:
            cursor = connection.cursor()
            if query == 'resume':
                insert_query = "INSERT INTO data (name, salary, experience, sorc, link) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (name, salary, experience, sorc, link))
            else:
                insert_query = "INSERT INTO data (name, salary, experience, sorc, link) VALUES (%s, %s, %s, %s, %s);"
                cursor.execute(insert_query, (name, salary, experience, sorc, link))
            connection.commit()
            print("Данные успешно добавлены в таблицу")
        except (Exception, Error) as error:
            print("Ошибка при вставке данных:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()


def read_data():
    connection = connect()
    if connection is not None:
        try:
            cursor = connection.cursor()
            select_query = "SELECT * FROM data;"
            cursor.execute(select_query)
            records = cursor.fetchall()
            # print(records)
            # for row in records:
            #     print("ID =", row[0])
            #     print("Name =", row[1], "\n")
            #     print("Salary =", row[2], "\n")
            #     print("Experience =", row[3], "\n")
            #     print("Skills or Company=", row[4], "\n")
            #     print("Link =", row[5], "\n")
            return records
        except (Exception, Error) as error:
            print("Ошибка при чтении данных:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()


def count():
    connection = connect()
    if connection is not None:
        try:
            cursor = connection.cursor()
            select_query = "SELECT COUNT(*) FROM data;"
            cursor.execute(select_query)
            result = cursor.fetchone()
            return result[0]
        except (Exception, Error) as error:
            print("Ошибка при чтении данных:", error)
        finally:
            if connection:
                cursor.close()
                connection.close()
