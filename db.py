import sqlite3

DB_NAME = 'wkn_ticker.db'

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wkn_mapping (
        wkn TEXT PRIMARY KEY,
        ticker TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        wkn TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        wkn TEXT,
        amount REAL NOT NULL,
        purchase_date TEXT NOT NULL
    )
    ''')

    conn.commit()
    conn.close()

def add_wkn_ticker(wkn, ticker):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if wkn == "":
            cursor.execute('INSERT INTO wkn_mapping (wkn, ticker) VALUES (NULL, ?)', (ticker,))
        else:
            cursor.execute('INSERT OR REPLACE INTO wkn_mapping (wkn, ticker) VALUES (?, ?)', (wkn, ticker))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_ticker_from_wkn(wkn):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ticker FROM wkn_mapping WHERE wkn = ?', (wkn,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_all_wkn_tickers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT wkn, ticker FROM wkn_mapping')
    results = cursor.fetchall()
    conn.close()
    return results

def add_portfolio_position(ticker, wkn, amount, purchase_date):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO portfolio_positions (ticker, wkn, amount, purchase_date)
    VALUES (?, ?, ?, ?)
    ''', (ticker, wkn, amount, purchase_date))
    conn.commit()
    conn.close()

def get_portfolio_positions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT ticker, wkn, amount, purchase_date FROM portfolio_positions ORDER BY purchase_date DESC')
    results = cursor.fetchall()
    conn.close()
    return results
