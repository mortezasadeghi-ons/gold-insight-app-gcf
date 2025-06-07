import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Gold Insight", layout="wide")
st.title("📈 تحلیل انس جهانی طلا")

days = st.sidebar.slider("تعداد روزهای گذشته برای تحلیل:", 30, 365, 90)
symbol = "GC=F"

@st.cache_data
def get_data():
    end = datetime.today()
    start = end - timedelta(days=days)
    df = yf.download(symbol, start=start, end=end)
    if df.empty:
        return df
    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["RSI"] = compute_rsi(df["Close"])
    return df

def compute_rsi(data, period=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

df = get_data()

if df.empty:
    st.error("❌ داده‌ای برای نمایش وجود ندارد. احتمالاً اتصال به Yahoo Finance برقرار نیست.")
else:
    st.subheader("📊 نمودار قیمت و میانگین‌های متحرک")
    st.line_chart(df[["Close", "EMA20", "EMA50"]])

    st.subheader("📉 شاخص RSI")
    st.line_chart(df["RSI"])

    latest_price = df["Close"].iloc[-1]
    latest_rsi = df["RSI"].iloc[-1]

    st.metric("💰 قیمت لحظه‌ای انس", f"${latest_price:.2f}")
    st.metric("📉 RSI", f"{latest_rsi:.2f}")

    if latest_rsi < 30:
        st.success("✅ سیگنال خرید (Oversold)")
    elif latest_rsi > 70:
        st.error("⚠️ سیگنال فروش (Overbought)")
    else:
        st.info("🔄 بدون سیگنال قطعی")

    st.subheader("📰 آخرین اخبار طلا از CNBC")
    def get_news():
        try:
            url = "https://www.cnbc.com/gold/"
            r = requests.get(url)
            soup = BeautifulSoup(r.content, "html.parser")
            headlines = soup.find_all("a", class_="Card-title", limit=5)
            return [h.text.strip() for h in headlines]
        except:
            return ["خطا در دریافت اخبار."]
    for news in get_news():
        st.write("• " + news)
