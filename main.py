from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import time
import json
from dotenv import load_dotenv
import os
from datetime import date

# Default time to wait for page loads
time_to_wait = 5

def open_chatgpt_homepage(driver):
    driver.get('https://chatgpt.com/')
    time.sleep(time_to_wait)

# Find and click the login button
def click_login_button(driver):
    xpath = "//button[@data-testid='login-button']"
    login_button = driver.find_element(By.XPATH, xpath)
    login_button.click()
    time.sleep(time_to_wait)

# Find the email input field and enter your email
def enter_email(driver, email):
    field_id = "email-input"
    email_input = driver.find_element(By.ID, field_id)
    email_input.send_keys(email)
    email_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

# Find the password input field and enter your password
def enter_password(driver, password):
    field_id = "password"
    password_input = driver.find_element(By.ID, field_id)
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

# Open pricing panel
def open_pricing_panel(driver):
    driver.get('https://chatgpt.com/#pricing')
    driver.refresh()  # Refresh to display the subscription management panel
    time.sleep(time_to_wait * 2)

# Find and click the "Manage my subscription" button
def click_manage_subscription(driver):
    btn_mng_subs = driver.find_element(By.LINK_TEXT, "Manage my subscription")
    btn_mng_subs.click()
    time.sleep(time_to_wait * 2)  # Wait for the subscription management page to load


# Find the link to the PDF invoice
def download_pdf_receipt(driver, output_dir):    
    xpath = "(//a[contains(@href,'acct_')])[1]"
    link_pdf = driver.find_element(By.XPATH, xpath)

    # Get the href attribute which contains the link to the invoice
    href = link_pdf.get_attribute('href')

    # Modify the href to point to the JSON data URL
    href = href.replace("invoice", "invoicedata")
    href = href.replace("com/i/", "com/invoice_receipt_file_url/")

    # Navigate to the modified href to get the JSON data
    driver.get(href)

    # Extract the JSON data from the page
    json_link = driver.find_element(By.ID, "json").text
    data = json.loads(json_link)
    file_url = data['file_url']

    # Extract cookies from the driver
    cookies = driver.get_cookies()

    # Download the PDF file using requests with the extracted cookies
    # Old method: r = requests.get(file_url, allow_redirects=True, cookies=cookies)
    r = requests.get(file_url, allow_redirects=True, cookies={cookie['name']: cookie['value'] for cookie in cookies})

    # Generate a filename with the current date as a prefix
    today = date.today()
    filename = today.strftime("%Y-%m-%d") + "_receipt.pdf"
    file_path = os.path.join(output_dir, filename)

    # Save the PDF file in the specified directory
    with open(file_path, 'wb') as f:
        f.write(r.content)

    time.sleep(10)
    
def main():
    # Load environment variables from .env file
    load_dotenv()

    # Get the ChatGPT login credentials from environment variables
    email = os.getenv('USER')
    password = os.getenv('PASS')
    
    # Define the output directory
    output_dir = "saved_pdfs"

    # Create the output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Initialize the Firefox WebDriver
    options = webdriver.FirefoxOptions()
    # options.add_argument('--headless')  # Uncomment to run in headless mode
    driver = webdriver.Firefox(options=options)

    try:
        open_chatgpt_homepage(driver)
        click_login_button(driver)    
        enter_email(driver, email)    
        enter_password(driver, password)

        # Open the ChatGPT home page again
        open_chatgpt_homepage(driver)
        open_pricing_panel(driver)
        click_manage_subscription(driver)
        download_pdf_receipt(driver, output_dir)

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()