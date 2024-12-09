import time
import pandas as pd
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By


def scraping(kwd, num):

    driver = webdriver.Chrome()
    # driver = webdriver.Firefox()
    driver.maximize_window()
    driver.get(f"https://mercari-shops.com/search?keyword={kwd}")
    time.sleep(5)

    store_urls = []
    index = -1

    while len(store_urls) < num:
        index += 1
        print(f"...........................................................................{index}")
        try:
            if index % 80 == 0:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

                items = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-box"]')

            item_info = {}
            
            # -------------------------
            # 商品URL
            # -------------------------
            item_info['detail_url'] = items[index].find_element(By.TAG_NAME, "a").get_attribute('href')
            print(f"detail_url _____ _____ _____ {item_info['detail_url']}")

            driver.execute_script("window.open(arguments[0], '_blank');", item_info['detail_url'])
            time.sleep(2)

            driver.switch_to.window(driver.window_handles[1])
            time.sleep(1)

            info_div = driver.find_element(By.ID, "product-info")

            store_element = info_div.find_element(By.CSS_SELECTOR, 'a[data-testid="shops-profile-link"]')

            # -------------------------
            # ストア情報
            # -------------------------
            item_info['store_url'] = store_element.get_attribute('href').split('?')[0]
            print(f"store_url _____ _____ _____ {item_info['store_url']}")

            if item_info['store_url'] in store_urls:
                print('duplicated')
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                time.sleep(1)
                continue
            else:
                store_urls.append(item_info['store_url'])

            item_info['store_name'] = store_element.find_element(By.TAG_NAME, 'p').text
            print(f"store_name _____ _____ _____ {item_info['store_name']}")

            item_info['store_reviews'] = store_element.find_element(By.TAG_NAME, 'span').text
            print(f"store_reviews _____ _____ _____ {item_info['store_reviews']}")

            # -------------------------
            # 商品名
            # -------------------------
            item_info['title'] = info_div.find_element(By.CSS_SELECTOR, 'div[data-testid="product-title-section"]').text
            print(f"title _____ _____ _____ {item_info['title']}")
            
            # -------------------------
            # 商品価格
            # -------------------------
            item_info['price'] = info_div.find_element(By.CSS_SELECTOR, 'div[data-testid="product-price"]').text
            print(f"price _____ _____ _____ {item_info['price']}")

            # -------------------------
            # 商品レビュー数
            # -------------------------
            item_info['review'] = info_div.find_element(By.CSS_SELECTOR, 'a[data-testid="product-reviews"]').find_element(By.TAG_NAME, 'span').text
            print(f"review _____ _____ _____ {item_info['review']}")

            # -------------------------
            # 商品の状態
            # -------------------------
            item_info['status'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='商品の状態']").text
            print(f"status _____ _____ _____ {item_info['status']}")

            # -------------------------
            # 配送料の負担
            # -------------------------
            item_info['shipping_charge'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='配送料の負担']").text
            print(f"shipping_charge _____ _____ _____ {item_info['shipping_charge']}")
            
            # -------------------------
            # 配送の方法
            # -------------------------
            item_info['shipping_method'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='配送の方法']").text
            print(f"shipping_method _____ _____ _____ {item_info['shipping_method']}")
            
            # -------------------------
            # 発送元の地域
            # -------------------------
            item_info['origin'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='発送元の地域']").text
            print(f"origin _____ _____ _____ {item_info['origin']}")
            
            # -------------------------
            # 発送までの日数
            # -------------------------
            item_info['delivery_time'] = info_div.find_element(By.CSS_SELECTOR, "span[data-testid='発送までの日数']").text
            print(f"delivery_time _____ _____ _____ {item_info['delivery_time']}")

            data = {
                "検索キーワード": kwd,
                "ストアURL": item_info['store_url'],
                "ストアレビューURL": f"{item_info['store_url']}/reviews",
                "ストア名": item_info['store_name'],
                "ストアレビュー数": item_info['store_reviews'],
                "商品URL": item_info['detail_url'],
                "商品名": item_info['title'],
                "商品価格": item_info['price'],
                "レビュー数": item_info['review'],
                "商品の状態": item_info['status'],
                "配送料の負担": item_info['shipping_charge'],
                "配送の方法": item_info['shipping_method'],
                "発送元の地域": item_info['origin'],
                "発送までの日数": item_info['delivery_time']
            }

            # Save to CSV
            out = pd.DataFrame([data])
            out.to_csv("output.csv", mode="a", header=not pd.io.common.file_exists("output.csv"), index=False, encoding="utf-8-sig")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)

        except Exception as e:
            print('詳細情報の取得に失敗しました。', e)
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            time.sleep(1)
            continue

    driver.quit()

    messagebox.showinfo("OK", "スクレイピング完了しました。")


if __name__ == "__main__":
    scraping("LEDライト", 200)
