import requests
from bs4 import BeautifulSoup
import discord
from os import getenv
from dotenv import load_dotenv
# ctftime.org upcoming 대회 정보 파싱
# 1. upcoming 대회 리스트 파싱 -> 하루에 한번씩 파싱하여 중복되는 대회 정보는 제거 후 새로운 대회가 열렸을 때만 다음 단계 수행
#      대회 이름, 대회 날짜, Location이 온라인 일때만
# 2. 대회 페이지 링크 파싱
# 3. 데이터 정리 후 discord에 업로드



load_dotenv(verbose=True)

discord_token= getenv("DISCORD_TOKEN")

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
            text = "대회 이름 : " + i[0] + "\n대회 시간 : " + i[1] + " \n대회 링크 : " + i[2]
            await message.channel.send(text)
            await message.channel.send("----------------------------------------------------------------------------------------")
    else:
        await message.channel.send("저를 사용할 수 있는 채널 또는 유효한 명령어가 아닙니다.")

async def get_upcoming_data():
    ctftime = "https://ctftime.org"
    upcoming_url = ctftime + "/event/list/upcoming"
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    response = requests.get(upcoming_url,headers=headers)
        
    if response.status_code == 200:
        upcoming_html = response.text
        upcoming_soup = BeautifulSoup(upcoming_html, 'html.parser')
        table = upcoming_soup.find('table')
        trs = table.find_all('tr')
        ctf_list = []
        for idx, tr in enumerate(trs):
            if idx > 0:
                    tds = tr.find_all('td')
                    hrefs = tds[0].find('a')["href"]
                    if tds[3].text.strip() == "On-line":
                        event_url = ctftime + hrefs
                        event_reqs = requests.get(event_url,headers=headers)
                        if event_reqs.status_code == 200:
                            event_html = event_reqs.text
                            event_soup = BeautifulSoup(event_html, 'html.parser')
                            div = event_soup.find("div", {'class' : 'span10'})
                            ps = div.find_all("p")
                            
                            links = ps[5].text.strip("Official URL: ")
                            ctf_list.append([tds[0].text.strip(),tds[1].text.strip(), links])
    else : 
        print(response.status_code)
    return ctf_list

client.run(discord_token)

