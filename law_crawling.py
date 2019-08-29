#2019.07.20-KimSeokMin
#필요 라이브러리 : selenium, bs4(beautifulsoup)
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup as BS
from multiprocessing.pool import Pool, ThreadPool
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
#from selenium.common.exceptions import TimeoutException
import threading
import re
import csv

casenum = 1
def getCaseNum(html):
    global casenum
    bs = BS(html, "lxml")
    csnum = bs.find_all("a",{"class":"layer_pop_open"})
    arr = []
    for i in csnum:
        cs = i.get('id')
        cs = cs.replace("py_","")
        arr += [[casenum,int(cs)]]
        print(casenum, cs)
        casenum+=1
    return arr

def getCase(case):
    f = open("case.csv", mode = "a", encoding = 'utf-8', newline = '')
    wr = csv.writer(f)
    driver = get_driver()
    link = url2+str(case[1])
    driver.get(link)
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME, 'page')))
    time.sleep(2.5)
    html = driver.page_source
    bs = BS(html, 'lxml')
    prescripts = bs.find("div",{"class":"page"})
    if prescripts == None:
        return
    else:
        scripts = prescripts.find_all("p")
    result = ''
    for script in scripts:
        strong_elements = script.find_all("strong")
        for strong in strong_elements:
            strong.extract()
    for script in scripts:
        result += script.get_text()
    wr.writerow([case[0], case[1], result])
    print(case[0])
    f.close()
    

threadLocal = threading.local()

def get_driver():
    driver = getattr(threadLocal, 'driver', None)
    if driver is None:
        options = webdriver.ChromeOptions()
        prefs = {'profile.default_content_setting_values': {'cookies': 2, 'images': 2, 'javascript': 2, 
                                    'plugins': 2, 'popups': 2, 'geolocation': 2, 
                                    'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2, 
                                    'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 
                                    'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 
                                    'ppapi_broker': 2, 'automatic_downloads': 2, 'midi_sysex': 2, 
                                    'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2, 
                                    'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 
                                    'durable_storage': 2}}
        options.add_argument('headless')
        options.add_experimental_option('prefs', prefs)
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('window-size=1920x1080')
        options.add_argument("disable-gpu")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
        driver = webdriver.Chrome(path, chrome_options=options)
        setattr(threadLocal, 'driver', driver)
    return driver


path = "D:\chromedriver\chromedriver"
url = "https://glaw.scourt.go.kr/wsjo/panre/sjo050.do"
url2 = "https://glaw.scourt.go.kr/wsjo/panre/sjo100.do?contId="

checknum = 1
def CaseNum():
    global checknum
    #1.대법원 사이트 접속
    case = list()
    driver = get_driver()
    driver.get(url)
    time.sleep(2)
    search_box = driver.find_element_by_name("srchw")
    search_box.send_keys("손해배상")
    driver.find_element_by_xpath('//*[@id="search"]/div[2]/fieldset/a[1]').click()
    driver.find_element_by_xpath('//*[@id="search"]/div[2]/fieldset/div/p/a').click()
    
    #2. 판례 번호 크롤링 
    for i in range(10):
        if i==0:
            html = driver.page_source
            case += getCaseNum(html)
            time.sleep(0.3)
            driver.find_element_by_xpath('//*[@id="tabwrap"]/div/div/div[1]/div[3]/div/fieldset/p/a[1]').click()
            checknum +=1
        elif(i>=1 and i<=9):
            html = driver.page_source
            case += getCaseNum(html)
            time.sleep(0.3)
            driver.find_element_by_xpath('//*[@id="tabwrap"]/div/div/div[1]/div[3]/div/fieldset/p/a[2]').click()
            checknum +=1
        elif(i>=10 and i<622):
            html = driver.page_source
            case += getCaseNum(html)
            time.sleep(0.5)
            button = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.XPATH,'//*[@id="tabwrap"]/div/div/div[1]/div[3]/div/fieldset/p/a[3]')))
            button.click()
            checknum += 1
        if i==622:
            html = driver.page_source
            case += getCaseNum(html)
            time.sleep(0.3)
            driver.find_element_by_xpath('//*[@id="tabwrap"]/div/div/div[1]/div[3]/div/fieldset/p/a[3]').click()
            html = driver.page_source
            case += getCaseNum(html)
            time.sleep(0.3)

    f = open("casenum.csv", mode="w", encoding = 'utf-8', newline = '')
    wr = csv.writer(f)
    for cs in case:
        wr.writerow([cs[0], cs[1]])
    f.close()

#1.먼저 casenum.csv 생성
CaseNum()#이건 처음 한번만 하고 지우기
print(checknum)

f = open('casenum.csv', mode='r', encoding='utf-8')
rd = csv.reader(f)
arr = list(rd)#casenum 리스트
f.close()
case = arr[:1000] #arr[0] 부터 arr[999]까지 자르기 알아서 원하는 개수만큼 잘라써라

#2. case.csv 생성 *중요 : 처음 실행시에 mode = 'w'이고, 다음부턴 mode = 'a'
f2 = open("case.csv", mode = "w", encoding = 'utf-8', newline = '')
wr2 = csv.writer(f2)
wr2.writerow(['caseindex','casenum', 'script'])
f2.close()


ThreadPool(6).map(getCase, case)
driver.quit()
