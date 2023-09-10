import requests
import os 
import json
from config import cookies, headers, params_listing, json_data_list, params_prices

def file_write(file_name, data): # запись в файл
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

def file_load(file_name): # запись в файл
    with open(file_name) as file:
        return json.load(file)

# Header почаще менять, они слетают
# https://www.mvideo.ru/smartfony-i-svyaz-10/smartfony-205?f_skidka=da&f_tolko-v-nalichii=da

def get_data():

    # отправлем запрос на получение товаров, нам нужны id товаров
    response = requests.get(
        'https://www.mvideo.ru/bff/products/listing', 
        params = params_listing(205), 
        cookies=cookies, 
        headers=headers
    ).json()

    product_ids = response.get("body").get("products")

    file_write(file_name = "1_product_ids.json", data = product_ids)

    # отправляем запрос на получение подробной инфы про товары, отправляя id товаров
    response = requests.post(
        'https://www.mvideo.ru/bff/product-details/list', 
        cookies=cookies, 
        headers=headers, 
        json=json_data_list(product_ids)
        ).json()


    file_write(file_name = "2_products.json", data = response)

    products_ids_str = ",".join(product_ids) # создаем строку с перечислением id товаров 


    # получаем цены
    response = requests.get(
        'https://www.mvideo.ru/bff/products/prices', 
        params = params_prices(products_ids_str), 
        cookies = cookies, 
        headers = headers
        ).json()

    file_write(file_name = "3_prices.json", data = response)

    products_prices = {}
    
    # по json документу доходим до списка 
    material_prices = response.get('body').get('materialPrices') 
    
    # и переходим к перебору этого списка 
    for item in material_prices:
        item_id = item.get('price').get('productId') # находим id товара
        item_base_price = item.get('price').get('basePrice') # Находим стандартную стоимость 
        item_sale_price = item.get('price').get('salePrice') # Находим стоимость со скидкой 
        item_bonus = item.get('bonusRubles').get('total') # Находим бонусные акции
        
        products_prices[item_id] = { # к опредленному id вписываем
            'product_basePrice': item_base_price, # стандартную стоимость 
            'product_salePrice': item_sale_price, # стоимость со скидкой 
            'product_bonus': item_bonus # бонусные акции
        }
        
    file_write(file_name = "4_products_prices.json", data = products_prices)
        
# в этой ф-ии мы совмещаем данные о товаре и цены
def get_result():
    # открываем общую информацию о товарах 
    products_data = file_load(file_name = '2_products.json')

    # открываем цены на эти товары
    products_prices = file_load(file_name = '4_products_prices.json')
    
    # находим товары в объекте 
    products_data = products_data.get('body').get('products')
    
    # проходимся это этим товарам
    for product in products_data:
        # смотрим у них id
        product_id = product.get('productId') 
        
        # если id продукта есть в объекте цен
        if product_id in products_prices:
            # то записываем цены по этому id 
            prices = products_prices[product_id] 
        
        # создаем дополнительные записи в 
        product['product_basePrice'] = prices.get('product_basePrice')
        product['product_salePrice'] = prices.get('product_salePrice')
        product['product_bonus'] = prices.get('product_bonus')
        
    # запись результата 
    file_write(file_name = "5_result.json", data = products_data)


    
def main():
    get_data()
    get_result()

if __name__ == "__main__":
    main()