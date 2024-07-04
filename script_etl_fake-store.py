import requests
import pandas as pd
from datetime import datetime

class ETLProcess:
    def __init__(self, carts_url, products_url):
        self.carts_url = carts_url
        self.products_url = products_url
        self.cart_data = None
        self.product_data = None

    def extract(self):
        cart_response = requests.get(self.carts_url)
        if cart_response.status_code == 200:
            self.cart_data = cart_response.json()
        else:
            raise Exception("Failed to fetch cart data from API")

        product_response = requests.get(self.products_url)
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

    def load(self, output_file):
        if not self.data:
            raise Exception("No data to load")
        
        df = pd.DataFrame(self.data)
        df.to_csv(output_file, index=False)

    def run(self, output_file):
        self.extract()
        self.transform()
        self.load(output_file)

if __name__ == "__main__":
    etl = ETLProcess(carts_url="https://fakestoreapi.com/carts", products_url="https://fakestoreapi.com/products")
    etl.run(output_file="user_cart_data.csv")