from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_hello_world():
    # Setup Chrome driver with automatic webdriver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        # Navigate to Google
        driver.get("https://www.google.com")
        print("Hello, World! Successfully opened Google!")
        
        # Find search box and type "Hello World"
        search_box = driver.find_element(By.NAME, "q")
        search_box.send_keys("Hello World")
        
        # Small pause to see the results
        time.sleep(2)
        
        print("Successfully typed 'Hello World' in Google search!")
        
    finally:
        # Clean up
        driver.quit()

if __name__ == "__main__":
    test_hello_world()
