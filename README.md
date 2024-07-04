# ETL de dados da API Fake Store

Este projeto implementa um pipeline de dados (Extração, Transformação e Carga) utilizando a linguagem de programação Python e o paradigma de Programação Orientada a Objetos (POO). O objetivo é extrair dados da API Fake Store, transformá-los e carregá-los em um arquivo CSV. Além disso, os dados foram transformados para considerar as seguintes informações especificas para serem armazenadas no arquivo final: 

- identificador de usuário;
- data mais recente em que o usuário adicionou produtos ao carrinho;
- categoria em que o usuário tem mais produtos adicionados ao carrinho.

## Estrutura do Projeto

- `script_etl_fake-store.ipynb`: Script principal que contém a implementação do pipeline ETL.
- `user_cart_data.csv`: Arquivo CSV gerado contendo os dados transformados.
- `README.md`: Este arquivo de documentação.

## Detalhes do Pipeline

### Extração (Extract)

A fase de extração envolve a coleta dos dados da API Fake Store. Utilizamos a biblioteca `requests` para fazer requisições HTTP GET e obter os dados em formato JSON.

```python
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

### Transformação (Transform)

Na fase de transformação, processamos os dados para obter as seguintes informações:

Identificador de usuário (user_id)
Data mais recente em que o usuário adicionou produtos ao carrinho (last_added_date)
Categoria em que o usuário tem mais produtos adicionados ao carrinho (top_category)
Utilizamos um dicionário para acumular essas informações e, em seguida, transformamos os dados em um formato adequado para carregamento.

```python
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
