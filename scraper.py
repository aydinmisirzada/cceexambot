from datetime import datetime
import sqlite3
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import transform_data_to_dict


options = Options()
options.headless = True  # Enable headless mode for invisible operation
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument('--disable-dev-shm-usage')

LANG_LEVELS_WHITELIST = ['A1', 'A2', 'B1', 'B2', 'C1']


async def fetch_seats_by_language_level(levels: list[str]):
    # Check if the provided language levels are valid
    valid_levels = {'A1', 'A2', 'B1', 'B2', 'C1'}
    if not all(level in valid_levels for level in levels):
        raise ValueError(
            "Invalid language level. Must be one of: 'A1', 'A2', 'B1', 'B2', 'C1'.")

    result = {}  # level -> str[][]
    driver = webdriver.Chrome(options=options)

    driver.get("https://ujop.cuni.cz/UJOP-371.html?ujopcmsid=4")
    time.sleep(1)

    for l in levels:
        result[l] = []
        level_element = Select(driver.find_element(By.ID, 'select_uroven'))
        level_element.select_by_value(l)

        termin_element = driver.find_element(By.ID, 'select_termin')
        is_termin_selectable = termin_element.is_displayed() and termin_element.is_enabled()

        termin_select = Select(termin_element)
        if is_termin_selectable:
            for index in range(1, len(termin_select.options)):
                termin_select.select_by_index(index)
                num_of_slots_element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located((By.ID, 'qxid')))

                # wait for result to load
                time.sleep(1)

                result[l].append(
                    [termin_select.options[index].text, num_of_slots_element.text])
        else:
            num_of_slots_element = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.ID, 'qxid')))
            time.sleep(1)
            result[l].append(
                [termin_select.first_selected_option.text, num_of_slots_element.text])

    driver.quit()

    return result


def get_seats_from_db(language_levels: list[str]):
    # Check if the provided language levels are valid
    valid_levels = {'A1', 'A2', 'B1', 'B2', 'C1'}
    if not all(level in valid_levels for level in language_levels):
        raise ValueError(
            "Invalid language level. Must be one of: 'A1', 'A2', 'B1', 'B2', 'C1'.")

    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Create a placeholder string for the SQL query
    placeholders = ', '.join('?' for _ in language_levels)

    # Execute the query with the provided language levels
    query = f'''
        SELECT id, exam_date, language_level, number_of_seats
        FROM exam_data
        WHERE language_level IN ({placeholders})
    '''
    cursor.execute(query, language_levels)

    results = cursor.fetchall()

    conn.close()

    return results


def write_data_to_db(data):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Get the current Unix timestamp
    current_timestamp = int(datetime.now().timestamp())

    for language_level, entries in data.items():
        for entry in entries:
            exam_date = entry[0]
            number_of_seats = int(entry[1])

            # Check if the record exists
            cursor.execute('''
                SELECT id FROM exam_data
                WHERE exam_date = ? AND language_level = ?
            ''', (exam_date, language_level))

            existing_record = cursor.fetchone()

            if existing_record:
                # Update the existing record
                cursor.execute('''
                    UPDATE exam_data
                    SET number_of_seats = ?, last_fetch_time = ?
                    WHERE id = ?
                ''', (number_of_seats, current_timestamp, existing_record[0]))
            else:
                # Insert a new record
                cursor.execute('''
                    INSERT INTO exam_data (exam_date, language_level, number_of_seats, last_fetch_time)
                    VALUES (?, ?, ?, ?)
                ''', (exam_date, language_level, number_of_seats, current_timestamp))

    conn.commit()
    conn.close()


async def get_or_fetch_seats(levels: list[str]):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()

    # Check if any record has last_fetch_time older than 30 minutes
    cursor.execute('''
        SELECT *
        FROM exam_data
    ''')

    is_db_empty = len(cursor.fetchall()) == 0

    # Get the current time and calculate the timestamp for 30 minutes ago
    current_timestamp = int(datetime.now().timestamp())
    thirty_minutes_ago = current_timestamp - 1800

    # Check if any record has last_fetch_time older than 30 minutes
    cursor.execute('''
        SELECT DISTINCT language_level
        FROM exam_data
        WHERE last_fetch_time < ?
    ''', (thirty_minutes_ago,))

    outdated_data = cursor.fetchall()
    outdated_levels = [row[0] for row in outdated_data]

    if set(levels).intersection(outdated_levels) or is_db_empty:
        # Fetch new data
        fetched_data = await fetch_seats_by_language_level(levels)

        # Write new data to the database
        write_data_to_db(fetched_data)

    # Correctly format the placeholders for the IN clause
    placeholders = ', '.join('?' for _ in levels)

    # Return data from the database
    cursor.execute(f'''
        SELECT exam_date, language_level, number_of_seats
        FROM exam_data
        WHERE language_level IN ({placeholders})
    ''', levels)

    results = cursor.fetchall()

    conn.close()

    return transform_data_to_dict(results)


if __name__ == '__main__':
    lvls = ['A1', 'A2']

    n = get_or_fetch_seats(lvls)
