import argparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests
import time
import json
from dotenv import load_dotenv
import os
from datetime import date, datetime
import pypdf

# Default time to wait for page loads
time_to_wait = 5

def open_chatgpt_homepage(driver):
    driver.get('https://chatgpt.com/')
    time.sleep(time_to_wait)

def click_login_button(driver):
    xpath = "//button[@data-testid='login-button']"
    login_button = driver.find_element(By.XPATH, xpath)
    login_button.click()
    time.sleep(time_to_wait)

def enter_email(driver, email):
    field_id = "email-input"
    email_input = driver.find_element(By.ID, field_id)
    email_input.send_keys(email)
    email_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

def enter_password(driver, password):
    field_id = "password"
    password_input = driver.find_element(By.ID, field_id)
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)
    time.sleep(time_to_wait)

def open_pricing_panel(driver):
    driver.get('https://chatgpt.com/#pricing')
    driver.refresh()  # Refresh to display the subscription management panel
    time.sleep(time_to_wait * 2)

def click_manage_subscription(driver):
    btn_mng_subs = driver.find_element(By.LINK_TEXT, "Manage my subscription")
    btn_mng_subs.click()
    time.sleep(time_to_wait * 2)  # Wait for the subscription management page to load

def download_pdf_receipt(driver, output_dir, filename):
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
    r = requests.get(file_url, allow_redirects=True, cookies={cookie['name']: cookie['value'] for cookie in cookies})

    # Generate a file path
    file_path = os.path.join(output_dir, filename)

    # Save the PDF file in the specified directory
    with open(file_path, 'wb') as f:
        f.write(r.content)

    time.sleep(10)
    
    return file_path

def extract_invoice_details(pdf_path):
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = pypdf.PdfReader(file)
        number_of_pages = len(reader.pages)
        
        # Extract text from each page
        text = ""
        for page in range(number_of_pages):
            text += reader.pages[page].extract_text()
    
    # Initialize variables
    invoice_number = None
    date_paid = None
    
    # Search for invoice number and date paid patterns
    for line in text.split('\n'):
        if "Invoice number" in line:
            invoice_number = line.split("Invoice number")[-1].strip()
        elif "Date paid" in line:
            date_str = line.split("Date paid")[-1].strip()
            date_paid = datetime.strptime(date_str, "%b %d, %Y").date().isoformat()
        if invoice_number and date_paid:
            break

    return invoice_number, date_paid

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Download ChatGPT invoices.")
    parser.add_argument("--output_dir", type=str, default="saved_pdfs", help="Directory to save the PDF files")
    parser.add_argument("--filename", type=str, default=date.today().strftime("%Y%m%d") + "_receipt.pdf", help="Filename for the PDF receipt")
    parser.add_argument("--username", type=str, help="Username for ChatGPT login")
    parser.add_argument("--password", type=str, help="Password for ChatGPT login")
    args = parser.parse_args()
        
    # Load environment variables from .env file
    load_dotenv()
    
    # Get the ChatGPT login credentials from arguments or environment variables
    email = args.username or os.getenv('USER')
    password = args.password or os.getenv('PASS')
    
    # Check if email and password are provided, if not prompt the user to create .env file
    if not email or not password:
        if not os.path.exists('.env'):
            print("Please create a .env file with the following content:")
            print("USER=your_email@example.com")
            print("PASS=your_password")
            with open('.env', 'w') as f:
                f.write("USER=\nPASS=\n")
            print("A .env file has been created. Please fill in your credentials and rerun the script.")
            return
        else:
            email = os.getenv('USER')
            password = os.getenv('PASS')

    # Define the output directory
    output_dir = args.output_dir

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
        download_pdf_receipt(driver, output_dir, args.filename)

    finally:
        # Close the WebDriver
        driver.quit()

if __name__ == "__main__":
    main()
