from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import time
import json
from dotenv import load_dotenv
import os
from datetime import date

# Initialize the Firefox WebDriver
options = webdriver.FirefoxOptions()
##options.add_argument('--headless')  # Run in headless mode if needed
driver = webdriver.Firefox(options=options)

load_dotenv()

# Get the ChatGPT login credentials from environment variables
email = os.getenv('USER')
password = os.getenv('PASS')
time_to_wait = 5

try:
    driver.get('https://chatgpt.com/')
    time.sleep(time_to_wait)

    # Find login button with attribute and value data-testid="login-button"
    login_button = driver.find_element(By.XPATH, "//button[@data-testid='login-button']")
    login_button.click()
    time.sleep(time_to_wait)

    # Find the email input field and enter your email id=email-input
    email_input = driver.find_element(By.ID, "email-input")
    email_input.send_keys(email)

    email_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

    # Find the password input field and enter your password id=password
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

    # Open the ChatGPT login page
    driver.get('https://chatgpt.com')
    time.sleep(time_to_wait)  # Wait for the login page to load

    # Reloading the page with the #pricing URL
    driver.get('https://chatgpt.com/#pricing')

    # Le refresh permet d'afficher le panneau de gestion de l'abonnement
    driver.refresh()
    time.sleep(time_to_wait)

    btn_mng_subs = driver.find_element(By.LINK_TEXT, "Manage my subscription")
    btn_mng_subs.click()

    # Wait for the subscription management page to load
    # It takes a bit longer
    time.sleep(time_to_wait * 2)

    # Display the panel to download the invoice
    link_pdf = driver.find_element(By.XPATH, "(//a[contains(@href,'acct_')])[1]")

    # The href attribute contains the link to the invoice
    href = link_pdf.get_attribute('href')

    # Replace invoice subdomain by invoicedata
    href = href.replace("invoice", "invoicedata")

    # Replace /i/ by /invoice_receipt_file_url/
    href = href.replace("com/i/", "com/invoice_receipt_file_url/")
    
    # Get response body of href from selenium
    driver.get(href)

    # On Firefox, json files are beautifully displayed, we need to
    # get the text of the json element
    json_link = driver.find_element(By.ID, "json").text

    # Parse the json to get the download link
    data = json.loads(json_link)
    file_url = data['file_url']

    # Extract cookies
    cookies = driver.get_cookies()

    # Get the file using requests and cookies
    r = requests.get(file_url, allow_redirects=True, cookies=cookies)

    # Generate a filename with date as a prefix    
    today = date.today()
    filename = today.strftime("%Y-%m-%d") + "_receipt.pdf"

    # Save the file
    with open(filename, 'wb') as f:
        f.write(r.content)
    
    time.sleep(10)

finally:
    # Close the WebDriver
    driver.quit()
