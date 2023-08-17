import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

from pypdf import PdfReader
from io import BytesIO

iom_job_portal_url = "https://recruit.iom.int/sap/bc/webdynpro/sap/hrrcf_a_unreg_job_search?sap-client=100&sap-language=EN&sap-wd-configid=ZHRRCF_A_UNREG_JOB_SEARCH#"


def find_pdf_url(job_code: str) -> str:
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    with webdriver.Chrome(options=chrome_options) as driver:
        driver.get(iom_job_portal_url)

        # Setup wait for later
        wait = WebDriverWait(driver, 10)

        # Store the ID of the original window
        original_window = driver.current_window_handle

        # Check we don't have other windows open already
        assert len(driver.window_handles) == 1

        # wait for the page to load
        driver.implicitly_wait(10)

        # Click the link which opens in a new window
        driver.find_element("xpath", f"//*[contains(text(), '{job_code}')]").click()

        # Wait for the new window or tab
        wait.until(EC.number_of_windows_to_be(2))

        # Loop through until we find a new window handle
        for window_handle in driver.window_handles:
            if window_handle != original_window:
                driver.switch_to.window(window_handle)
                break

        # find embedded pdf element by xpath
        embedded_element = driver.find_element("xpath", "//*[@id=\"WD2B\"]")

        # get the src attribute
        pdf_url = embedded_element.get_attribute("src")

        return pdf_url


def extract_text_from_pdf_url(pdf_url: str) -> str:
    response = requests.get(pdf_url)
    my_raw_data = response.content
    text = ""
    with BytesIO(my_raw_data) as data:
        reader = PdfReader(data)

        for page_number in range(len(reader.pages)):
            text += reader.pages[page_number].extract_text()

    return text


def get_iom_job_description(job_code: str) -> str:
    try:
        pdf_url = find_pdf_url(job_code)
    except:
        # Could not find pdf for job code
        return None

    content = extract_text_from_pdf_url(pdf_url)

    return content





