import re
from typing import Optional
from seleniumwire import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import pandas as pd
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from datetime import datetime


USERNAME = ''
PASSWORD = ''
ENDPOINT = ''

def clean_up(trash,year):
    trash = trash.split()
    nums = trash[1]
    day = nums[:2]
    date = trash[0]+' '+str(day)+' '+str(year)
    nums = nums[2:]
    sp = nums[:6]
    rest = (nums[6:])
    if rest.__contains__('.'):
        p = rest.index(".")
        beg = str(rest[:p])
        end = str(rest[p:])
        if len(beg) == 2:
            sp = str(sp)+beg[0]
            imx = beg[1]+end
        elif len(beg) == 1:
            imx = imx = beg[0]+end
    else:
        if len(rest) == 2:
            imx = rest[1]
            sp = str(sp) + str(rest[0])
        elif len(rest) == 1:
            imx = rest[0]

    treasure = [date,sp,float(imx)]
    return (treasure)

def proxy(user: str, password: str, endpoint: str) -> dict:
    wire_options = {"proxy": {"http": f"http://{user}:{password}@{endpoint}","https": f"https://{user}:{password}@{endpoint}"}}
    return wire_options

def scrape():
    options = webdriver.ChromeOptions()
    proxies = proxy(USERNAME,PASSWORD,ENDPOINT)
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options, seleniumwire_options=proxies)

    try:
        driver.get('https://imx.tdameritrade.com/#myChart')
        wait=WebDriverWait(driver,20)
        wait.until(EC.element_to_be_clickable((By.ID,"li-Table View"))).click()
        wait.until(EC.element_to_be_clickable((By.CLASS_NAME,"chart-link"))).click()
        soup = bs(driver.page_source, 'html.parser')
        sts = []
        monthc = 12
        yearc = 2023

        for i in soup.select('div[class*="row-info row-container row-allow-hover"]'):
            sts.append(clean_up(i.get_text(),yearc))
            monthc = monthc + 1
            if monthc > 12:
                monthc = 1
                yearc = yearc - 1 
        for i in soup.select('div[class*="row-info row-container null"]'):
            if i.get_text().__contains__('-'):
                pass
            else:
                sts.append(clean_up(i.get_text(),yearc))
                monthc = monthc + 1
                if monthc > 12:
                    monthc = 1
                    yearc = yearc - 1
        return sts

    finally:
        driver.quit()

def frame():
    df = pd.DataFrame(scrape())
    df = df.rename(columns={0:'date',1:'s&p',2:'imx'})
    format = '%B %d %Y'
    df['date'] = [datetime.strptime(x, format) for x in df['date']]
    df = df.sort_values(by='date')
    plt.plot(df['date'],df['imx'])
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%b\n%Y'))
    plt.ylabel('Investor Movement Index')
    plt.show()

if __name__ == '__main__':
    frame()