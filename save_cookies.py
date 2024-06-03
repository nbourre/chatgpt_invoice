from selenium import webdriver
from selenium.webdriver.common.by import By
import time
import json

def save_cookies_to_file(driver, file_path):
    with open(file_path, 'w') as file:
        json.dump(driver.get_cookies(), file)

driver = webdriver.Firefox()
driver.get('https://chat.openai.com/auth/login')
time.sleep(60)  # Time to manually log in

# Save cookies after login
save_cookies_to_file(driver, 'cookies.json')

driver.quit()
