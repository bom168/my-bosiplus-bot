import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- ส่วนของ USERNAME, PASSWORD, URL เหมือนเดิม ---
USERNAME = os.environ.get('BOSIPLUS_USER')
PASSWORD = os.environ.get('BOSIPLUS_PASS')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

BOSIPLUS_LOGIN_URL = 'https://bsplus.manage-ione.com/th/auth/login'
BOSIPLUS_REPORT_URL = 'https://bsplus.manage-ione.com/th/finance/withdrawal/list'

def run_bot():
    print("เริ่มต้นการทำงานของบอท...")
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("window-size=1920,1080") # 👈 เพิ่มขนาดหน้าจอเผื่อไว้
    
    with webdriver.Chrome(options=chrome_options) as driver:
        
        print(f"กำลังเข้าสู่หน้าล็อกอิน: {BOSIPLUS_LOGIN_URL}")
        driver.get(BOSIPLUS_LOGIN_URL)
        
        try:
            print("กำลังรอให้ช่อง Username โหลดเสร็จ...")
            username_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'username'))
            )
            username_field.send_keys(USERNAME)
            print("กรอก Username สำเร็จ")

            driver.find_element(By.ID, 'password').send_keys(PASSWORD)
            print("กรอก Password สำเร็จ")

            driver.find_element(By.TAG_NAME, 'button').click()
            print("ส่งข้อมูลล็อกอินแล้ว")

            # --- ‼️ เพิ่มเวลารอให้ JavaScript ทำงาน ‼️ ---
            print("รอหลังล็อกอิน 10 วินาที เพื่อให้หน้าเว็บหลักโหลดสมบูรณ์...")
            time.sleep(10) # 👈 เพิ่มเวลารอเป็น 10 วินาที

            print(f"กำลังเข้าสู่หน้ารายงาน: {BOSIPLUS_REPORT_URL}")
            driver.get(BOSIPLUS_REPORT_URL)

            # --- ‼️ เพิ่มเวลารออีกครั้งที่หน้ารายงาน ‼️ ---
            print("รอที่หน้ารายงานอีก 10 วินาที เพื่อให้ JavaScript สร้างปุ่มและตาราง...")
            time.sleep(10) # 👈 เพิ่มเวลารอเป็น 10 วินาที

            print("กำลังค้นหาและคลิกที่แท็บ 'สำเร็จ'...")
            success_tab_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//*[contains(., 'สำเร็จ')]"))
            )
            success_tab_button.click()
            print("คลิกแท็บ 'สำเร็จ' แล้ว!")
            
            time.sleep(5) # รอให้ตารางข้อมูลโหลดใหม่

            print("กำลังรอให้ข้อมูลในตารางโหลด...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table > tbody > tr')) # 👈 ทำให้ Selector ง่ายลง
            )
            print("ข้อมูลโหลดสำเร็จ! เริ่มการดึงข้อมูล...")
            
            table_rows = driver.find_elements(By.CSS_SELECTOR, 'table > tbody > tr') # 👈 ทำให้ Selector ง่ายลง
            print(f"พบข้อมูลทั้งหมด {len(table_rows)} แถว")

            if not table_rows:
                print("ไม่พบข้อมูลในตาราง 'สำเร็จ' ณ เวลานี้")
            
            for row in table_rows:
                # ส่วน for loop เหมือนเดิม
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) > 8:
                    status = cells[8].text.strip()
                    if "สำเร็จ" in status:
                        payload = {
                            'refId': cells[1].text.strip(),
                            'user': cells[2].text.strip(),
                            'time': cells[3].text.strip(),
                            'amount': cells[6].text.strip(),
                            'status': status
                        }
                        print(f"ส่งข้อมูลรายการสำเร็จ: {payload['refId']}")
                        requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print("เกิดข้อผิดพลาดร้ายแรงระหว่างการทำงาน!")
            print(e)
            # driver.save_screenshot('error_screenshot.png')
    
    print("บอททำงานเสร็จสิ้น")

if __name__ == '__main__':
    run_bot()
