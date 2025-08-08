import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- ดึงข้อมูลลับจาก Environment Variables ที่เราจะตั้งค่าบน Render ---
# ไม่ต้องแก้ไขส่วนนี้
USERNAME = os.environ.get('BOSIPLUS_USER')
PASSWORD = os.environ.get('BOSIPLUS_PASS')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# --- URL เป้าหมาย (อัปเดตเป็นเวอร์ชันล่าสุดตามที่คุณให้มา) ---
BOSIPLUS_LOGIN_URL = 'https://bsplus.manage-ione.com/th/auth/login'
BOSIPLUS_REPORT_URL = 'https://bsplus.manage-ione.com/th/finance/withdrawal/list'

def run_bot():
    print("เริ่มต้นการทำงานของบอท...")
    
    # --- ตั้งค่า Chrome ให้ทำงานแบบไม่แสดงหน้าจอ (Headless) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    
    # ใช้ 'with' เพื่อให้แน่ใจว่าเบราว์เซอร์จะถูกปิดเสมอเมื่อทำงานเสร็จ
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.implicitly_wait(10) # ตั้งค่าให้รอองค์ประกอบต่างๆ สูงสุด 10 วินาที

        # --- ขั้นตอนล็อกอิน ---
        print(f"กำลังเข้าสู่หน้าล็อกอิน: {BOSIPLUS_LOGIN_URL}")
        driver.get(BOSIPLUS_LOGIN_URL)
        
        # ‼️ สำคัญ: ให้คุณหา ID ที่ถูกต้องจากหน้าเว็บ แล้วนำมาใส่แทนที่ตรงนี้ ‼️
        # วิธีหา: ไปที่หน้าเว็บ > คลิกขวาที่ช่อง Username/Password > Inspect > แล้วหา id="xxx"
        driver.find_element(By.ID, 'ID_ของช่อง_USERNAME').send_keys(USERNAME)
        driver.find_element(By.ID, 'ID_ของช่อง_PASSWORD').send_keys(PASSWORD)
        
        # หากปุ่มล็อกอินไม่มี ID อาจจะต้องหาด้วยวิธีอื่น เช่น Class Name หรือ XPath
        driver.find_element(By.TAG_NAME, 'button').click()
        print("ส่งข้อมูลล็อกอินแล้ว")

        # --- เข้าสู่หน้ารายงาน ---
        time.sleep(5) # รอ 5 วินาทีเพื่อให้แน่ใจว่าล็อกอินและเปลี่ยนหน้าสำเร็จ
        print(f"กำลังเข้าสู่หน้ารายงาน: {BOSIPLUS_REPORT_URL}")
        driver.get(BOSIPLUS_REPORT_URL)

        # --- ดึงข้อมูลจากตาราง ---
        print("กำลังค้นหาตารางข้อมูล...")
        table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered > tbody > tr')
        print(f"พบข้อมูลทั้งหมด {len(table_rows)} แถว")

        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 8: 
                status = cells[8].text.strip()
                if "สำเร็จ" in status:
                    # สร้างข้อมูลที่จะส่ง (Payload)
                    payload = {
                        'refId': cells[1].text.strip(),
                        'user': cells[2].text.strip(),
                        'time': cells[3].text.strip(),
                        'amount': cells[6].text.strip(),
                        'status': status
                    }
                    
                    # --- ส่งข้อมูลไปที่ Webhook ของ Google Apps Script ---
                    print(f"ส่งข้อมูลรายการสำเร็จ: {payload['refId']}")
                    try:
                        requests.post(WEBHOOK_URL, json=payload)
                    except Exception as e:
                        print(f"  -> เกิดข้อผิดพลาดในการส่ง: {e}")
    
    print("บอททำงานเสร็จสิ้น")

# สั่งให้บอททำงานเมื่อรันไฟล์นี้
if __name__ == '__main__':
    run_bot()
