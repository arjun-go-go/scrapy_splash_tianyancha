# -*- coding: utf-8 -*-
# author: arjun
# @Time: 18-3-8 下午5:01


import csv
import scrapy
import time
from scrapy_splash import SplashRequest
from copy import deepcopy
import re
from scrapy.selector import Selector
from ..items import TianYanItem

class TianyanSplashSpider(scrapy.Spider):
    name = 'tianyan_splash'
    allowed_domains = ['tianyancha.com']
    start_urls = ['http://tianyancha.com/']


    #登录使用的lua脚本
    lua_script = """
              function main(splash,args)
                local ok, reason = splash:go(args.url)
                user_name = args.user_name
                user_passwd = args.user_passwd
                user_text = splash:select(".modulein.modulein1.mobile_box.pl30.pr30.f14.collapse.in .pb30.position-rel input")
                pass_text = splash:select(".modulein.modulein1.mobile_box.pl30.pr30.f14.collapse.in .pb40.position-rel input")
                login_btn = splash:select(".modulein.modulein1.mobile_box.pl30.pr30.f14.collapse.in .c-white.b-c9.pt8.f18.text-center.login_btn")
                if (user_text and pass_text and login_btn) then
                    user_text:send_text(user_name)
                    pass_text:send_text(user_passwd)
                    login_btn:mouse_click({})
                end

              splash:wait(math.random(5, 10))
                return {
                    url = splash:url(),
                    content = splash:html(),
                    cookies = splash:get_cookies(),
                    headers = splash.args.headers,
                  }
                 end

          """

    # 设置代理使用lua脚本，splash不能记录登录的状态。获取cookie
    lua_sc = """
            function main(splash, args)
                splash:init_cookies(splash.args.cookie)
                 splash:on_request(function(request)
                    request:set_proxy{
                        host = 'xxxxxxx',  #代理ip
                        port = xxx,        #代理端口
                        type = "https"     #https可能支持不了，http可以的
                      }
                     end)
                local ok, reason = splash:go(args.url)
                 splash:wait(5)
                return {
                content = splash:html(),
                cookie = splash:get_cookies(),
                 }
            end

        """

    def start_requests(self):
        url = "https://www.tianyancha.com/login"
        yield SplashRequest(url,
                            endpoint="execute",
                            args={
                                "wait":15,
                                "lua_source":self.lua_script,
                                "user_name":"xxxxxx",  #天眼查登录账户，由于获取的数据需要多层请求，我用的vip
                                "user_passwd":"xxxxxx" #天眼查登录密码
                            },
                            meta={"user_name":"xxxxxx"}, #天眼查登录账户
                            callback=self.parse
                            )


    #这里是通过读取csv获取已有的公司名称，通过搜索查寻，可以根据需求定制
    def parse(self, response):
        self.login_user = response.meta["user_name"]
        self.cookie = response.data["cookies"]
        company_list = csv.reader(open('example.csv', 'r'))
        for i in company_list:
            i = i[0]
            urls = "https://www.tianyancha.com/" + "search?key={0}".format(i)
            yield SplashRequest(urls,
                                callback=self.parse_company,
                                meta={"i": i},
                                endpoint="execute",
                                args={
                                    "wait": 20,
                                    "lua_source": self.lua_sc,
                                    "cookie": self.cookie,
                                }
                                )
    #对公司历史名称做处理
    def parse_company(self, response):
        content = response.data["content"]
        res = Selector(text=content)
        i = response.meta["i"]
        divs = res.xpath("//div[@class='result-list']/div")
        list = []
        for div in divs:
            temp = {}
            temp["company_url"] = div.xpath(".//div[@class='header']/a/@href").extract_first()
            titles = div.xpath(".//div[@class='match text-ellipsis']/span/text()").extract_first()
            if titles is not None and "历史名称" in titles:
                temp["old_name"] = div.xpath(".//div[@class='match text-ellipsis']/span[2]/em/text()").extract_first()
            else:
                temp["old_name"] = ""
            names = div.xpath(".//div[@class='header']/a//text()").extract()
            if len(names) > 0:
                temp["company_name"] = "".join(names)
            list.append(temp)
        for li in list:
            if li["company_name"] == i or li["old_name"] == i:
                company_url = li["company_url"]
                yield SplashRequest(company_url
                                    ,callback=self.company_detail
                                    ,meta={"i": i}
                                    ,endpoint="execute"
                                    ,args={
                                        "wait": 20,
                                        "lua_source": self.lua_sc,
                                        "cookie": self.cookie,
                                    }
                                    )

    #公司详情信息获取,所需信息自己提取信息
    def company_detail(self, response):
        content = response.data["content"]
        res = Selector(text=content)
        item = {}
        # item = TianYanItem()
        item["company"] = res.xpath(
            "//div[@class='content']/div[@class='header']/h1/text()").extract_first()

        pass
