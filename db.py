import sqlite3

# Verbindung zur DB (wird erstellt, wenn sie nicht existiert)
conn = sqlite3.connect('wkn_ticker.db')
cursor = conn.cursor()

# Tabelle erstellen (falls nicht existiert)
cursor.execute('''
CREATE TABLE IF NOT EXISTS wkn_mapping (
    wkn TEXT PRIMARY KEY,
    ticker TEXT NOT NULL
)
''')

# Beispiel-Daten einfügen
sample_data = [
    ('846900', 'BMW.DE'),
    ('865985', 'DAI.DE'),
    ('A0B7FY', 'SAP.DE'),
    ('851399', 'VOW3.DE')
]

cursor.executemany('INSERT OR IGNORE INTO wkn_mapping (wkn, ticker) VALUES (?, ?)', sample_data)
conn.commit()

# WKN suchen
def get_ticker_from_wkn(wkn):
    cursor.execute('SELECT ticker FROM wkn_mapping WHERE wkn = ?', (wkn,))
    result = cursor.fetchone()
    return result[0] if result else None

# Beispiel Nutzung
wkn_input = '846900'
ticker = get_ticker_from_wkn(wkn_input)
print(f"WKN {wkn_input} entspricht dem Ticker {ticker}")

conn.close()
