# ETL Pipeline para Dados da API Fake Store

Este projeto implementa um pipeline de ETL (Extração, Transformação e Carga) utilizando a linguagem de programação Python. O objetivo é extrair dados da API Fake Store, transformá-los e carregá-los em um arquivo CSV.

## Estrutura do Projeto

- `etl_process.py`: Script principal que contém a implementação do pipeline ETL.
- `user_cart_data.csv`: Arquivo CSV gerado contendo os dados transformados.
- `README.md`: Este arquivo de documentação.

## Detalhes do Pipeline

### Extração (Extract)

A fase de extração envolve a coleta dos dados da API Fake Store. Utilizamos a biblioteca `requests` para fazer múltiplas requisições HTTP GET e obter todos os dados em formato JSON.

```python
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
    self.cart_data = self.fetch_all_pages(self.carts_url)
    product_response = requests.get(self.products_url)
    if product_response.status_code == 200:
        self.product_data = product_response.json()
    else:
        raise Exception("Failed to fetch product data from API")
