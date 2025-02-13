from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Set up WebDriver with WebDriver Manager
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
# นาย A เข้าเว็บแอพ
driver.get("http://127.0.0.1:8000/polls/")

try:
    # รอให้รายการ Poll ปรากฏขึ้นมา
    polls = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul li a"))
    )
    
    # ตรวจสอบว่ามี Polls แสดง 5 อันล่าสุด
    assert len(polls) > 0, "No polls available!"
    
    # คลิกเข้าไปที่ Poll แรก
    polls[0].click()
    
    # รอให้หน้าโหวตโหลด
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "form"))
    )
    
    # เลือกตัวเลือกแรกของแบบสำรวจ
    choices = driver.find_elements(By.NAME, "choice")
    assert len(choices) > 0, "No choices available to vote!"
    choices[0].click()
    
    # กดปุ่มโหวต
    vote_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit']")
    vote_button.click()
    
    # ตรวจสอบว่าผลโหวตแสดงขึ้นมา
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "h1"))
    )
    
    # ตรวจสอบว่ามีปุ่ม "Vote again?"
    vote_again_link = driver.find_element(By.LINK_TEXT, "Vote again?")
    assert vote_again_link is not None, "Vote again link not found!"
    
    # กดย้อนกลับไปหน้าหลัก
    back_link = driver.find_element(By.LINK_TEXT, "Back")
    back_link.click()
    
    # ตรวจสอบว่า redirect กลับไปหน้า /polls/
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "ul li a"))
    )
    assert "polls" in driver.current_url, "Did not redirect back to polls index!"
    
    print("Test Passed: Functional test completed successfully.")

except Exception as e:
    print(f"Test Failed: {e}")

finally:
    # ปิด WebDriver
    driver.quit()
