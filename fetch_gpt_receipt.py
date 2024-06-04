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
from pdfminer.high_level import extract_text
import logging

# Set up logging
logging.basicConfig(filename='script.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


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
    try:
        # Extract text from the PDF file
        text = extract_text(pdf_path)

        # Initialize variables
        invoice_number = None
        date_paid = None

        # Split text into lines for better processing
        lines = text.split('\n')

        # Search for invoice number and date paid patterns
        for i, line in enumerate(lines):
            if "Invoice number" in line:
                # Extract invoice number from the line
                invoice_number = line.split("Invoice number")[-1].strip()
                
                # Replace \x00 by "-"
                invoice_number = invoice_number.replace("\x00", "-")
            elif "Date paid" in line and i + 3 < len(lines):
                # The date paid might be three lines after "Date paid"
                date_str = lines[i + 3].strip()
                try:
                    date_paid = datetime.strptime(date_str, "%b %d, %Y").date().isoformat()
                except ValueError as e:
                    logging.error(f"Failed to parse date: {date_str} - {e}")
                    continue
            if invoice_number and date_paid:
                break

        return invoice_number, date_paid
    
    except Exception as e:
        logging.error(f"Failed to extract invoice details: {e}")
        return None, None

def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Download ChatGPT receipts.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--output_dir", type=str, default="saved_pdfs", help="Directory to save the PDF files")
    parser.add_argument("--filename", type=str, help="Filename for the PDF receipt")
    parser.add_argument("--username", type=str, help="Username for ChatGPT login")
    parser.add_argument("--password", type=str, help="Password for ChatGPT login")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

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
    if args.headless:
        options.add_argument('--headless')
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
        
        # Download PDF receipt
        temp_filename = args.filename or date.today().strftime("%Y%m%d") + " - ChatGPT - Receipt.pdf"
        pdf_path = download_pdf_receipt(driver, output_dir, temp_filename)
        
        # Extract invoice details
        invoice_number, date_paid = extract_invoice_details(pdf_path)
        print(f"Invoice number: {invoice_number}")
        print(f"Date paid: {date_paid}")

        # Rename file if no filename was provided
        if not args.filename and invoice_number and date_paid:
            new_filename = f"{date_paid.replace('-', '')} - {invoice_number} - ChatGPT.pdf"
            new_file_path = os.path.join(output_dir, new_filename)
            os.rename(pdf_path, new_file_path)
            print(f"File renamed to: {new_filename}")
        else:
            print("Unable to extract details from file. File not renamed.")
            print(f"File saved as: {temp_filename}")
            
    except Exception as e:
        logging.error(f"Error in main function: {e}")
        
    finally:
        # Close the WebDriver
        driver.quit()

def test_extract_invoice_details():
    # Test the PDF extraction function
    pdf_path = "2024-06-04_invoice.pdf"
    invoice_number, date_paid = extract_invoice_details(pdf_path)
    print(f"Invoice number: {invoice_number}")
    print(f"Date paid: {date_paid}")

if __name__ == "__main__":
    main()
    #test_extract_invoice_details()
