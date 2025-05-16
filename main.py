import tkinter as tk
from tkinter import ttk
from db import init_db
from gui_tabs import create_tab1, create_tab2, create_tab3

def main():
    init_db()

    window = tk.Tk()
    window.title("Aktien Portfolio App mit WKN-Datenbank")
    window.geometry("850x750")

    notebook = ttk.Notebook(window)
    notebook.pack(expand=True, fill='both')

    tab1 = create_tab1(notebook)
    notebook.add(tab1, text='Kurs & Kennzahlen')

    # Wir übergeben eine Funktion, damit Tab2 Tab3 refreshen kann
    tab3 = create_tab3(notebook)
    notebook.add(tab3, text='Portfolio verwalten')

    tab2 = create_tab2(notebook, refresh_portfolio_tab_callback=tab3.refresh_all)
    notebook.add(tab2, text='Aktie/ETF hinzufügen')

    window.mainloop()

if __name__ == "__main__":
    main()
