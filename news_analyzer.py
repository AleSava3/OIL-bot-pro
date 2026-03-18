BULLISH_KEYWORDS = [
    "war","iran","attack","hormuz","supply","disruption","sanctions"
]

BEARISH_KEYWORDS = [
    "inventory","increase","production","stocks","surplus","exports"
]

def analyze_news(news_list):
    score = 0

    for news in news_list:
        text = (news["title"] + " " + news["description"]).lower()

        for word in BULLISH_KEYWORDS:
            if word in text:
                score += 1

        for word in BEARISH_KEYWORDS:
            if word in text:
                score -= 1

    if score > 2:
        return "BULLISH"
    elif score < -2:
        return "BEARISH"
    return "NEUTRAL"
