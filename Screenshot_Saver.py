import streamlit as st
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from PIL import Image
import os
import io
import time
from datetime import datetime
import logging
import requests
import json

# 로깅 설정
logging.basicConfig(filename='app_errors.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_chrome_driver():
    # 크롬 드라이버 옵션 설정
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--enable-unsafe-swiftshader")
    return options

def create_output_folder(base_folder):
    # 출력 폴더 생성
    today = datetime.now().strftime("%Y-%m-%d")
    new_folder_path = os.path.join(base_folder, today)
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    return new_folder_path

def full_page_screenshot(driver, output_folder, url):
    # 전체 페이지 스크린샷 캡처
    safe_url = url.replace('/', '_').replace('?', '_').replace(':', '_').replace('*', '_').replace('|', '_')
    filename = f"{datetime.now().strftime('%Y%m%d_%H%M')}_{safe_url}.png"
    total_width = driver.execute_script("return document.body.scrollWidth")
    total_width = min(total_width, 2300)
    driver.set_window_size(total_width, 1080)
    total_height = int(driver.execute_script("return document.body.scrollHeight"))
    window_height = int(driver.execute_script("return window.innerHeight"))
    scrolls = (total_height // window_height) + (1 if total_height % window_height > 0 else 0)
    stitched_image = Image.new('RGB', (total_width, total_height))
    for scroll in range(scrolls):
        driver.execute_script(f"window.scrollTo(0, {scroll * window_height})")
        time.sleep(0.5)
        screenshot = driver.get_screenshot_as_png()
        screenshot_image = Image.open(io.BytesIO(screenshot))
        stitched_image.paste(screenshot_image, (0, scroll * window_height))
    stitched_image.save(os.path.join(output_folder, filename))

def extract_and_save_text(url, output_folder):
    # 웹 페이지 텍스트 추출 및 저장
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        tags_to_capture = ['h1', 'h2', 'h3', 'ul', 'ol', 'div', 'meta', 'title'] # 내용과 양에 따라 수정 필요
        elements = [elem for elem in soup.find_all(tags_to_capture) if len(elem.get_text(strip=True)) >= 10]
        page_data = [{'tag': elem.name, 'attributes': dict(elem.attrs), 'text': elem.get_text(strip=True)} for elem in elements]
        safe_url = url.replace('/', '_').replace('?', '_').replace(':', '_').replace('*', '_').replace('|', '_')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{timestamp}_{safe_url}.json"
        filepath = os.path.join(output_folder, filename)
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(page_data, file, indent=4, ensure_ascii=False)

def click_and_capture(driver, url, output_folder):
    # 링크 클릭 및 캡처 처리
    visited_urls = set()
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    links = driver.find_elements(By.CSS_SELECTOR, "a[href]")
    progress_bar = st.progress(0)
    for index, link in enumerate(links): # 페이지 내의 다른 페이지 링크 탐색
        href = link.get_attribute('href')
        if href and href not in visited_urls and link.is_displayed(): # 중복 및 표시 안 되는 링크 제외
            visited_urls.add(href)
            main_window = driver.current_window_handle
            try:
                driver.execute_script("window.open();")
                secondary_window = driver.window_handles[1]
                driver.switch_to.window(secondary_window)
                driver.get(href)
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                full_page_screenshot(driver, output_folder, href)
                extract_and_save_text(href, output_folder)
                st.info(f"Processed: {href}")
                progress_bar.progress((index + 1) / len(links)) # 진행 상황 업데이트
            except Exception as e:
                logging.error(f"Error processing link {index + 1}: {str(e)}")
            finally:
                if secondary_window:
                    driver.close()
                    driver.switch_to.window(main_window)
    progress_bar.empty()

def take_screenshots(url, base_folder):
    # 스크린샷 촬영 및 저장
    output_folder = create_output_folder(base_folder)
    options = setup_chrome_driver()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    click_and_capture(driver, url, output_folder)
    driver.quit()

def main():
    st.title('Web Page Screenshot and Text Extraction Tool')
    url = st.text_input('Enter the URL of the website:', '')
    base_folder = st.text_input('Enter the base path of the folder to save screenshots and text files:', '')
    if st.button('Start Processing'):
        if url and base_folder:
            take_screenshots(url, base_folder)
            st.success('All tasks have been completed successfully.')
        else:
            st.error('Please enter a valid URL and folder path.')

if __name__ == "__main__":
    main()
