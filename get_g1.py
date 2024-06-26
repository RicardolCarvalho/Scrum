from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep

notices = []

def initialize_chrome_browser(options=None):
    options = options or webdriver.ChromeOptions()
    options.add_argument('--profile-directory=Default')
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-login-animations")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-popup-blocking")
    driver = webdriver.Chrome(
        options=options) 
    return driver

def get_g1_news():
    driver = initialize_chrome_browser()
    driver.maximize_window()
    driver.get('https://g1.globo.com/')
    sleep(1)
    wait = WebDriverWait(driver, 10)
    elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.feed-post-link')))
    for element in elements:
        link = element.get_attribute('href')
        notices.append(link)

    noticias = []

    for notice in notices:
        driver.get(notice)
        sleep(1)
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'h1.content-head__title')))
        title_text = title.text
        content = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.mc-article-body > article:nth-child(1)')))
        content_text = content.text
        date_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.content-publication-data__updated')))
        date_text = date_element.text [:10]

        noticias.append({
            'titulo': title_text,
            'conteudo': content_text,
            'data': date_text,
        })

        driver.back()
        sleep(1)

    driver.quit()

    return noticias
