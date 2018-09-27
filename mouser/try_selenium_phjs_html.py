from selenium import webdriver
import time

driver = webdriver.Chrome(executable_path='F:/chromedriver/chromedriver.exe')
driver.get('https://products.avnet.com/shop/en/ema/rf-and-microwave/vcos')


"""driver.maximize_window()

t = driver.find_elements_by_xpath("//div[@id='partsShwMoreBtn']")

if u'SHOW MORE RESULTS' in t.text:  # 判断标题中是否有途牛，如果有则点击
    print('yes')  # 判断结果
    t.click()  # 点击这个a链接
"""
data = driver.page_source
print (data)
print(len(data))
driver.quit()


