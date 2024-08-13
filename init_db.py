import sqlite3
import time


def get_db_connection():
    return sqlite3.connect('bot_data.db')

# Function to add a new user if they don't already exist, and update last_usage if they do


def add_user_if_not_exists(subscriber_id, chat_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert the user if they don't exist, or update the last_usage if they do
    cursor.execute('''
        INSERT INTO bot_users (subscriber_id, chat_id, last_usage)
        VALUES (?, ?, ?)
        ON CONFLICT(subscriber_id) DO UPDATE SET last_usage = excluded.last_usage, chat_id = excluded.chat_id
    ''', (subscriber_id, chat_id, int(time.time())))

    conn.commit()
    conn.close()

# Function to add or update a subscription


def add_subscription(subscriber_id, levels: list[str]):
    conn = get_db_connection()
    cursor = conn.cursor()

    subscribed_levels = ','.join(levels)

    print('subscribed_levels', subscribed_levels)
    print('subscriber_id', subscriber_id)

    cursor.execute('''
        INSERT INTO subscriptions (subscriber_id, subscribed_levels)
        VALUES (?, ?)
        ON CONFLICT(subscriber_id) DO UPDATE SET subscribed_levels = excluded.subscribed_levels
    ''', (subscriber_id, subscribed_levels))

    print('executed')

    conn.commit()

    print('commited')

    conn.close()


def delete_subcription(subscriber_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete the subscription for the given subscriber_id
    cursor.execute('''
        DELETE FROM subscriptions WHERE subscriber_id = ?
    ''', (subscriber_id,))

    conn.commit()
    conn.close()

# Function to get users and their subscriptions


def get_user_subscriptions():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT bot_users.subscriber_id, bot_users.chat_id, subscriptions.subscribed_levels 
        FROM bot_users
        JOIN subscriptions ON bot_users.subscriber_id = subscriptions.subscriber_id
    ''')

    user_subscriptions = cursor.fetchall()
    conn.close()
    return user_subscriptions


def get_user_subscription(subscriber_id):
    subscriptions = get_user_subscriptions()

    s = [sub for sub in subscriptions if sub[0] == subscriber_id]

    return s[0]


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
