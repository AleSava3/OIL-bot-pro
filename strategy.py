import yfinance as yf
import pandas as pd

def get_data(interval):
    df = yf.download("CL=F", period="1d", interval=interval)

    if df is None or df.empty:
        return None

    # 🔥 FIX CRUCIALE: appiattisce colonne multi-index
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # tieni solo colonne base
    df = df[["Open", "High", "Low", "Close", "Volume"]]

    df = df.dropna()

    return df


def calculate_indicators(df):
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()

    delta = df["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()

    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df


def generate_signal(df):
    if df is None or df.empty:
        return [], None

    last = df.iloc[-1]

    try:
        # 🔥 FORZA VALORI NUMERICI REALI
        ema20 = float(last["EMA20"])
        ema50 = float(last["EMA50"])
        rsi = float(last["RSI"])
        price = float(last["Close"])
    except:
        return [], None

    signals = []

    # STRONG
    if ema20 > ema50 and rsi < 65:
        signals.append(("BUY", "STRONG"))

    if ema20 < ema50 and rsi > 35:
        signals.append(("SELL", "STRONG"))

    # SCALP
    if rsi < 30:
        signals.append(("BUY", "SCALP"))

    if rsi > 70:
        signals.append(("SELL", "SCALP"))

    # INTRADAY
    if 40 < rsi < 60:
        if ema20 > ema50:
            signals.append(("BUY", "INTRADAY"))
        elif ema20 < ema50:
            signals.append(("SELL", "INTRADAY"))

    return signals, price
