import requests
import lxml.html
import time
import datetime
import sys
import os
import django
sys.path.append("navernow")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "navernow.settings")
django.setup()


class NaverNow:
    BASE_URI = 'https://entertain.naver.com'
    PAGE_URI = BASE_URI + (
        '/now'
        '?sid=%(sid)s'
        '&date=%(date)s'
        '&page=%(page)s'
    )

    def __init__(self):
        self.sid = '7a5'
        self.date = datetime.date.today()
        self.page = 1
        self.max = 500
        self.contents = []
        self.latest_uri = 'NULL'

    def fetch_posts(self):
        try:
            self.fetch_latest_post()
        except IndexError:
            pass
        self.fetch_timeline()
        self.fetch_texts()
        self.contents.reverse()
        self.register_to_db()

    def fetch_latest_post(self):
        from news.models import Post
        obj = Post.objects.all().order_by('-pk')[0:1]
        latest_uri = obj[0].uri
        print(latest_uri)
        self.latest_uri = latest_uri
        print('Connected.')

    def fetch_timeline(self):
        uri = self.PAGE_URI % {
            'sid': self.sid,
            'date': self.date,
            'page': self.page
        }
        res = requests.get(uri)
        html_obj = lxml.html.fromstring(res.text).xpath('//*[@id="newsWrp"]/ul')[0]
        items = html_obj.xpath('.//li')
        if items[0].text == '기사가 없습니다.':
            return
        for item in items:
            tit = item.xpath('.//*[@class="tit"]')[0]
            content = {
                'title': tit.text,
                'uri': tit.attrib['href']
                }
            if content['uri'] == self.latest_uri:
                print('Listed %s Posts' % len(self.contents))
                return
            try:
                content['thumbnail'] = item.xpath('.//img')[0].attrib['src']
            except IndexError:
                content['thumbnail'] = 'NULL'
            self.contents.append(content)
        print('Listed %s Posts' % len(self.contents))
        if len(self.contents) >= self.max:
            return
        time.sleep(0.1)
        self.page += 1
        self.fetch_timeline()

    def fetch_texts(self):
        count = 0
        for item in self.contents:
            count += 1
            uri = self.BASE_URI + item['uri']
            res = requests.get(uri)
            html_obj = lxml.html.fromstring(res.text)
            time_str = html_obj.xpath('//*[@class="article_info"]//em')[0].text
            if (time_str[11:13] == '오전') ^ (time_str[14:-3] == '12'):
                time_str = time_str[:11]+time_str[14:]
            elif time_str[11:13] == '오후':
                time_str = time_str[:11]+str(int(time_str[14:-3])+12)+time_str[-3:]
            elif (time_str[11:13] == '오전') and (time_str[14:-3] == '12'):
                time_str = time_str[:11] + str(int(time_str[14:-3]) - 12) + time_str[-3:]
            item['date'] = datetime.datetime.strptime(time_str, '%Y.%m.%d %H:%M')
#            item['date'] = date.strftime('%Y/%m/%d %H:%M')
            text = lxml.html.tostring(html_obj.xpath('//*[@id="articeBody"]')[0], encoding="utf-8").decode()
            text = text.replace('\n', '')
            item['text'] = text.replace('\t', '')
            print('Fetched %s %s / %s' % (uri, count, len(self.contents)))
            time.sleep(0.1)

    def register_to_db(self):
        from news.models import Post
        print('Connected.')
        for i in self.contents:
            Post.objects.create(title=i['title'], uri=i['uri'], text=i['text'], date=i['date'], thumbnail=i['thumbnail'])
        print('Registered.')


def main():
    navernow = NaverNow()
    navernow.fetch_posts()
#   print(navernow.contents)


if __name__ == '__main__':
    main()
