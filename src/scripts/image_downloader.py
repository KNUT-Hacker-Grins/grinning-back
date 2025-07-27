import os
import time
import requests
import time, random
from enum import Enum
from PIL import Image
from io import BytesIO
from typing import Union
from PIL import UnidentifiedImageError
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException   
from chrome_manager import ChromeDriverService

class ScrollBehavior(Enum):
    AUTO = "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });"
    SMOOTH = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });"
    END = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end' });"

def scroll_into_view(browser: Chrome, element: WebElement, scroll_script: str = ScrollBehavior.AUTO.value, wait_time: Union[int, float, None] = None):
    """Scrolls the browser to bring the element into view."""
    if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
        wait_time = random.uniform(1, 2)
    
    browser.execute_script(scroll_script, element)
    time.sleep(wait_time)

class ImgDownloadCrawler(ChromeDriverService):
    def search_query(self, query):
        search_box = self.browser.find_element(By.CSS_SELECTOR, "textarea.gLFyf")
        search_box.send_keys(query)
        search_box.submit()
        time.sleep(2)

    def find_image_elems(self):
        image_elements = self.browser.find_elements(By.CSS_SELECTOR, "div.eA0Zlc.WghbWd.FnEtTd.mkpRId.m3LIae.RLdvSe.qyKxnc.ivg-i.PZPZlf.GMCzAd")
        if not image_elements:
            print("이미지를 찾을 수 없습니다.")
            return None
        print(f"총 이미지 갯수: {len(image_elements)}")
        return image_elements

    def get_image_url(self):
        actual_images = self.browser.find_element(By.CSS_SELECTOR, "img.sFlh5c.FyHeAf.iPVvYb")
        image_url = None    
        src = actual_images.get_attribute("src")
        if src and "http" in src:
            image_url = src

        return image_url
        
    def download_and_save(self, image_url, query, image_num):
        response = requests.get(image_url, verify=False, timeout=10)
        response.raise_for_status()

        content_type = response.headers.get("Content-Type", "")
        if not content_type.startswith("image/"):
            print(f"❌ 이미지가 아님: {content_type}")
            return

        image = Image.open(BytesIO(response.content))
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        filename = f"{query}_{image_num}.jpg"
        image.save(os.path.join(query, filename))
        print(f"✅ 저장 완료: {filename}")

    def start_download(self, query, num):
        index = 0
        image_num = 1
        os.makedirs(query, exist_ok=True)
        
        try:
            self.start(url="https://www.google.com/imghp", headless=False)
            self.search_query(query)
            image_elements = self.find_image_elems()
            
            while index <= num:
                try:
                    index += 1
                    scroll_into_view(self.browser, image_elements[index])
                    image_elements[index].click()
                    time.sleep(1)

                    image_url = self.get_image_url()
                    self.download_and_save(image_url, query, image_num)
                    image_num += 1

                except NoSuchElementException:
                    print(f"❌ 크롤러가 요소를 찾을 수 없음")
                    continue
                except UnidentifiedImageError:
                    print(f"❌ PIL이 이미지를 식별할 수 없음 (index: {index})")
                    continue
                except requests.exceptions.SSLError:
                    print(f"❌ SSL 오류: {image_url}")
                    continue
                except requests.exceptions.RequestException as e:
                    print(f"❌ 요청 실패: {e}")
                    continue
                except Exception as e:
                    print(f"❌ ERROR: {e}")
                    continue
                
        finally:
            self.stop()

if __name__ == "__main__":
    ImgDownloadCrawler().start_download("카드", 50) 
