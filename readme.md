# Fetch latest ChatGPT invoice script

# Instructions easy running

## Prerequisites
- VS Code with extension "Python Virtual Environment Creator" or whatever you like
- Selenium WebDriver for Firefox
- Be sure to add the path to the geckodriver to the PATH environment variable

## Steps
1. Clone this repository
2. Open with VS Code
3. Create a virtual environment
   1. <key>Ctrl</key> + <key>Shift</key> + <key>P</key>
   2. Type "Python: Create New Virtual Environment"
4. Create a `.env` file in the root directory
5. Add the following environment variables to the `.env` file
   ```env
   USER=your_username
   PASS=your_password
   ```
6. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```
7. Run the script
   ```bash
   python main.py
   ```

