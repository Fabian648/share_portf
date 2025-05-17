import streamlit as st
import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="Aktienbewertung", layout="centered")
st.title("📈 Aktienbewertungstool")

# --- Datenbank Setup ---
conn = sqlite3.connect("aktien_bewertungen.db")
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS bewertungen (
        id INTEGER PRIMARY KEY,
        ticker TEXT,
        datum TEXT,
        score INTEGER,
        kgv REAL,
        kbv REAL,
        dividende REAL,
        gewinn REAL,
        verschuldung REAL
    )
''')
conn.commit()

def save_to_db(data):
    c.execute('''
        INSERT INTO bewertungen (ticker, datum, score, kgv, kbv, dividende, gewinn, verschuldung)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['ticker'],
        data['datum'],
        data['score'],
        data['kgv'],
        data['kbv'],
        data['dividende'],
        data['gewinn'],
        data['verschuldung']
    ))
    conn.commit()

def load_history(ticker):
    c.execute('SELECT datum, score, kgv, kbv, dividende, gewinn, verschuldung FROM bewertungen WHERE ticker = ? ORDER BY datum DESC', (ticker,))
    return c.fetchall()

# --- Eingabe ---
ticker_input = st.text_input("🔎 Gib den Ticker der Aktie ein (z. B. AAPL, MSFT, AMZN)")

if ticker_input:
    ticker = yf.Ticker(ticker_input.upper())
    data = ticker.info

    st.subheader(f"📊 {data.get('longName', ticker_input)} – Übersicht")

    # Dividendenrendite
    div_yield = data.get('dividendYield')
    if div_yield is not None and 0 < div_yield < 1:
        div_yield_percent = round(div_yield * 100, 2)
    else:
        div_yield_percent = 0.0

    # Verschuldung berechnen (totalDebt / totalAssets)
    total_debt = data.get('totalDebt')
    total_assets = data.get('totalAssets')
    if total_debt and total_assets and total_assets != 0:
        debt_ratio = round(total_debt / total_assets, 2)
    else:
        debt_ratio = None

    st.write(f"**Aktueller Kurs:** {data.get('currentPrice', 'N/A')} USD")
    st.write(f"**Marktkapitalisierung:** {data.get('marketCap', 'N/A'):,}")
    st.write(f"**KGV:** {data.get('trailingPE', 'N/A')}")
    st.write(f"**KBV:** {data.get('priceToBook', 'N/A')}")
    st.write(f"**Dividendenrendite:** {div_yield_percent}%")
    st.write(f"**Umsatz:** {data.get('totalRevenue', 'N/A'):,}")
    st.write(f"**Gewinn:** {data.get('netIncomeToCommon', 'N/A'):,}")
    st.write(f"**Verschuldungsgrad (Debt/Assets):** {debt_ratio if debt_ratio is not None else 'N/A'}")

    # Bewertungspunkte einzeln berechnen
    points = []

    kgv = data.get('trailingPE')
    if kgv and kgv < 15:
        points.append(("KGV < 15", 20))
    else:
        points.append(("KGV < 15", 0))

    kbv = data.get('priceToBook')
    if kbv and kbv < 2:
        points.append(("KBV < 2", 20))
    else:
        points.append(("KBV < 2", 0))

    if div_yield_percent > 2:
        points.append(("Dividendenrendite > 2%", 20))
    else:
        points.append(("Dividendenrendite > 2%", 0))

    gewinn = data.get('netIncomeToCommon')
    if gewinn and gewinn > 0:
        points.append(("Gewinn > 0", 20))
    else:
        points.append(("Gewinn > 0", 0))

    if debt_ratio is not None and debt_ratio < 0.5:
        points.append(("Verschuldung < 50%", 20))
    else:
        points.append(("Verschuldung < 50%", 0))

    score = sum(p[1] for p in points)

    st.subheader(f"📈 Bewertung: {score}/100 Punkte")

    # Punkte Tabelle anzeigen
    st.table(pd.DataFrame(points, columns=["Kriterium", "Punkte"]))

    if score >= 80:
        st.success("✅ Sehr attraktives Investment")
    elif score >= 60:
        st.warning("⚠️ Möglicherweise lohnenswert")
    else:
        st.error("❌ Eher kein gutes Investment")

    # Speichern Button
    if st.button("💾 Bewertung speichern"):
        to_save = {
            "ticker": ticker_input.upper(),
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "score": score,
            "kgv": kgv,
            "kbv": kbv,
            "dividende": div_yield_percent,
            "gewinn": gewinn,
            "verschuldung": debt_ratio
        }
        save_to_db(to_save)
        st.success("Bewertung gespeichert.")

    # Verlauf anzeigen
    st.subheader("📅 Bewertungshistorie")
    history = load_history(ticker_input.upper())
    if history:
        df_hist = pd.DataFrame(history, columns=["Datum", "Score", "KGV", "KBV", "Dividende", "Gewinn", "Verschuldung"])
        st.dataframe(df_hist)
    else:
        st.write("Keine gespeicherten Bewertungen für diese Aktie.")

    # --- Chart-Optionen ---
    st.subheader("📊 Chart Kennzahlenverlauf")
    hist_data = ticker.history(period="1y")
    if hist_data.empty:
        st.write("Keine historischen Kursdaten verfügbar.")
    else:
        columns_map = {
            "Schlusskurs": "Close",
            "Volumen": "Volume",
            "Eröffnung": "Open",
            "Hoch": "High",
            "Tief": "Low"
        }
        chart_option = st.selectbox("Kennzahl wählen", list(columns_map.keys()))
        column_name = columns_map[chart_option]

        fig, ax = plt.subplots()
        ax.plot(hist_data.index, hist_data[column_name], label=chart_option)
        ax.set_title(f"{ticker_input.upper()} - {chart_option} Verlauf (1 Jahr)")
        ax.set_xlabel("Datum")
        ax.set_ylabel(chart_option)
        ax.legend()
        plt.xticks(rotation=45)
        st.pyplot(fig)
