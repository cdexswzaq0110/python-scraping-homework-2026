import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


def create_driver():
    """建立並回傳 Chrome WebDriver。"""

    options = Options()

    # 反自動化偵測設定
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # 偽裝一般 Windows Chrome 使用者
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/121.0.0.0 Safari/537.36"
    )

    # 關閉 Blink 自動化特徵
    options.add_argument("--disable-blink-features=AutomationControlled")

    # Selenium 4.6+ 通常會自動處理 ChromeDriver
    driver = webdriver.Chrome(options=options)

    return driver


def open_manga_page(driver, url):
    """開啟漫畫詳情頁。"""

    driver.get(url)
    print("Page Title:", driver.title)


def click_free_read_button(driver):
    """點擊漫畫詳情頁中的免費閱讀按鈕。"""

    button = driver.find_element(By.CSS_SELECTOR, "button.open-viewer.book-begin.ga")
    button.click()
    print("已點擊免費閱讀按鈕")


def switch_to_new_window(driver):
    """切換到最新開啟的瀏覽器分頁。"""

    time.sleep(2)
    all_windows = driver.window_handles
    driver.switch_to.window(all_windows[-1])
    print("已切換到新視窗")


def click_read_now(driver):
    """點擊「すぐに読む」連結。"""

    wait = WebDriverWait(driver, 10)

    read_now = wait.until(
        EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "すぐに読む"))
    )
    read_now.click()

    print("已點擊すぐに読む")
    time.sleep(3)


def download_manga_by_screenshot(driver, output_dir="downloaded_manga"):
    """
    自動翻頁並截圖目前可見的漫畫圖片。

    參數：
    driver: Selenium WebDriver
    output_dir: 儲存圖片的資料夾名稱
    """

    os.makedirs(output_dir, exist_ok=True)

    wait_element = WebDriverWait(driver, 10)
    total_image_count = 0

    while True:
        # 取得目前畫面上的漫畫圖片元素
        image_elements = driver.find_elements(By.CSS_SELECTOR, "div.page_image img.image")

        for img_element in image_elements:
            # 只截圖目前可見的圖片，避免抓到隱藏頁面
            if img_element.is_displayed():
                file_path = os.path.join(
                    output_dir,
                    f"manga_page_{total_image_count:03d}.png"
                )

                img_element.screenshot(file_path)
                print(f"成功擷取頁面並儲存為: {file_path}")

                total_image_count += 1

        try:
            # 等待下一頁按鈕可以點擊
            next_page = wait_element.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.flip.flip-left"))
            )

            next_page.click()
            print("已點擊下一頁，等待畫面載入...")

            time.sleep(2)

        except TimeoutException:
            print("【系統提示】找不到下一頁按鈕，已達最後一頁，結束爬取迴圈。")
            break

    print(f"總共儲存 {total_image_count} 張圖片")


def main():
    """主程式入口。"""

    manga_url = "https://www.mangaz.com/book/detail/157901"
    output_dir = "downloaded_manga"

    driver = create_driver()

    try:
        open_manga_page(driver, manga_url)
        click_free_read_button(driver)
        switch_to_new_window(driver)
        click_read_now(driver)
        download_manga_by_screenshot(driver, output_dir)

    finally:
        driver.quit()
        print("WebDriver 已關閉")


if __name__ == "__main__":
    main()
