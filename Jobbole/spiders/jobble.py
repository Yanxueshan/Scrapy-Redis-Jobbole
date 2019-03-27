'''
    本模块为Scrapy入口文件，具体编写解析向URL发起请求后获取到的源码
'''

import re
import datetime
from urllib import parse
from scrapy.http import Request
from Jobbole.items import JobboleArticleItem
from Jobbole.libs.common import get_md5
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from settings import BASE_DIR
import pickle
from scrapy_redis.spiders import RedisSpider


class JobbleSpider(RedisSpider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    redis_key = "jobbole:start_urls"
    # start_urls = ['http://blog.jobbole.com/all-posts/']

    # scrapy默认处理 >=200 并且 <300的URL，其他的会过滤掉，handle_httpstatus_list表示对返回这些状态码的URL不过滤，自己处理
    handle_httpstatus_list = [302, 403, 404]

    def __init__(self):
        # crawl_url_count: 用来统计爬取URL的总数
        self.crawl_url_count = 0

        # 信号处理，当爬虫退出时执行spider_closed方法
        dispatcher.connect(self.spider_closed, signals.spider_closed)

        # 信号处理，当引擎从downloader中获取到一个新的Response对象时调用get_crawl_url_count方法
        dispatcher.connect(self.get_crawl_url_count, signals.response_received)

        # 数据收集，收集Scrapy运行过程中302/403/404页面URL及URL数量
        # failed_url: 用来存放302/403/404页面URL
        self.failed_url = []

        super().__init__()

    def spider_closed(self, spider):
        '''
            收集爬取失败（302/403/404）的URL，并写入json文件中
        '''
        self.crawler.stats.set_value("failed_urls", ','.join(self.failed_url))
        pickle.dump(self.failed_url, open(BASE_DIR+"/failed_url/failed_url.json", 'wb'))

    def get_crawl_url_count(self, spider):
        '''
            当引擎engine从downloader中获取到一个新的Response对象时调用，crawl_url_count+=1
        '''
        self.crawl_url_count += 1
        print("截止目前，爬取URL总数为：", self.crawl_url_count)
        return self.crawl_url_count

    def parse(self, response):
        '''
            1. 解析出下一页的URL，并且解析出所有的文章URL
        '''
        if response.status in [302, 403, 404]:
            self.failed_url.append(response.url)
            # 数据收集，当Response状态码为302/403/404时，failed_url数加1
            self.crawler.stats.inc_value("failed_url")

        url_tags = response.css('#archive .floated-thumb .post-thumb a')
        for url_tag in url_tags:
            url = url_tag.css('::attr(href)').extract_first('')
            yield Request(url=parse.urljoin(response.url, url), callback=self.parse_detail)

        next_page_url = response.css('.navigation .next.page-numbers::attr(href)').extract_first('')
        if next_page_url:
            yield Request(url=parse.urljoin(response.url, next_page_url), callback=self.parse)

    def parse_detail(self, response):
        '''
            编写网页源代码具体的解析逻辑，解析出我们想要的数据
        '''
        jobbole_article_item = JobboleArticleItem()

        title = response.css('.grid-8 .entry-header h1::text').extract_first('')
        content = response.css('.grid-8 .entry').extract_first('')
        
        support_nums = response.css('.post-adds .vote-post-up h10::text').extract_first('')
        if support_nums:
            support_nums = int(support_nums)
        else:
            support_nums = 0

        collection_nums = response.css('.bookmark-btn::text').extract_first('')
        re_match = re.findall('\d+', collection_nums)
        if re_match:
            collection_nums = int(re_match[0])
        else:
            collection_nums = 0

        comment_nums = response.css('a[href="#article-comment"] span::text').extract_first('')
        re_match = re.findall('\d+', comment_nums)
        if re_match:
            comment_nums = int(re_match[0])
        else:
            comment_nums = 0

        publish_date = response.css('.entry-meta-hide-on-mobile::text').extract_first('').strip().replace('·', '').replace(' ', '')
        publish_date = datetime.datetime.strptime(publish_date, '%Y/%m/%d').date()

        tags = response.css('.entry-meta-hide-on-mobile a::text').extract()
        for tag in tags:
            if '评论' in tag:
                tags.remove(tag)
        tags = '/'.join(tags)

        jobbole_article_item['title'] = title
        jobbole_article_item['url'] = response.url
        jobbole_article_item['url_id'] = get_md5(response.url)
        jobbole_article_item['content'] = content
        jobbole_article_item['support_nums'] = support_nums
        jobbole_article_item['collection_nums'] = collection_nums
        jobbole_article_item['comment_nums'] = comment_nums
        jobbole_article_item['publish_date'] = publish_date
        jobbole_article_item['tags'] = tags

        yield jobbole_article_item
