import time
import requests
import os
from datetime import datetime
from strategy import get_data, calculate_indicators, generate_signal
from news_fetcher import get_oil_news
from news_analyzer import analyze_news

# 🔐 ENV VARIABLES (Railway)
TOKEN = os.getenv("TOKEN", "7371559340:AAHH5CWUka_CgPGKmKVLnAxQZOMk-wEWYLs")
CHAT_ID = os.getenv("CHAT_ID", "742168271")

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

            # reset contatore orario
            if now.hour != last_hour:
                signals_sent_hour = 0
                last_hour = now.hour

            # limite giornaliero
            if signals_sent_today >= MAX_SIGNALS_PER_DAY:
                time.sleep(300)
                continue

            signals_all = []

            # 🔥 MULTI TIMEFRAME
            for tf in ["1m", "5m", "15m"]:
                df = get_data(tf)
                df = calculate_indicators(df)

                signals, price = generate_signal(df)

                for sig, strength in signals:
                    signals_all.append((sig, strength, price, tf))

            # 🧠 NEWS
            news = get_oil_news()
            sentiment = analyze_news(news)

            for signal, strength, entry, tf in signals_all:

                # limite segnali per ora
                if signals_sent_hour >= MAX_SIGNALS_PER_HOUR:
                    break

                # evita duplicati
                signal_id = f"{signal}-{tf}-{round(entry,1)}"
                if signal_id in sent_signals:
                    continue

                # filtro news (soft)
                if sentiment == "BULLISH" and signal == "SELL" and strength == "STRONG":
                    continue

                if sentiment == "BEARISH" and signal == "BUY" and strength == "STRONG":
                    continue

                # 🎯 SL / TP
                if strength == "SCALP":
                    sl = entry - 0.4 if signal == "BUY" else entry + 0.4
                    tp = entry + 0.7 if signal == "BUY" else entry - 0.7

                elif strength == "STRONG":
                    sl = entry - 1.0 if signal == "BUY" else entry + 1.0
                    tp = entry + 2.0 if signal == "BUY" else entry - 2.0

                else:  # INTRADAY
                    sl = entry - 0.7 if signal == "BUY" else entry + 0.7
                    tp = entry + 1.3 if signal == "BUY" else entry - 1.3

                # 📊 CONFIDENCE
                confidence = 55 if strength == "SCALP" else 75

                if (sentiment == "BULLISH" and signal == "BUY") or \
                   (sentiment == "BEARISH" and signal == "SELL"):
                    confidence += 10

                message = f"""
🔥 CRUDE OIL SIGNAL

Tipo: {signal} ({strength})
TF: {tf}

Entry: {entry:.2f}
SL: {sl:.2f}
TP: {tp:.2f}

🧠 Bias: {sentiment}
📊 Confidence: {confidence}%
"""

                send_message(message)

                # aggiorna contatori
                signals_sent_today += 1
                signals_sent_hour += 1
                sent_signals.add(signal_id)

            # reset giornaliero
            if now.hour == 0 and now.minute < 5:
                signals_sent_today = 0
                sent_signals.clear()

            time.sleep(90)

        except Exception as e:
            print("Errore:", e)
            time.sleep(60)


if __name__ == "__main__":
    run_bot()
