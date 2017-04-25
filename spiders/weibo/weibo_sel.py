# from selenium import webdriver
# from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.support.wait import WebDriverWait
#
# username = '767543579@qq.com'
# password = 'JOPPER'
# driver = webdriver.Chrome('C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe')
# driver.get('https://passport.weibo.cn/signin/login')
# elem = driver.find_element_by_xpath("//*[@id='loginName']")
# elem.send_keys(username)
# elem = driver.find_element_by_xpath("//*[@id='loginPassword']")
# elem.send_keys(password)
# elem = driver.find_element_by_xpath("//*[@id='loginAction']")
# elem.send_keys(Keys.ENTER)
# cookie2 = driver.get_cookies()
# print(cookie2)