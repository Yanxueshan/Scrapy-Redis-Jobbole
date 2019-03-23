# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class JobbolePipeline(object):
    '''
        示例Pipeline
    '''
    def process_item(self, item, spider):
        '''
            示例处理item
        '''
        return item


class MySQLPipeline(object):
    '''
        将获取到的数据保存到数据库Mysql中
    '''
    def __init__(self, connect):
        '''
            Pipeline的构造函数，获取Mysql的连接
        '''
        self.connect = connect
        self.cursur = self.connect.cursor()

    @classmethod
    def from_settings(cls, settings):
        '''
            读取settings配置文件中Mysql相关内容，并建立连接
        '''
        connect = pymysql.connect(host=settings['MYSQL_HOST'], db=settings['MYSQL_DBNAME'], user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWORD'], charset='utf8')

        return cls(connect)

    def process_item(self, item, spider):
        '''
            Mysql插入语句的具体执行逻辑
        '''
        insert_sql = 'insert into article(title, url, url_id, content, support_nums, collection_nums, comment_nums, publish_date, tags) values(%s, %s, %s, %s, %s, %s, %s, %s, %s)'

        self.cursur.execute(insert_sql, (item['title'], item['url'], item['url_id'], item['content'], item['support_nums'], item['collection_nums'], item['comment_nums'], item['publish_date'], item['tags']))
        self.connect.commit()
