import os
import time
import requests
from PIL import Image
from io import BytesIO
import time, random
from typing import Union
from enum import Enum
from selenium.webdriver.common.by import By
from selenium.webdriver import Chrome
from selenium.webdriver.remote.webelement import WebElement   
from src.scripts.chrome_manager import ChromeDriverService

class ScrollBehavior(Enum):
    AUTO = "arguments[0].scrollIntoView({ behavior: 'auto', block: 'center', inline: 'center' });"
    SMOOTH = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center', inline: 'center' });"
    END = "arguments[0].scrollIntoView({ behavior: 'smooth', block: 'end' });"

class ImgDownloadCrawler(ChromeDriverService):
    def download_google_image(self, query, num):
        if not os.path.exists(query):
            os.mkdir(query)
        
        index = 0
        
        try:
            self.start(url="https://www.google.com/imghp", headless=False)
            # 3. 검색창 찾기 → “지갑” 입력
            search_box = self.browser.find_element(By.CSS_SELECTOR, "textarea.gLFyf")
            search_box.send_keys(query)
            search_box.submit()
            time.sleep(2)

            # 4. 이미지 클릭
            image_elements = self.browser.find_elements(By.CSS_SELECTOR, "div.eA0Zlc.WghbWd.FnEtTd.mkpRId.m3LIae.RLdvSe.qyKxnc.ivg-i.PZPZlf.GMCzAd")
            if not image_elements:
                print("이미지를 찾을 수 없습니다.")
                return
            print(f"총 이미지 갯수: {len(image_elements)}")

            for img in image_elements:
                try:
                    self._scroll_into_view(self.browser, img)
                    img.click()
                    time.sleep(1)

                    # 5. 원본 이미지 URL 가져오기
                    actual_images = self.browser.find_element(By.CSS_SELECTOR, "img.sFlh5c.FyHeAf.iPVvYb")
                    image_url = None    
                    src = actual_images.get_attribute("src")
                    if src and "http" in src:
                        image_url = src

                    if not image_url or image_url in "https://www.intermarket.co.kr":
                        print("원본 이미지 URL을 찾을 수 없습니다.")
                        continue

                    # 6. 이미지 다운로드 및 저장
                    response = requests.get(image_url, verify=False, timeout=10)
                    if "image" not in response.headers.get("Content-Type", ""):
                        print(f"유효하지 않은 이미지 URL: {image_url}")
                        continue

                    image = Image.open(BytesIO(response.content))
                    if image.mode in ("RGBA", "LA", "P"):
                        image = image.convert("RGB")        
                    
                    index += 1
                    image.save(f"./{query}/{query}_{index}.jpg")
                    print(f"이미지가 {query}_{index}로 저장되었습니다.")

                    if index == num:
                        break
                except requests.exceptions.SSLError as ssl_err:
                    print(f"SSL 오류 발생: {ssl_err}")
                    continue  # 다음 이미지로 넘어감
                except requests.exceptions.RequestException as req_err:
                    print(f"요청 실패: {req_err}")
                    continue
                except Exception as e:
                    print(f"ERROR: {e}")
                
        finally:
            self.stop()

        
    def _scroll_into_view(
        self,
        browser: Chrome, 
        element: WebElement,
        scroll_script: str = ScrollBehavior.AUTO.value,  
        wait_time: Union[int, float, None] = None
    ) -> None:
        """Scrolls the browser to bring the element into view."""
        if wait_time is None:  # 호출될 때마다 새로운 랜덤 값 설정
            wait_time = random.uniform(1, 2)
        
        browser.execute_script(scroll_script, element)
        time.sleep(wait_time)

"""{
  "전자제품": ["휴대폰", "이어폰", "노트북"],
  "패션": ["시계", "지갑", "백팩"],
  "기타": ["우산"]
}"""

if __name__ == "__main__":
    ImgDownloadCrawler().download_google_image("카드", 50) 
