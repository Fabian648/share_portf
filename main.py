import tkinter as tk
from tkinter import ttk
import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Beispiel: kleine WKN -> Ticker Mapping-Tabelle
wkn_to_ticker = {
    '846900': 'BMW.DE',       # BMW WKN
    '865985': 'DAI.DE',       # Daimler WKN
    'A0B7FY': 'SAP.DE',       # SAP WKN
    '851399': 'VOW3.DE',      # Volkswagen WKN
    # Hier kannst du weitere WKNs ergänzen
}

def resolve_ticker(input_str):
    # Prüfen ob Eingabe WKN ist (nur Zahlen oder gemischt)
    # Wenn WKN in Tabelle, dann Ticker zurückgeben, sonst Eingabe als Ticker interpretieren
    input_clean = input_str.strip().upper()
    if input_clean in wkn_to_ticker:
        return wkn_to_ticker[input_clean]
    else:
        # Sonst Eingabe als Ticker annehmen
        return input_clean

def get_stock_info(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        current_price = info.get('regularMarketPrice', 'N/A')
        day_high = info.get('dayHigh', 'N/A')
        day_low = info.get('dayLow', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        return current_price, day_high, day_low, market_cap, stock
    except Exception as e:
        return None, None, None, None, None

def show_info():
    user_input = entry.get()
    ticker = resolve_ticker(user_input)
    current_price, day_high, day_low, market_cap, stock = get_stock_info(ticker)
    if stock is not None:
        result_label.config(text=f"Eingabe: {user_input} → Ticker: {ticker}\n"
                                 f"Aktueller Kurs: {current_price} USD\n"
                                 f"Tageshoch: {day_high} USD\n"
                                 f"Tiefstkurs: {day_low} USD\n"
                                 f"Marktkapitalisierung: {market_cap}")

        hist = stock.history(period="1mo")

        global canvas
        if canvas:
            canvas.get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(hist.index, hist['Close'], label='Schlusskurs')
        ax.set_title(f"{ticker} Schlusskurs - letzte 30 Tage")
        ax.set_xlabel("Datum")
        ax.set_ylabel("Preis in USD")
        ax.legend()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=window)
        canvas.draw()
        canvas.get_tk_widget().pack(padx=10, pady=10)
    else:
        result_label.config(text="Fehler bei der Abfrage. Bitte Ticker oder WKN prüfen.")

window = tk.Tk()
window.title("Aktienkurs und Kennzahlen (mit WKN-Unterstützung)")

ttk.Label(window, text="Ticker oder WKN eingeben (z.B. AAPL oder 846900):").pack(padx=10, pady=5)
entry = ttk.Entry(window)
entry.pack(padx=10, pady=5)

ttk.Button(window, text="Anzeigen", command=show_info).pack(padx=10, pady=10)

result_label = ttk.Label(window, text="")
result_label.pack(padx=10, pady=10)

canvas = None  # globale Variable für die Grafik

window.mainloop()
