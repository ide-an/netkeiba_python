import re

import scrapy


# この日付けより後のデータのみ取得する
DATA_MIN = '20220320'
# JSON のキー
KEYS = ['order',
        'frame',
        'number',
        'name',
        'age',
        'weight',
        'jocky',
        'time',
        'difference',
        'time-metric',
        'passed',
        'last-spurt',
        'odds',
        'popularity',
        'horse-weight',
        'train-time',
        'comments',
        'remarks',
        'trainer',
        'owner',
        'prise']


class NetkeibaSpider(scrapy.Spider):
    name = "netkeiba"
    start_urls = [
        'https://regist.netkeiba.com/account/?pid=login',
    ]

    def parse(self, response):
        self.logger.info("parse")
        if hasattr(self, 'user_id') and hasattr(self, 'user_pass') and self.user_id and self.user_pass:
            self.logger.info("Login...")
            return scrapy.FormRequest.from_response(
                response,
                formcss='.member_select_box form',
                formdata={'login_id': self.user_id, 'pswd': self.user_pass},
                callback=self.after_login
            )
        else: # ログイン情報がなければログインせずに収集する。この場合time-metricやremarkが取れない
            self.logger.info("Not Login...")
            return scrapy.Request('http://db.netkeiba.com/?pid=race_top', callback=self.parse_month)

    def after_login(self, response):
        self.logger.info("after_login")
        if not response.css('.Icon_Mypage'):
            self.logger.error("Login failed")
            return
        yield scrapy.Request('http://db.netkeiba.com/?pid=race_top', callback=self.parse_month)

    def parse_month(self, response):
        self.logger.info("parse_month")
        for day in response.css('.race_calendar td a::attr(href)'):
            full_url = response.urljoin(day.extract())

            yield scrapy.Request(full_url, callback=self.parse_race_list)

        next_page = response.css('.race_calendar li.rev a::attr(href)')

        if len(next_page) > 1:
            next_page = next_page[1].extract()
            m = re.search(r"date=([0-9]+)", next_page)

            if not m:
                return

            date = m.group(1)

            if next_page is not None and date > DATA_MIN:
                next_page = response.urljoin(next_page)

                yield scrapy.Request(next_page, callback=self.parse)

    def parse_race_list(self, response):
        for race in response.css('.race_top_data_info > dd > a::attr(href)'):
            full_url = response.urljoin(race.extract())

            yield scrapy.Request(full_url, callback=self.parse_race)

    def parse_race(self, response):
        if len(response.css('.race_table_01 tr')) < 2:
            return

        result = {'title': None,
                  'race_href': None,
                  'horses': [],
                  'diary': None,
                  'smalltxt': None}

        if response.css('title::text'):
            result['title'] = response.css('title::text').extract_first()

        if response.css('.race_num li a.active::attr(href)'):
            result['race_href'] = response.css('.race_num li a.active::attr(href)').extract_first()

        if response.css('diary_snap_cut span::text'):
            result['diary'] = response.css('diary_snap_cut span::text').extract_first()

        if response.css('p.smalltxt::text'):
            result['smalltxt'] = response.css('p.smalltxt::text').extract_first()

        for i, tr in enumerate(response.css('.race_table_01 tr')[1:]):
            result['horses'].append({})

            for h, td in zip(KEYS, tr.css('td')):
                result['horses'][i][h] = None
                if h in ['name', 'jocky', 'trainer', 'owner'] and td.css('a::attr(href)'): # id収集のためhrefを保存
                    result['horses'][i][h + '_href'] = td.css('a::attr(href)').extract_first()

                if td.css('::text'):
                    text = td.css('::text').extract()
                    text = ' '.join([t.strip() for t in text]).lstrip().rstrip()
                    result['horses'][i][h] = text

        yield result

