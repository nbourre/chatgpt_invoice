from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import json

# Function to load cookies from file
def load_cookies_from_file(file_path):
    with open(file_path, 'r') as file:
        cookies = json.load(file)
    return cookies

# Function to save cookies to file
def save_cookies_to_file(driver, file_path):
    with open(file_path, 'w') as file:
        json.dump(driver.get_cookies(), file)

# Initialize the Firefox WebDriver
options = webdriver.FirefoxOptions()
##options.add_argument('--headless')  # Run in headless mode if needed
driver = webdriver.Firefox(options=options)

# Load env variables
from dotenv import load_dotenv
import os
load_dotenv()

# Get the ChatGPT login credentials from environment variables
email = os.getenv('USER')
password = os.getenv('PASS')

try:
    driver.get('https://chatgpt.com/')
    time.sleep(5)  # Time to manually log in

    # Find login button with attribute and value data-testid="login-button"
    login_button = driver.find_element(By.XPATH, "//button[@data-testid='login-button']")
    login_button.click()
    time.sleep(5)

    # Find the email input field and enter your email id=email-input
    email_input = driver.find_element(By.ID, "email-input")
    email_input.send_keys(email)

    email_input.send_keys(Keys.ENTER)
    time.sleep(2)

    # Find the password input field and enter your password id=password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(5)

    # Open the ChatGPT login page
    driver.get('https://chatgpt.com')
    time.sleep(5)  # Wait for the login page to load


    # Load cookies if previously saved
    # cookies = load_cookies_from_file('cookies.json')
    # for cookie in cookies:
    #     driver.add_cookie(cookie)

    # # Refresh the page to apply cookies
    # driver.refresh()
    # time.sleep(5)

    # Reloading the page with the #pricing URL
    driver.get('https://chatgpt.com/#pricing')

    # Le refresh permet d'afficher le panneau de gestion de l'abonnement
    driver.refresh()
    time.sleep(5)

    btn_mng_subs = driver.find_element(By.LINK_TEXT, "Manage my subscription")
    btn_mng_subs.click()

    # Attendre que la page de gestion de l'abonnement soit chargée
    time.sleep(10)

    # Afficher le panneau pour télécharger la facture
    link_pdf = driver.find_element(By.XPATH, "(//a[contains(@href,'acct_')])[1]")
    # driver.execute_script("arguments[0].scrollIntoView(true);", link_pdf)

    href = link_pdf.get_attribute('href')

    # Replace invoice subdomain by invoicedata
    href = href.replace("invoice", "invoicedata")

    # Replace /i/ by /invoice_receipt_file_url/
    href = href.replace("com/i/", "com/invoice_receipt_file_url/")
    
    # Get response body of href from selenium
    driver.get(href)

    json_link = driver.find_element(By.ID, "json").text

    # Parse the json to get the download link
    import json
    data = json.loads(json_link)
    file_url = data['file_url']

    # Extract cookies
    cookies = driver.get_cookies()

    # Python http request get the file
    import requests
    r = requests.get(file_url, allow_redirects=True, cookies=cookies)


    # Generate a filename with date as a prefix
    from datetime import date
    today = date.today()
    filename = today.strftime("%Y-%m-%d") + "_invoice.pdf"

    # Save the file
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    time.sleep(10)



    # # Download receipt button
    # download_receipt = driver.find_element(By.XPATH, "(//button[contains(@data-testid,'download-invoice-receipt-pdf-button')])[1]")
    # download_receipt.click()

    # time.sleep(10)
    # # Navigate to the invoice page (adjust the URL as needed)
    # driver.get('https://chat.openai.com/invoices')
    # time.sleep(5)

    # # Locate the download button and click it (adjust the selector as needed)
    # download_button = driver.find_element(By.CSS_SELECTOR, 'button.download-invoice')
    # download_button.click()
    # time.sleep(10)  # Wait for the download to complete

    # Save cookies to file
    # save_cookies_to_file(driver, 'cookies.json')

finally:
    # Close the WebDriver
    driver.quit()
