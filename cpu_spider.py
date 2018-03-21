import re
import sqlite3

import pandas

import config
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq

opt = webdriver.ChromeOptions()
opt.set_headless()

driver = webdriver.Chrome(options=opt)
wait = WebDriverWait(driver, 10)
driver.set_window_size(1200,700)
def search():
    print('正在搜索...')
    try:
        driver.get('http://www.taobao.com')
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))
        commit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))

        input.send_keys(config.KEUWORD)
        commit.click()
        total_page = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.total')))
        get_info()
        return total_page.text
    except TimeoutException:
        return search()
def next_page(page_num):
    print('搜索到%s页' % page_num)
    try:
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        commit = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()
        input.send_keys(page_num)
        commit.click()
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > ul > li.item.active > span'), str(page_num)))
        get_info()
    except TimeoutException:
        next_page(page_num)
def get_info():
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    html = driver.page_source
    doc = pq(html)
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        cpu_info = {
            'image':item.find('.pic .img').attr('data-src'),
            'price':item.find('.price').text().split('\n')[1],
            'deal':item.find('.deal-cnt').text()[:-3],
            'name':item.find('.title').text(),
            'shop':item.find('.shop').text(),
            'location':item.find('.location').text()
        }
        yield cpu_info
def save_data():
    df = pandas.DataFrame(get_info())
    df.to_excel('cpu.xlsx',header=('image','price','name','deal','shop','location'))

def main():
    total_page = search()
    total_page = int(re.compile('(\d+)').search(total_page).group(1))
    for i in range(2,total_page+1):
        next_page(i)
        save_data()
    driver.close()


if __name__ == '__main__':
    main()



