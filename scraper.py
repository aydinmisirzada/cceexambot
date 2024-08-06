from pprint import pprint
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

from utils import print_results

options = Options()
options.headless = True  # Enable headless mode for invisible operation
options.add_argument("--window-size=1920,1200")  # Define the window size of the browser

DRIVER_PATH = '/opt/homebrew/bin/chromedriver'

LANG_LEVELS_WHITELIST = ['A1', 'A2', 'B1', 'B2', 'C1']

def get_seats_by_language_level(levels: list[str]):
    result = {} # level -> str[][]
    driver = webdriver.Chrome(options=options)

    driver.get("https://ujop.cuni.cz/UJOP-371.html?ujopcmsid=4")
    time.sleep(1)

    levels = [l.upper() for l in levels]
    for l in levels:
        if l not in LANG_LEVELS_WHITELIST:
            continue

        result[l] = []
        level_element = Select(driver.find_element(By.ID, 'select_uroven'))
        level_element.select_by_value(l)

        termin_element = driver.find_element(By.ID, 'select_termin')
        is_termin_selectable = termin_element.is_displayed() and termin_element.is_enabled()

        termin_select = Select(termin_element)
        if is_termin_selectable:
            for index in range(1, len(termin_select.options)):
                termin_select.select_by_index(index)
                num_of_slots_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'qxid')))

                # wait for result to load
                time.sleep(1) 

                result[l].append([termin_select.options[index].text, num_of_slots_element.text])
        else:
            num_of_slots_element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.ID, 'qxid')))
            time.sleep(1)
            result[l].append([termin_select.first_selected_option.text, num_of_slots_element.text])


    driver.quit()

    return result

if __name__ == '__main__':
    levels = ['a1', 'a3', 'a2']
    result = get_seats_by_language_level(levels)
    print_results(result)
