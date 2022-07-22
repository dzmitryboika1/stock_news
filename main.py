import requests
from auth_data import *
from twilio.rest import Client

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

account_sid = ACCOUNT_SID
auth_token = AUTH_TOKEN
my_phone_number = MY_PHONE_NUMBER
sender_number = SENDER_NUMBER

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
stock_api_key = STOCK_API_KEY

stock_api_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_api_key,
}

NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
NEWS_API_KEY = "3fe4134b27d54b9dba0de18dc69b136d"
news_api_parameters = {
    "q": COMPANY_NAME,
    "searchIn": "title",
    "apiKey": NEWS_API_KEY
}


def make_request(url: str, param: dict) -> dict:
    response = requests.get(url=url, params=param)
    response.raise_for_status()
    return response.json()


def compare_stock_price(data: dict):
    data_list = [value for (key, value) in data["Time Series (Daily)"].items()]
    yesterday_price = float(data_list[0]["4. close"])
    day_before_yesterday_price = float(data_list[1]["4. close"])
    percentage_difference = round((yesterday_price - day_before_yesterday_price) / yesterday_price * 100, 2)
    if percentage_difference >= 0.5:
        return f"TSLA:🔺{percentage_difference}%"
    elif percentage_difference <= -0.5:
        return f"TSLA:🔻{percentage_difference}%"
    else:
        return


def fetch_fresh_news():
    """return 3 fresh most relevant article related to the company"""
    news_data = make_request(NEWS_ENDPOINT, news_api_parameters)
    three_articles = news_data["articles"][:3]
    formatted_articles = [
        f"HeadLine: {article['title']}. \nBrief: {article['description']}" for article in three_articles
    ]
    return formatted_articles


def send_sms(article, percentage: str):
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        body=f"{percentage}\n{article}",
        from_=sender_number,
        to=my_phone_number,
    )
    print(message.status)


stock_data = make_request(STOCK_ENDPOINT, stock_api_parameters)
price_difference = compare_stock_price(stock_data)
if price_difference:
    news_trio = fetch_fresh_news()
    for news in news_trio:
        send_sms(news, price_difference)
