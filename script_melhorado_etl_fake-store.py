import requests
import pandas as pd
from datetime import datetime
import concurrent.futures
from sqlalchemy import create_engine

class ETLProcess:
    def __init__(self, carts_url, products_url, db_url):
        self.carts_url = carts_url
        self.products_url = products_url
        self.db_url = db_url
        self.cart_data = []
        self.product_data = None

    def fetch_all_pages(self, url):
        all_data = []
        page = 1
        while True:
            response = requests.get(url, params={'page': page})
            if response.status_code == 200:
                data = response.json()
                if not data:  # No more data to fetch
                    break
                all_data.extend(data)
                page += 1
            else:
                raise Exception("Failed to fetch data from API")
        return all_data

    def extract(self):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_cart = executor.submit(self.fetch_all_pages, self.carts_url)
            future_product = executor.submit(requests.get, self.products_url)
            self.cart_data = future_cart.result()
            product_response = future_product.result()
            if product_response.status_code == 200:
                self.product_data = product_response.json()
            else:
                raise Exception("Failed to fetch product data from API")

    def transform(self):
        if not self.cart_data or not self.product_data:
            raise Exception("No data to transform")
        
        # Create a mapping from productId to category
        product_category_map = {product['id']: product['category'] for product in self.product_data}
        
        users = {}
        for entry in self.cart_data:
            user_id = entry['userId']
            date_added = datetime.fromisoformat(entry['date'])
            
            for product in entry['products']:
                product_id = product['productId']
                category = product_category_map.get(product_id, 'unknown')
                
                if user_id not in users:
                    users[user_id] = {
                        'last_added_date': date_added,
                        'categories': {category: product['quantity']}
                    }
                else:
                    if date_added > users[user_id]['last_added_date']:
                        users[user_id]['last_added_date'] = date_added

                    if category in users[user_id]['categories']:
                        users[user_id]['categories'][category] += product['quantity']
                    else:
                        users[user_id]['categories'][category] = product['quantity']
        
        transformed_data = []
        for user_id, info in users.items():
            max_category = max(info['categories'], key=info['categories'].get)
            transformed_data.append({
                'user_id': user_id,
                'last_added_date': info['last_added_date'].strftime('%Y-%m-%d'),
                'top_category': max_category
            })
        
        self.data = transformed_data

    def load(self):
        if not self.data:
            raise Exception("No data to load")
        
        engine = create_engine(self.db_url)
        df = pd.DataFrame(self.data)
        df.to_sql('user_cart_data', engine, if_exists='replace', index=False)

    def run(self):
        self.extract()
        self.transform()
        self.load()

if __name__ == "__main__":
    etl = ETLProcess(
        carts_url="https://fakestoreapi.com/carts",
        products_url="https://fakestoreapi.com/products",
        db_url="sqlite:///user_cart_data.db"  # database connection string
    )
    etl.run()