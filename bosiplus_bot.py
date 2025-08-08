import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# --- ดึงข้อมูลสำคัญจาก Environment Variables เพื่อความปลอดภัย ---
# เราจะไปตั้งค่าตัวแปรเหล่านี้บนเซิร์ฟเวอร์ Render ในบทที่ 4
USERNAME = os.environ.get('BOSIPLUS_USER')
PASSWORD = os.environ.get('BOSIPLUS_PASS')
WEBHOOK_URL = os.environ.get('WEBHOOK_URL')

# --- URL เป้าหมาย ---
BOSIPLUS_LOGIN_URL = 'https://topup.manage-one.com/th/login'
BOSIPLUS_REPORT_URL = 'https://topup.manage-one.com/th/finance/twd-list'

def run_bot():
    print("เริ่มต้นการทำงานของบอท...")

    # --- ตั้งค่า Chrome ให้ทำงานแบบไม่แสดงหน้าจอ (Headless) ---
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")

    # ใช้ 'with' เพื่อให้แน่ใจว่าเบราว์เซอร์จะถูกปิดเสมอ
    with webdriver.Chrome(options=chrome_options) as driver:
        driver.implicitly_wait(10) # รอองค์ประกอบสูงสุด 10 วินาที

        # --- ขั้นตอนล็อกอิน ---
        print(f"กำลังเข้าสู่หน้าล็อกอิน: {BOSIPLUS_LOGIN_URL}")
        driver.get(BOSIPLUS_LOGIN_URL)

        # สังเกต: ID ของช่องกรอกคือ 'username' และ 'password'
        driver.find_element(By.ID, 'username').send_keys(USERNAME)
        driver.find_element(By.ID, 'password').send_keys(PASSWORD)
        driver.find_element(By.TAG_NAME, 'button').click()
        print("ส่งข้อมูลล็อกอินแล้ว")

        # --- เข้าสู่หน้ารายงาน ---
        time.sleep(3) # รอสักครู่หลังล็อกอิน
        print(f"กำลังเข้าสู่หน้ารายงาน: {BOSIPLUS_REPORT_URL}")
        driver.get(BOSIPLUS_REPORT_URL)

        # --- ดึงข้อมูลจากตาราง ---
        print("กำลังค้นหาตารางข้อมูล...")
        # สังเกต: เราเลือกตารางด้วย class 'table-bordered' และหาทุกแถวใน 'tbody'
        table_rows = driver.find_elements(By.CSS_SELECTOR, 'table.table-bordered > tbody > tr')
        print(f"พบข้อมูลทั้งหมด {len(table_rows)} แถว")

        for row in table_rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) > 8: # ตรวจสอบว่าแถวนั้นมีคอลัมน์ครบ
                status = cells[8].text.strip()
                if "สำเร็จ" in status:
                    # สร้าง Dictionary (payload) ที่มีข้อมูล
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