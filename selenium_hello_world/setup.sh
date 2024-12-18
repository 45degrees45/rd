#!/bin/bash

# Create directories
mkdir -p config pages tests

# Create all __init__.py files
touch config/__init__.py pages/__init__.py tests/__init__.py

# Create config.py
cat > config/config.py << 'EOL'
class TestConfig:
    BASE_URL = "https://www.google.com"
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 20
EOL

# Create base_page.py
cat > pages/base_page.py << 'EOL'
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)

    def find_element(self, by, value):
        return self.wait.until(EC.presence_of_element_located((by, value)))
EOL

# Create google_page.py
cat > pages/google_page.py << 'EOL'
from selenium.webdriver.common.by import By
from .base_page import BasePage

class GooglePage(BasePage):
    SEARCH_BOX = (By.NAME, "q")
    
    def search(self, text):
        search_box = self.find_element(*self.SEARCH_BOX)
        search_box.send_keys(text)
EOL

# Create conftest.py
cat > tests/conftest.py << 'EOL'
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

@pytest.fixture
def driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()
EOL

# Create test_google_search.py
cat > tests/test_google_search.py << 'EOL'
import pytest
from pages.google_page import GooglePage

def test_google_search(driver):
    driver.get("https://www.google.com")
    google_page = GooglePage(driver)
    google_page.search("Python Selenium")
    assert "Python Selenium" in driver.title
EOL

# Make the script executable
chmod +x setup.sh
