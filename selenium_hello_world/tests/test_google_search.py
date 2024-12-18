import pytest
from pages.google_page import GooglePage

def test_google_search(driver):
    driver.get("https://www.google.com")
    google_page = GooglePage(driver)
    google_page.search("Python Selenium")
    assert "Python Selenium" in driver.title
