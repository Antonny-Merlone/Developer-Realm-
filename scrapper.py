
import mysql.connector
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

class StockScraper:
    def __init__(self, db_config):
        self.db_config = db_config
        self.stocks = {
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corp.',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'TSLA': 'Tesla Inc.'
        }

    def scrape_google_finance(self, symbol):
        url = f"https://www.google.com/finance/quote/{symbol}:NASDAQ"
        response = requests.get(url)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            price_element = soup.find("div", class_="YMlKec fxKbKc")
            
            if price_element:
                price = price_element.text.replace('$', '').replace(',', '')
                return {
                    'symbol': symbol,
                    'price': float(price),
                    'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
        return None

    def get_alpha_vantage_data(self, symbol, api_key):
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={symbol}&apikey={api_key}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                df = pd.DataFrame.from_dict(time_series, orient="index")
                df.columns = ["Open", "High", "Low", "Close", "Volume"]
                return df
        return None

    def save_to_mysql(self, stock_data):
        try:
            conn = mysql.connector.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS scrapper (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symbol VARCHAR(10),
                price DECIMAL(10, 2),
                date DATETIME,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            cursor.execute(create_table_query)
            
            # Insert stock data
            insert_query = """
            INSERT INTO scrapper (symbol, price, date)
            VALUES (%s, %s, %s)
            """
            values = (stock_data['symbol'], stock_data['price'], stock_data['date'])
            
            cursor.execute(insert_query, values)
            conn.commit()
            
            print(f"Successfully saved {stock_data['symbol']} data to database")
            
        except mysql.connector.Error as err:
            print(f"Database error: {err}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()

def main():
    # Database configuration
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'trial_db'
    }
    
    # Initialize scraper
    scraper = StockScraper(db_config)
    
    # Scrape and save data for each stock
    for symbol in scraper.stocks.keys():
        print(f"\nProcessing {scraper.stocks[symbol]}...")
        stock_data = scraper.scrape_google_finance(symbol)
        
        if stock_data:
            print(f"{scraper.stocks[symbol]} Stock Price: ${stock_data['price']}")
            scraper.save_to_mysql(stock_data)
        else:
            print(f"Failed to retrieve data for {symbol}")

if __name__ == "__main__":
    main()

