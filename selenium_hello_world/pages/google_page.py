from selenium.webdriver.common.by import By
from .base_page import BasePage

class GooglePage(BasePage):
    SEARCH_BOX = (By.NAME, "q")
    
    def search(self, text):
        search_box = self.find_element(*self.SEARCH_BOX)
        search_box.send_keys(text)
