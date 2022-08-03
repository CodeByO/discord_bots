import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import discord
from os import getenv
from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
# ctftime.org upcoming 대회 정보 파싱
# 1. upcoming 대회 리스트 파싱 -> 하루에 한번씩 파싱하여 중복되는 대회 정보는 제거 후 새로운 대회가 열렸을 때만 다음 단계 수행
#      대회 이름, 대회 날짜, Location이 온라인 일때만
# 2. 대회 페이지 링크 파싱
# 3. 데이터 정리 후 discord에 업로드



load_dotenv(verbose=True)

discord_token= getenv("DISCORD_TOKEN")
chrome_driver_path = getenv("CHROME_DRIVER_PATH")

def set_chrome_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('disable-gpu')
    options.add_argument('window-size=900x1080')
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36")
    options.add_argument("lang=ko_KR")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

driver = set_chrome_driver()

# discord Client 객체 생성

client = discord.Client()

#event decorator를 설정하고 on_ready function을 할당

@client.event
async def on_ready():
    print('We have logged in as {}'.format(client))
    print('Bot name: {}'.format(client.user.name))  # 여기서 client.user는 discord bot을 의미합니다. (제가 아닙니다.)
    print('Bot ID: {}'.format(client.user.id))  # 여기서 client.user는 discord bot을 의미합니다.
# event decorator를 설정하고 on_message function을 할당해줍니다.
@client.event
async def on_message(message):
    if message.author == client.user:
        return 
    elif message.channel.name == "대회-모음" and message.content.startswith('신규'):
        ctf_list = await get_upcoming_data()
        for i in ctf_list:
            text = "대회 이름 : " + i[1] + "\n대회 시간 : " + i[2] + " \n대회 링크 : " + i[0]
            await message.channel.send(text)
            await message.channel.send("------------------------------------------------------")
    else:
        await message.channel.send("저를 사용할 수 있는 채널 또는 유효한 명령어가 아닙니다.")

def get_upcoming_data():
    URL = 'https://ctftime.org/event/list/upcoming'
    driver.get(URL)
    element_text = []
    ctf_table = driver.find_elements("tag name",'td')
    for element in ctf_table:
        element_text.append(element.text)
        

    list_len = 7

    tmp_list = [element_text[i * list_len:(i + 1) * list_len] for i in range((len(element_text) + list_len - 1) // list_len )] 
    ctf_list = []
    for i in tmp_list:
        tmp = driver.find_element("link text",i[0])
        i.insert(0,tmp.get_attribute("href"))
        
    for i in tmp_list:
        driver.get(i[0])
        official_url = driver.find_element("partial link text","http")
        del i[0]
        i.insert(0,official_url.text)
        if i[4] == 'On-line':
            ctf_list.append([i[0],i[1],i[2]])
    return ctf_list

    
client.run(discord_token)
