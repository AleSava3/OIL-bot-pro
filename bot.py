import time
import requests
import os
from datetime import datetime
from strategy import get_data, calculate_indicators, get_trend, generate_entry
from news_fetcher import get_oil_news
from news_analyzer import analyze_news

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

MAX_SIGNALS_PER_DAY = 15
MAX_SIGNALS_PER_HOUR = 3

signals_sent_today = 0
signals_sent_hour = 0
last_hour = 0
sent_signals = set()


def send_message(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": CHAT_ID, "text": text})


def run_bot():
    global signals_sent_today, signals_sent_hour, last_hour, sent_signals

    while True:
        try:
            now = datetime.now()

            if now.hour != last_hour:
                signals_sent_hour = 0
                last_hour = now.hour

            if signals_sent_today >= MAX_SIGNALS_PER_DAY:
                time.sleep(300)
                continue

            # 📊 M15 → direzione
            df_m15 = get_data("15m")
            df_m15 = calculate_indicators(df_m15)
            trend = get_trend(df_m15)

            if trend is None:
                time.sleep(60)
                continue

            # ⚡ M5 → entry
            df_m5 = get_data("5m")
            df_m5 = calculate_indicators(df_m5)

            signal, entry, strength = generate_entry(df_m5, trend)

            if signal is None:
                time.sleep(60)
                continue

            # 🧠 news
            news = get_oil_news()
            sentiment = analyze_news(news)

            signal_id = f"{signal}-{round(entry,1)}"
            if signal_id in sent_signals:
                time.sleep(60)
                continue

            # filtro news leggero
            if sentiment == "BULLISH" and signal == "SELL":
                time.sleep(60)
                continue

            if sentiment == "BEARISH" and signal == "BUY":
                time.sleep(60)
                continue

            # 🎯 SL / TP
            if strength == "SNIPER_TREND":
                sl = entry - 0.6 if signal == "BUY" else entry + 0.6
                tp = entry + 1.2 if signal == "BUY" else entry - 1.2
            else:
                sl = entry - 0.7 if signal == "BUY" else entry + 0.7
                tp = entry + 1.0 if signal == "BUY" else entry - 1.0

            confidence = 75

            if (sentiment == "BULLISH" and signal == "BUY") or \
               (sentiment == "BEARISH" and signal == "SELL"):
                confidence += 10

            message = f"""
🎯 CRUDE OIL PRO

Tipo: {signal} ({strength})

Entry: {entry:.2f}
SL: {sl:.2f}
TP: {tp:.2f}

📊 Trend M15: {trend}
🧠 Bias: {sentiment}
📊 Confidence: {confidence}%
"""

            send_message(message)

            signals_sent_today += 1
            signals_sent_hour += 1
            sent_signals.add(signal_id)

            time.sleep(90)

        except Exception as e:
            print("Errore:", e)
            time.sleep(60)


if __name__ == "__main__":
    run_bot()