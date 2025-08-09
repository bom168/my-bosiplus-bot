import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# ‼️ เพิ่ม 2 บรรทัดนี้เข้ามา ‼️
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
    
    # --- ส่วนตั้งค่า Chrome เหมือนเดิม ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    with webdriver.Chrome(options=chrome_options) as driver:
        # ‼️ ลบ driver.implicitly_wait(10) ออกไป เพื่อใช้การรอแบบใหม่ ‼️

        # --- ขั้นตอนล็อกอิน (เหมือนเดิม) ---
        print(f"กำลังเข้าสู่หน้าล็อกอิน: {BOSIPLUS_LOGIN_URL}")
        driver.get(BOSIPLUS_LOGIN_URL)
        
        driver.find_element(By.ID, 'username').send_keys(USERNAME)
        driver.find_element(By.ID, 'password').send_keys(PASSWORD)
        driver.find_element(By.TAG_NAME, 'button').click()
        print("ส่งข้อมูลล็อกอินแล้ว")

        # --- เข้าสู่หน้ารายงาน ---
        time.sleep(3) # รอหลังล็อกอินสักครู่
        print(f"กำลังเข้าสู่หน้ารายงาน: {BOSIPLUS_REPORT_URL}")
        driver.get(BOSIPLUS_REPORT_URL)

        # --- ดึงข้อมูลจากตาราง (อัปเกรดใหม่) ---
        print("กำลังรอให้ข้อมูลในตารางโหลด...")
        try:
            # ‼️ ให้บอทรอจนกว่า 'แถวแรก' ของข้อมูลในตารางจะปรากฏขึ้นมา (รอนานสุด 20 วินาที) ‼️
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered > tbody > tr'))
            )
            print("ข้อมูลโหลดสำเร็จ! เริ่มการดึงข้อมูล...")
            
            table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered > tbody > tr')
            print(f"พบข้อมูลทั้งหมด {len(table_rows)} แถว")

            for row in table_rows:
                # ... ส่วนที่เหลือใน for loop เหมือนเดิมทั้งหมด ...
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
            # หากรอนานเกิน 20 วินาทีแล้วข้อมูลยังไม่มา ให้พิมพ์ Error ออกมา
            print(f"ไม่พบข้อมูลในตาราง หรือเกิดข้อผิดพลาด: {e}")
    
    print("บอททำงานเสร็จสิ้น")

if __name__ == '__main__':
    run_bot()
