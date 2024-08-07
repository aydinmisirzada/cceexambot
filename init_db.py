import sqlite3


def create_tables_from_file(sql_file):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    with open(sql_file, 'r', encoding='utf-8') as file:
        sql_script = file.read()

    cursor.executescript(sql_script)

    conn.commit()
    conn.close()


if __name__ == '__main__':
    create_tables_from_file('create_tables.sql')
