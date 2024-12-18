from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GooglePage:
    def __init__(self, driver):
        self.driver = driver
        self.search_box = (By.NAME, "q")
        self.search_button = (By.NAME, "btnK")
        
    def search(self, query):
        # Wait for search box to be visible and enter query
        search_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(self.search_box)
        )
        search_input.clear()
        search_input.send_keys(query)
        
        # Wait for and click search button
        # Note: We need to wait for button to be clickable
        button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(self.search_button)
        )
        button.click()

def test_google_search(driver):
    driver.get("https://www.google.com")
    google_page = GooglePage(driver)
    google_page.search("Python Selenium")
    
    # Wait for title to change after search
    WebDriverWait(driver, 10).until(
        lambda x: "Python Selenium" in x.title
    )
    
    # Assert the search term is in the page title
    assert "Python Selenium" in driver.title, f"Expected 'Python Selenium' in title, but got '{driver.title}'"
