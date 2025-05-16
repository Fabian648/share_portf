import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from db import *
from stock_api import *

# Globale Variable für Chart Canvas
canvas = None

def create_tab1(parent):
    global canvas
    frame = ttk.Frame(parent)

    ttk.Label(frame, text="Ticker oder WKN eingeben (z.B. AAPL oder 846900):").pack(padx=10, pady=5)
    entry = ttk.Entry(frame)
    entry.pack(padx=10, pady=5)

    result_label = ttk.Label(frame, text="")
    result_label.pack(padx=10, pady=10)

    def resolve_ticker(input_str):
        input_clean = input_str.strip().upper()
        ticker = get_ticker_from_wkn(input_clean)
        return ticker if ticker else input_clean

    def show_info():
        global canvas
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

            if canvas:
                canvas.get_tk_widget().destroy()

            fig, ax = plt.subplots(figsize=(6, 4))
            ax.plot(hist.index, hist['Close'], label='Schlusskurs')
            ax.set_title(f"{ticker} Schlusskurs - letzte 30 Tage")
            ax.set_xlabel("Datum")
            ax.set_ylabel("Preis in USD")
            ax.legend()
            fig.tight_layout()

            canvas = FigureCanvasTkAgg(fig, master=frame)
            canvas.draw()
            canvas.get_tk_widget().pack(padx=10, pady=10)
        else:
            result_label.config(text="Fehler bei der Abfrage. Bitte Ticker oder WKN prüfen.")

    ttk.Button(frame, text="Anzeigen", command=show_info).pack(padx=10, pady=10)

    return frame

def create_tab2(parent, refresh_portfolio_tab_callback):
    frame = ttk.Frame(parent)

    ttk.Label(frame, text="WKN (optional):").pack(padx=10, pady=5)
    wkn_entry = ttk.Entry(frame)
    wkn_entry.pack(padx=10, pady=5)

    ttk.Label(frame, text="Ticker (Pflichtfeld):").pack(padx=10, pady=5)
    ticker_entry = ttk.Entry(frame)
    ticker_entry.pack(padx=10, pady=5)

    def save_entry():
        wkn = wkn_entry.get().strip().upper()
        ticker = ticker_entry.get().strip().upper()

        if ticker == "":
            messagebox.showerror("Fehler", "Ticker darf nicht leer sein!")
            return

        if not ticker_exists(ticker):
            messagebox.showerror("Fehler", f"Ticker '{ticker}' scheint nicht gültig oder verfügbar zu sein.")
            return

        success = add_wkn_ticker(wkn, ticker)
        if success:
            messagebox.showinfo("Erfolg", f"Eintrag gespeichert:\nTicker: {ticker}\nWKN: {wkn if wkn else '(keine)'}")
            wkn_entry.delete(0, tk.END)
            ticker_entry.delete(0, tk.END)
            refresh_portfolio_tab_callback()
        else:
            messagebox.showerror("Fehler", "Eintrag konnte nicht gespeichert werden (möglicherweise doppelter WKN)")

    ttk.Button(frame, text="Speichern", command=save_entry).pack(padx=10, pady=15)

    return frame

def create_tab3(parent):
    frame = ttk.Frame(parent)

    ttk.Label(frame, text="Auswahl aus vorhandenen Aktien/ETFs:").pack(padx=10, pady=5)

    combo_values = []
    combo_var = tk.StringVar()
    combobox = ttk.Combobox(frame, textvariable=combo_var, state="readonly", width=40)
    combobox.pack(padx=10, pady=5)

    def refresh_combo_values():
        nonlocal combo_values
        entries = get_all_wkn_tickers()
        combo_values = []
        for wkn, ticker in entries:
            if wkn:
                combo_values.append(f"{ticker} ({wkn})")
            else:
                combo_values.append(f"{ticker} (kein WKN)")
        combobox['values'] = combo_values
        if combo_values:
            combobox.current(0)
        else:
            combobox.set('')

    refresh_combo_values()

    # Eingabefelder für Menge und Kaufdatum
    frame_inputs = ttk.Frame(frame)
    frame_inputs.pack(padx=10, pady=10, fill='x')

    ttk.Label(frame_inputs, text="Anzahl Aktien (auch Bruchteile):").grid(row=0, column=0, sticky='w')
    amount_entry = ttk.Entry(frame_inputs)
    amount_entry.grid(row=0, column=1, sticky='w')

    ttk.Label(frame_inputs, text="Kaufdatum:").grid(row=1, column=0, sticky='w')
    purchase_date_entry = DateEntry(frame_inputs, date_pattern='yyyy-mm-dd')
    purchase_date_entry.grid(row=1, column=1, sticky='w')

    def refresh_portfolio_list():
        portfolio_listbox.delete(0, tk.END)
        for ticker, wkn, amount, purchase_date in get_portfolio_positions():
            display = f"{purchase_date}: {amount} Aktien von {ticker} ({wkn if wkn else 'kein WKN'})"
            portfolio_listbox.insert(tk.END, display)

    def add_selected_to_portfolio():
        selection = combo_var.get()
        if not selection:
            messagebox.showerror("Fehler", "Bitte eine Aktie/ETF auswählen!")
            return

        ticker = selection.split()[0]
        wkn_part = selection.split('(')[-1].strip(')')
        wkn = None if wkn_part == 'kein WKN' else wkn_part

        try:
            amount = float(amount_entry.get().replace(',', '.'))
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Fehler", "Bitte eine gültige positive Anzahl Aktien eingeben.")
            return

        purchase_date = purchase_date_entry.get_date().strftime('%Y-%m-%d')

        add_portfolio_position(ticker, wkn, amount, purchase_date)
        messagebox.showinfo("Erfolg", f"{amount} Aktien von {ticker} (WKN: {wkn if wkn else 'kein WKN'}) zum {purchase_date} hinzugefügt.")

        amount_entry.delete(0, tk.END)
        refresh_portfolio_list()

    ttk.Button(frame, text="Zum Portfolio hinzufügen", command=add_selected_to_portfolio).pack(padx=10, pady=10)

    ttk.Label(frame, text="Deine Portfolio-Positionen:").pack(padx=10, pady=10)
    portfolio_listbox = tk.Listbox(frame, width=70, height=15)
    portfolio_listbox.pack(padx=10, pady=5)

    refresh_portfolio_list()

    # Callback um Tab1/Tab2 zu refreshen, wenn nötig
    def refresh_all():
        refresh_combo_values()
        refresh_portfolio_list()

    frame.refresh_all = refresh_all  # falls von außen benötigt

    return frame
