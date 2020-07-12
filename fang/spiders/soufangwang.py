# -*- coding: utf-8 -*-
import scrapy
from fang.items import FangItem,OFangItem
import re
# from scrapy_redis.dupefilter import RFPDupeFilter
from scrapy_redis.spiders import RedisSpider
class SoufangwangSpider(RedisSpider):
    name = 'soufangwang'
    allowed_domains = ['fang.com']
    # start_urls = ['https://www.fang.com/SoufunFamily.htm']
    redis_key = 'fang:start_urls'

    def parse(self, response):
        # 提取省份信息以及发送省份的url
        province = None
        trs = response.xpath("//div[@id='c02']//tr")
        for tr in trs:
            # 省份信息
            tds = tr.xpath("./td[not(@class)]")
            province_thing = tds[0].xpath(".//text()").get().strip()
            if province_thing:
                province = province_thing
            # 城市url和城市名
            city_links = tds[1].xpath("./a")
            # print('province:',province)
            for city_link in city_links:
                city = city_link.xpath("./text()").get()
                city_url = city_link.xpath("./@href").get() # type:str
                # print(f"city:{city},city_url:{city_url}")
            # break
                if 'bj' not in city_url:
                    new_url = 'newhouse.fang'.join(city_url.split('fang'))+'house/s/'
                    esf_url = 'esfhouse.fang'.join(city_url.split('fang'))+'house/s/'
                # print(new_url)
                else:
                    new_url = 'https://newhouse.fang.com/house/s/'
                    esf_url = 'https://esf.fang.com/'
                # break
                yield response.follow(url=new_url,callback=self.parse_new,meta={'province':province,
                        'city':city
                        })

                yield response.follow(url=esf_url,callback=self.parse_esf,meta={'province':province,
                        'city':city
                        })       
                break
            break
    def parse_new(self,response):
        lis = response.xpath("//div[@class='nhouse_list']/div/ul/li")
        province, city = response.meta['province'],response.meta['city']
        for li in lis:
            name = re.sub(r'\s','',''.join(li.xpath(".//div[contains(@class,'house_value')]//a/text()").getall()))
            # rank_orange = len(li.xpath(".//ul/li[@class='orange-star']").getall())
            # ran_half = len(li.xpath(".//ul/li[@class='half-star']").getall())
            # rank = rank_orange+0.5*ran_half
            rank = 4.5
            # rank这个值需要使用selenium取值，动态加载的数据
            house_info = re.sub(r'\s','',''.join(li.xpath(".//div[contains(@class,'house_type')]//text()").getall()))
            position = li.xpath(".//div[@class='address']/a/@title").get()
            origin_url = response.urljoin(li.xpath(".//div[@class='address']/a/@href").get())
            onsale = li.xpath(".//div[@class='fangyuan']/span/text()").get()
            special = ' '.join(li.xpath(".//div[@class='fangyuan']/a/text()").getall())
            price = re.sub(r'\s','',''.join(li.xpath(".//div[@class='nhouse_price']//text()").getall()))
            # origin_url = li.xpath("")
            item = FangItem(name=name,rank=rank,house_info=house_info,position=position,onsale=onsale,
            special=special,price=price,origin_url=origin_url,city=city,province=province)
            yield item
        next_ = response.xpath("//div[@class='page']//a[@class='next']/@href").get()
        if next_:
            next_url = response.urljoin(next_)
            yield response.follow(url=next_url,callback=self.parse_new,meta={'province':province,
                        'city':city
                        })
    def parse_esf(self,response):
        dls = response.xpath("//div[contains(@class,'shop_list')]//dl[@data-bg]")
        province,city = response.meta['province'],response.meta['city']
        for dl in dls:
            name = re.sub(r'\s','',dl.xpath(".//span[@class='tit_shop']/text()").get())
            house_info = re.sub(r'\s','',''.join(dl.xpath(".//p[@class='tel_shop']//text()").getall()))
            position = dl.xpath(".//p[@class='add_shop']/span/text()").get()
            subway = dl.xpath(".//p[contains(@class,'clearfix')]/span[not(@class='\\')]/text()").get()
            price = re.sub(r'\s','',''.join(dl.xpath(".//dd[@class='price_right']/span[@class='red']//text()").getall()))
            avg_price = dl.xpath(".//dd[@class='price_right']/span[2]//text()").get()
            item = OFangItem(province=province,city=city,name=name,house_info=house_info,position=position,subway=subway,
                            price = price,avg_price=avg_price
                            )
            print(item)
            # yield item
        # pass
        next_ = response.xpath("//div[@class='page_al']/p[1]/@href").get()
        if next_:
            next_url = response.urljoin(next_)
            yield response.follow(url=next_url,callback=self.parse_esf,meta={'province':province,
                        'city':city
                        })
