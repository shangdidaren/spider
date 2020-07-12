# 爬虫练习

#### 爬取fang.com网站的新房和二手房信息

1. 在https://www.fang.com/SoufunFamily.htm列表页面可以查找所有的地区的房源信息，例如https://hf.fang.com/，

构建成新房和二手房的URL，例如https://hf.newhouse.fang.com/house/s/，https://hf.esf.fang.com/。

`在parse函数中处理上述信息，并在parse_new函数和parse_esf函数中处理新房和二手房信息，请求下一页，继续通过此方法处理请求`

2. 构建新房和二手房的Item模型，在parse_new和parse_esf函数中返回，得到的对象会到pipeline进行处理和存储。
3. 在中间件中更换随机请求头来防止反爬虫，也可以通过更换ip代理的方式，个别通过js加载的数据可以通过selenium返回的响应来处理。验证码可以使用第三方平台识别。

#### 改为分布式爬虫

1. 安装scrapy_redis组件

   `pip install scrapy_redis`

2. 将项目中Spider类改为scapy_redis.spiders.RedisSpider，

3. 将start_urls注释掉，并加上redis_key字段，`redis_key =  fang:start_urls`

4. 在settings中添加相关配置

```python
SCHEDULER = "scrapy_redis.scheduler.Scheduler"
# 链接去重
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"
# 将数据保存到redis中
ITEM_PIPELINES = {
	'scrapy_redis.pipelines.RedisPipeline':300,
	
}
# 在redis保持队列不被清空，可以暂停和恢复
SCHEDULER_PERSIST = True

# 设置redis的信息
Redis独一台服务器，或者是做集群保证高可用
REDIS_HOST = 'redis服务ip'
REDIS_PORT = 6379
```

5. 将此项目放到爬虫服务器上，`pip freeze > require.txt`在爬虫服务器上安装相关依赖`pip install -r require.txt`
6. 运行scrapy runspider soufanwang.py，爬虫服务开始工作，等待开始指令。
7. 在redis服务器上`lpush fang:start_urls  https://www.fang.com/SoufunFamily.htm`，开始爬虫，redis中已经有值。