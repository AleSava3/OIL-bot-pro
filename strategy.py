import yfinance as yf
import pandas as pd

def get_data(interval):
    df = yf.download("CL=F", period="1d", interval=interval)
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
    last = df.iloc[-1]
    signals = []

    # STRONG
    if last["EMA20"] > last["EMA50"] and last["RSI"] < 65:
        signals.append(("BUY", "STRONG"))

    if last["EMA20"] < last["EMA50"] and last["RSI"] > 35:
        signals.append(("SELL", "STRONG"))

    # SCALP
    if last["RSI"] < 30:
        signals.append(("BUY", "SCALP"))

    if last["RSI"] > 70:
        signals.append(("SELL", "SCALP"))

    # INTRADAY
    if 40 < last["RSI"] < 60:
        if last["EMA20"] > last["EMA50"]:
            signals.append(("BUY", "INTRADAY"))
        elif last["EMA20"] < last["EMA50"]:
            signals.append(("SELL", "INTRADAY"))

    return signals, last["Close"]
