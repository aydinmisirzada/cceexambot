from typing import List

def print_results(data: dict[list[list[str]]]):
    for lang_level in data:
        print('Level', lang_level, end=':\n')
        for entry in data[lang_level]:
            date, capacity = entry
            print('Date:', date, 'Number of seats:', capacity)    

def print_for_telegram(data: dict[str, list[list[str]]]) -> str:
    result = ""
    for lang_level in data:
        result += f"*{lang_level} level:*\n\n"
        for entry in data[lang_level]:
            date, capacity = entry
            capacity_text = f"{int(capacity)} seats"
            date_text = "Date: " + date.replace('.','\.')

            result += "`{:<20}{:>10}`\n".format(date_text, capacity_text)
        result += "\n"

    return result

def get_help_messages():
    return "I can help you track and get the latest info about CCE Czech language exams.\n\nThe following commands are available:\n\n/checkstatus - Get current number of available seats\n\n/track - Subscribe to status updates. As soon as there's a free seat, we'll notify you. The data is updated every 1 hour.\n\n/track A1 A2 - Subscribe to status updates for select language levels\n\n/untrack - Unsubscribe from updates"