'''
    本模块为Scrapy入口文件，具体编写解析向URL发起请求后获取到的源码
'''

import re
import datetime
from urllib import parse
import scrapy
from scrapy.http import Request
from Jobbole.items import JobboleArticleItem
from Jobbole.libs.common import get_md5


class JobbleSpider(scrapy.Spider):
    '''
        pass
    '''
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        '''
            1. 解析出下一页的URL，并且解析出所有的文章URL
        '''
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
