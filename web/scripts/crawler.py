from bs4 import BeautifulSoup
import requests
import telegram
from hotdeal.models import Deal
from datetime import datetime, timedelta

response = requests.get(
    "https://www.ppomppu.co.kr/zboard/zboard.php?id=ppomppu")

soup = BeautifulSoup(response.text, "html.parser")
BOT_TOKEN = "5713889241:AAEn0uELsEoPsCbln1WgrtjhK-tRjJP2Wow"

bot = telegram.Bot(token=BOT_TOKEN)


def run():

    # delete deals older than 3days
    row, _ = Deal.objects.filter(created_at__lte=datetime.now() -
                                 timedelta(days=3)).delete()

    print(row, "deals deleted")
    items = soup.find_all("tr", {'class': ["list1", "list0"]})

    for item in items:

        try:
            image = item.find("img", class_="thumb_border").get("src")[2:]
            image = "http://" + image
            title = item.find("font", class_="list_title").text
            title = title.strip()
            link = item.find("font", class_="list_title").parent.get("href")
            # 링크에 따라 /zboard가 있는게 있음
            link = link.replace("/zboard/", "")
            # 링크에 hotdeal 이 있으면
            if link.find("/hotdeal/") != -1:
                link = "https://www.ppomppu.co.kr" + link
            else:
                link = "https://www.ppomppu.co.kr/zboard/" + link

            reply_count = item.find("span", class_="list_comment2").text
            reply_count = int(reply_count)
            up_count = item.find_all("td")[-2].text
            up_count = up_count.split("-")[0]
            up_count = int(up_count)

            if up_count >= 5:
                if (Deal.objects.filter(link__iexact=link).count() == 0):
                    Deal(image_url=image, title=title, link=link,
                         reply_count=reply_count, up_count=up_count).save()
                # print(image, title, link, reply_count, up_count)
                    bot.sendMessage(-1001822872431,
                                    '{} {}'.format(title, link))
        except Exception as e:
            continue
