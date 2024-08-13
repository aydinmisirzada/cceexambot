-- Create the exam data table
CREATE TABLE IF NOT EXISTS exam_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exam_date TEXT NOT NULL, -- Date string in "MM:DD:YYYY" format
    language_level TEXT NOT NULL CHECK (language_level IN ('A1', 'A2', 'B1', 'B2', 'C1')), -- Language level
    number_of_seats INTEGER NOT NULL, -- Number of free seats for the given exam date
    last_fetch_time INTEGER NOT NULL -- Unix timestamp indicating the last fetch time
);

-- Create the bot users table
CREATE TABLE IF NOT EXISTS bot_users (
    subscriber_id INTEGER PRIMARY KEY, -- Telegram ID of the user
    chat_id INTEGER NOT NULL, -- ID of the chat with the user
    last_usage INTEGER NOT NULL -- Unix timestamp of when the user last interacted with the telegram bot
);

-- Create the subscriptions table
CREATE TABLE IF NOT EXISTS subscriptions (
    subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
    subscriber_id INTEGER NOT NULL UNIQUE,
    subscribed_levels TEXT NOT NULL,
    FOREIGN KEY (subscriber_id) REFERENCES bot_users(subscriber_id)
);