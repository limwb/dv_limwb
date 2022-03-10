import folium
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# 변수 저장 배열 선언
name_list = []
status_list = []
address_list = []
lng_list = []
lat_list = []

def crawling():
    #크롬 드라이버
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.set_window_size(640, 320)

    #크롤링할 사이트
    driver.get('https://*****.com/login/')

    # 로그인
    driver.find_element_by_xpath('//*[@id="id"]').send_keys('*****')
    driver.find_element_by_xpath('//*[@id="password"]').send_keys('*****')
    sleep(1)
    driver.find_element_by_xpath('//*[@id="btn_login"]').click()
    driver.find_element_by_xpath('/html/body/div/div[1]/div[3]/div[2]').click()

    # 샘플 10개 크롤링
    for i in range(1, 10):
        name = driver.find_element_by_xpath('//*[@id="table_id"]/tbody/tr[' + str(i) + ']/td[2]').text
        name_list.append(name)
        status = driver.find_element_by_xpath('//*[@id="table_id"]/tbody/tr[' + str(i) + ']/td[5]').text

        #folium.Icon에서 지원하지 않는 색상이라면 보라색으로 처리
        if status == 'green' or status == 'yellow' or status == 'red' :
            status_list.append(status)
        else :
            status_list.append('purple')

        driver.find_element_by_xpath('//*[@id="table_id"]/tbody/tr[' + str(i) + ']/td[9]/button[1]').click()  # 정보수정 클릭
        #변경된 화면으로 전환
        driver.switch_to.window(driver.window_handles[-1])
        address = driver.find_element_by_xpath('//*[@id="address"]').get_attribute('value')
        address_list.append(address)
        #본 화면으로 전환
        driver.switch_to.window(driver.window_handles[0])
        driver.find_element_by_xpath('/html/body/div[2]/div[1]/button/span[1]').click()

    # 구글맵을 통해 경도, 위도 구하기
    driver.get('https://www.google.com/maps')

    for address in address_list:
        driver.find_element_by_xpath('//*[@id="searchboxinput"]').send_keys(address)
        driver.find_element_by_xpath('//*[@id="searchbox-searchbutton"]').click()
        sleep(3)
        url_parse = str(driver.current_url)
        #@부터 끝까지 가져옴
        info = url_parse[url_parse.find('@') + 1:]
        #문자열 파싱 후 첫번째(위도)와 두번째(경도)만 저장
        lng_list.append(info.split(',')[0])
        lat_list.append(info.split(',')[1])
        #검색 부분 초기화 작업
        driver.find_element_by_xpath('//*[@id="searchboxinput"]').clear()

    for name, status, address, lng, lat in zip(name_list, status_list, address_list, lng_list, lat_list):
        print(name, '\t', status, '\t', address, '\t', lng, '\t', lat, '\t')


#지도의 첫 위치좌표
latitude = 36.3000324
longitude = 127.5661478

crawling()

#지도 기본 설정
m = folium.Map(location=[latitude, longitude],
               zoom_start=17,
               width=1500,
               height=1000
              )

#지도에 마크찍기
for i in range(len(lng_list)):
    if float(lng_list[i]) > 0 and float(lng_list[i]) > 0:
        print(lng_list[i], lat_list[i])
        x = float(lng_list[i])
        y = float(lat_list[i])

        folium.Marker(
            location=[x, y],
            popup=str(name_list[i]),
            icon=folium.Icon(color=status_list[i], icon='star')
        ).add_to(m)
    else:
        continue

#지도 저장
m.save('map.html')
