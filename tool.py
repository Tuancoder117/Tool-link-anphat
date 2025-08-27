import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# ==== CẤU HÌNH ====
URL = "https://www.anphatpc.com.vn/man-hinh-acer_dm1433.html" #thay link bằng link bạn muốn
PRODUCT_SELECTOR = "div.p-item.js-p-item a.p-name"
LOAD_MORE_SELECTOR = "a.btn-view-more"
WAIT_TIME = 10
SCROLL_PAUSE = 1
OUTPUT_FILE = "data_tab.txt"

# ==== ĐỌC DỮ LIỆU CŨ NẾU CÓ ====
collected = set()
if os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "r", encoding="utf-8-sig") as f:
        for line in f:
            parts = line.strip().split("\t")
            if len(parts) == 2:
                link, name = parts
                collected.add((name, link))
    print(f"Đã tải {len(collected)} sản phẩm từ file cũ.")

# ==== CẤU HÌNH SELENIUM ====
options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_argument("--start-maximized")
driver = webdriver.Chrome(service=Service(), options=options)
driver.get(URL)

# ==== HÀM THU THẬP SẢN PHẨM ====
def collect_products():
    products = driver.find_elements(By.CSS_SELECTOR, PRODUCT_SELECTOR)
    for p in products:
        try:
            name = p.get_attribute("title") or p.text.strip()
            link = p.get_attribute("href")
            if name and link:
                collected.add((name, link))  # tránh trùng bằng set
        except:
            continue

# ==== LOAD TẤT CẢ SẢN PHẨM ====
while True:
    collect_products()
    try:
        btn = driver.find_element(By.CSS_SELECTOR, LOAD_MORE_SELECTOR)
        if btn.is_displayed() and btn.is_enabled():
            driver.execute_script("arguments[0].scrollIntoView(true);", btn)
            time.sleep(SCROLL_PAUSE)
            driver.execute_script("show_more_product('1694','');")
            WebDriverWait(driver, WAIT_TIME).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, PRODUCT_SELECTOR)) > len(collected)
            )
            time.sleep(1)
        else:
            print("Hết sản phẩm để load.")
            break
    except TimeoutException:
        print("Timeout - không thấy sản phẩm mới.")
        break
    except:
        print("Không còn nút 'Xem thêm'.")
        break

collect_products()
print(f"Đã thu thập tổng cộng {len(collected)} sản phẩm (bao gồm dữ liệu cũ).")

# ==== LƯU FILE TAB-DELIMITED ====
with open(OUTPUT_FILE, "w", encoding="utf-8-sig") as f:
    for name, link in collected:
        f.write(f"{link}\t{name}\n")

driver.quit()
print(f"Đã lưu vào {OUTPUT_FILE}.")
