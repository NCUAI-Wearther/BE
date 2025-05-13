import requests

url = "https://api.hm.com/search-services/v1/zh_asia3/listing/resultpage"
params = {
    "pageSource": "PLP",
    "page": 2,
    "sort": "RELEVANCE",
    "pageId": "/ladies/new-arrivals/view-all",
    "page-size": 36,
    "categoryId": "ladies_newarrivals_all",
    "filters": "sale:false||oldSale:false||isNew:true",
    "touchPoint": "DESKTOP",
    "skipStockCheck": "false"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers)
data = response.json()

products = data.get("plpList", {}).get("productList", [])

for product in products:
    name = product.get("productName")
    model_image = product.get("modelImage")
    product_image = product.get("productImage")
    color = product.get("colorName")
    link = f"https://www2.hm.com/{product.get('url')}"
    price = product.get("prices", [{}])[0].get("formattedPrice")

    print(f"商品名稱：{name}")
    print(f"顏色：{color}")
    print(f"連結：{link}")
    print(f"Model圖片：{model_image}")
    print(f"Product圖片：{product_image}")
    print(f"價格：{price}")
    print("-" * 40)
