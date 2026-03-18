import yfinance as yf
import pandas as pd

def get_data(interval):
    df = yf.download("CL=F", period="1d", interval=interval)

    if df is None or df.empty:
        return None

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

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


# 🔥 DIREZIONE M15
def get_trend(df):
    if df is None or df.empty:
        return None

    last = df.iloc[-1]

    try:
        ema20 = float(last["EMA20"])
        ema50 = float(last["EMA50"])
    except:
        return None

    if ema20 > ema50:
        return "BUY"
    elif ema20 < ema50:
        return "SELL"

    return None


# 🎯 ENTRY M5 SNIPER
def generate_entry(df, trend):
    if df is None or df.empty or len(df) < 3:
        return None, None, None

    last = df.iloc[-1]
    prev = df.iloc[-2]

    try:
        rsi = float(last["RSI"])
        price = float(last["Close"])
        prev_close = float(prev["Close"])
    except:
        return None, None, None

    # volatilità minima
    if abs(price - prev_close) < 0.1:
        return None, None, None

    # 🔥 breakout reale
    if trend == "BUY" and price > prev_close and 50 < rsi < 70:
        return "BUY", price, "SNIPER_TREND"

    if trend == "SELL" and price < prev_close and 30 < rsi < 50:
        return "SELL", price, "SNIPER_TREND"

    # ⚡ reversal forte
    if rsi < 25:
        return "BUY", price, "REVERSAL"

    if rsi > 75:
        return "SELL", price, "REVERSAL"

    return None, None, None