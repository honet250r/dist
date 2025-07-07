import tkinter as tk
import yfinance as yf
import threading
import time

# --- Configuration ---
# Ticker symbol for Nikkei 225 on Yahoo Finance
NIKKEI_TICKER = "^N225"
USDJPY_TICKER = "JPY=X" # Ticker symbol for USD/JPY
UPDATE_INTERVAL_MS = 60000  # 1 minute

# --- Main Application Class ---
class StockTicker(tk.Tk):
    def __init__(self):
        super().__init__()

        # Window Configuration
        self.title("Nikkei 225 & USD/JPY")
        self.geometry("144x80+100+100")  # Wider and taller for two lines
        self.overrideredirect(True)  # Remove window decorations
        self.attributes("-topmost", True)  # Always on top

        # Labels to display the prices
        self.nikkei_label = tk.Label(self, text="Nikkei: Loading...", font=("Arial", 14, "bold"), fg="white", bg="black")
        self.nikkei_label.grid(row=0, column=0, sticky="nsew")
        self.usdjpy_label = tk.Label(self, text="USD/JPY: Loading...", font=("Arial", 14, "bold"), fg="white", bg="black")
        self.usdjpy_label.grid(row=1, column=0, sticky="nsew")

        # Configure grid to expand with window
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Make window draggable
        self.bind("<ButtonPress-1>", self.start_move)
        self.bind("<ButtonRelease-1>", self.stop_move)
        self.bind("<B1-Motion>", self.do_move)

        # Right-click context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Update Now", command=self.update_price) # Manual update
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Exit", command=self.quit_app)
        self.bind("<Button-3>", self.show_context_menu)

        # Start the update loop
        self.update_price()

    def get_prices(self):
        """Fetches Nikkei 225 and USD/JPY prices using yfinance."""
        nikkei_price = "N/A"
        usdjpy_price = "N/A"
        try:
            # Fetch Nikkei 225
            nikkei = yf.Ticker(NIKKEI_TICKER)
            info_nikkei = nikkei.info
            current_nikkei = info_nikkei.get('currentPrice')
            if current_nikkei is not None:
                nikkei_price = f"{int(current_nikkei):,}"
            else:
                hist_nikkei = nikkei.history(period="1d")
                if not hist_nikkei.empty:
                    nikkei_price = f"{int(hist_nikkei['Close'].iloc[-1]):,}"

            # Fetch USD/JPY
            usdjpy = yf.Ticker(USDJPY_TICKER)
            info_usdjpy = usdjpy.info
            current_usdjpy = info_usdjpy.get('currentPrice')
            if current_usdjpy is not None:
                usdjpy_price = f"{current_usdjpy:,.2f}"
            else:
                hist_usdjpy = usdjpy.history(period="1d")
                if not hist_usdjpy.empty:
                    usdjpy_price = f"{hist_usdjpy['Close'].iloc[-1]:,.2f}"

        except Exception as e:
            print(f"Error fetching data with yfinance: {e}")
            return "Error", "Error"
        return nikkei_price, usdjpy_price

    def update_price(self):
        """Updates the price labels with the latest fetched prices."""
        def fetch_and_update():
            nikkei_price, usdjpy_price = self.get_prices()
            self.nikkei_label.config(text=f"{nikkei_price}")
            self.usdjpy_label.config(text=f"{usdjpy_price}")
            # Schedule the next update
            self.after(UPDATE_INTERVAL_MS, self.update_price)

        # Run the fetching in a separate thread to avoid blocking the GUI
        threading.Thread(target=fetch_and_update, daemon=True).start()

    def show_context_menu(self, event):
        """Displays the context menu on right-click."""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def quit_app(self):
        """Closes the application."""
        self.destroy()

    # --- Window Dragging Methods ---
    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

# --- Main Execution ---
if __name__ == "__main__":
    app = StockTicker()
    app.mainloop()