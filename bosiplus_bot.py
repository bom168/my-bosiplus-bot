import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
# เพิ่ม 2 บรรทัดนี้
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
        
        print(f"กำลังเข้าสู่หน้าล็อกอิน: {BOSIPLUS_LOGIN_URL}")
        driver.get(BOSIPLUS_LOGIN_URL)
        
        try:
            # --- ‼️ อัปเกรดส่วนล็อกอินให้รออย่างชาญฉลาด ‼️ ---
            print("กำลังรอให้ช่อง Username โหลดเสร็จ...")
            # สั่งให้รอจนกว่าจะเจอ element ที่มี id='username' และสามารถคลิกได้ (รอนานสุด 20 วิ)
            username_field = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.ID, 'username'))
            )
            username_field.send_keys(USERNAME)
            print("กรอก Username สำเร็จ")

            # กรอก Password
            driver.find_element(By.ID, 'password').send_keys(PASSWORD)
            print("กรอก Password สำเร็จ")

            # คลิกปุ่มล็อกอิน
            driver.find_element(By.TAG_NAME, 'button').click()
            print("ส่งข้อมูลล็อกอินแล้ว")

            # --- เข้าสู่หน้ารายงาน ---
            time.sleep(3) # รอหลังล็อกอินสักครู่
            print(f"กำลังเข้าสู่หน้ารายงาน: {BOSIPLUS_REPORT_URL}")
            driver.get(BOSIPLUS_REPORT_URL)

            # --- ดึงข้อมูลจากตาราง (ใช้การรอแบบชาญฉลาดเช่นกัน) ---
            print("กำลังรอให้ข้อมูลในตารางโหลด...")
            # ให้บอทรอจนกว่า 'แถวแรก' ของข้อมูลในตารางจะปรากฏขึ้นมา
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table-bordered > tbody > tr'))
            )
            print("ข้อมูลโหลดสำเร็จ! เริ่มการดึงข้อมูล...")
            
            table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered > tbody > tr')
            print(f"พบข้อมูลทั้งหมด {len(table_rows)} แถว")

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
            # หากเกิดข้อผิดพลาด ให้พิมพ์ออกมาดู
            print("เกิดข้อผิดพลาดร้ายแรงระหว่างการทำงาน!")
            print(e)
    
    print("บอททำงานเสร็จสิ้น")

if __name__ == '__main__':
    run_bot()
