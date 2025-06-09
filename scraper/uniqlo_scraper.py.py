import json
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException


chromedriver_path = './chromedriver-win64/chromedriver.exe'
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

base_url = 'https://www.uniqlo.com/tw/zh_TW/c/'
genders = ['women', 'men']

categories = [
    ['Top','tops'],
    ['Bottom','bottoms'],
    ['Outerwear','outer'],
    ['Outerwear','knit'],
    ['Hat','accessories-cap-hat'],
    ['Shoes','accessories-shoes'],
    ['Socks','inner-wear-socks'],
]

all_base_products_info = []

final_products_data = []

def random_sleep():
    time.sleep(random.uniform(3, 7))

def scroll_to_load_all_products(driver):

    last_height = driver.execute_script("return document.body.scrollHeight")
    last_product_count = 0
    scroll_attempts = 0
    max_scroll_attempts = 10

    while True:
        driver.execute_script("window.scrollBy(0, window.innerHeight * 0.8);")
        
        time.sleep(3)
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        current_product_count = len(driver.find_elements(By.CSS_SELECTOR, ".product-ul .product-li"))
        
        if new_height == last_height and current_product_count == last_product_count:
            scroll_attempts += 1
            if scroll_attempts >= max_scroll_attempts:
                print(f"已嘗試滾動 {max_scroll_attempts} 次，頁面高度和商品數量未再改變，停止滾動。")
                break
        else:
            scroll_attempts = 0

        last_height = new_height
        last_product_count = current_product_count

def get_detail_page_last_img_url(driver_instance, main_handle_instance, link_url_param):
    new_handle = None
    try:
        driver_instance.execute_script("window.open('');")
        new_handle = [h for h in driver.window_handles if h != main_handle_instance][0]
        driver.switch_to.window(new_handle)
        driver.get(link_url_param)
        
        time.sleep(5)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".picture-img"))
        )

        imgs = driver_instance.find_elements(By.CSS_SELECTOR, ".picture-img")
        last_img_url = imgs[-1].get_attribute("src") if imgs else None
        
        return last_img_url
    
    except TimeoutException:
        print(f"⚠️ 載入商品細節頁面超時: {link_url_param}")
        return None
    except NoSuchElementException:
        print(f"⚠️ 在商品細節頁面未找到圖片元素: {link_url_param}")
        return None
    except WebDriverException as e:
        print(f"⚠️ 瀏覽器操作錯誤: {e}")
        return None
    except Exception as e:
        print(f"⚠️ 取得細節圖失敗 (其他錯誤): {e}")
        return None
    finally:
        try:
            driver.close()
            driver.switch_to.window(main_handle_instance)
        except Exception as switch_e:
            print(f"⚠️ 無法切換回主分頁或關閉新分頁 (位於 finally): {switch_e}")


print("--- 開始第一階段：爬取商品基礎資訊 ---")
for gender in genders:
    for category in categories:
        url = f"{base_url}all_{gender}-{category[1]}.html"
        
        if category[0] == 'Hat':
            url=f"{base_url}all_women-accessories-cap-hat.html"
        if category[0] == 'Shoes':
            url=f"{base_url}all_women-accessories-shoes.html"
        print(f"\n🚀 正在處理分類: {category[0]} ({url})")
        random_sleep()
        driver.get(url)

        scroll_to_load_all_products(driver)

        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-ul .product-li"))
            )
            product_elements = driver.find_elements(By.CSS_SELECTOR, ".product-ul .product-li")
            print(f"✅ 在頁面 {url} 找到 {len(product_elements)} 個商品。")

            if not product_elements:
                print(f"頁面 {url} 未找到任何商品元素，跳過此分類。")
                continue
            
            for i, product in enumerate(product_elements):
                try:
                    WebDriverWait(product, 10).until(
                        EC.visibility_of_element_located((By.CSS_SELECTOR, "a.h-a-label"))
                    )
                    
                    a_tag = product.find_element(By.CSS_SELECTOR, "a.h-a-label")
                    link_url = a_tag.get_attribute('href')
                    
                    name_img = a_tag.find_element(By.CSS_SELECTOR, ".picture-img")
                    name = name_img.get_attribute("alt")
                    preview_img_url = name_img.get_attribute("src")

                    price = 0
                    try:
                        price_el = product.find_element(By.CSS_SELECTOR, ".product-price .h-currency")
                        price_text = price_el.text.strip().replace("NT$", "").replace(",", "")
                        price = int(price_text)
                    except NoSuchElementException:
                        try:
                            price_el = product.find_element(By.CSS_SELECTOR, ".origin-price .h-currency")
                            price_text = price_el.text.strip().replace("NT$", "").replace(",", "")
                            price = int(price_text)
                        except NoSuchElementException:
                            price = 0

                    product_base_data = {
                        "id": i,
                        "brand": "UNIQLO",
                        "gender": gender,
                        "category": category[0],
                        "name": name,
                        "preview_pic_url": preview_img_url,
                        "link_url": link_url,
                        "price": price,
                        "product_pic_url": None
                    }
                    all_base_products_info.append(product_base_data)
                    print(f"✅ 提取基礎資訊: {name} | 價格: ${price}")

                except NoSuchElementException as e:
                    print(f"❌ 單筆商品基礎元素未找到錯誤：{e} (跳過此商品)")
                except Exception as e:
                    print(f"❌ 處理單筆商品基礎資訊時發生未預期錯誤：{e} (跳過此商品)")

        except TimeoutException:
            print(f"⚠️ 載入商品列表超時，頁面可能未完全載入: {url}")
        except Exception as e:
            print(f"⚠️ 處理分類頁面時發生錯誤：{url} - {e}")

print(f"\n--- 第一階段完成：共收集 {len(all_base_products_info)} 筆商品基礎資訊 ---")

print("\n--- 開始第二階段：獲取商品詳細頁圖片 ---")
main_handle_for_details = driver.current_window_handle

for i, product_data in enumerate(all_base_products_info):
    name = product_data["name"]
    link_url = product_data["link_url"]
    preview_img_url = product_data["preview_pic_url"]

    print(f"--- 處理詳細圖 {i+1}/{len(all_base_products_info)}: {name} ---")
    random_sleep()

    last_img_url = get_detail_page_last_img_url(driver, main_handle_for_details, link_url)
    
    if last_img_url:
        product_data["product_pic_url"] = last_img_url
        print(f"✅ 成功獲取詳細圖: {name}")
    else:
        product_data["product_pic_url"] = preview_img_url
        print(f"⚠️ 獲取詳細圖失敗，改用預覽圖: {name}")
    
    final_products_data.append(product_data)


driver.quit()

# 寫入 JSON
output_path = "uniqlo_products.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(final_products_data, f, ensure_ascii=False, indent=2)

print(f"\n✅ 共儲存 {len(final_products_data)} 筆商品至 {output_path}")