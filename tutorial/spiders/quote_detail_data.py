# -*- coding:utf-8 -*-
import scrapy
import os
import sys
import re
import json


class Quotes(scrapy.Spider):
    name = "getData"

    list = []
    base_path = "E:\\CODE\\python\\workspace\\ScrapyTest\\tutorial\\"
    data_json_filename = "data.json"

    def write_to_detail(self, text):
        urls = []
        file_path_name = self.base_path + "haveRead.txt"
        print("开始写入读取的url...")
        if os.path.isfile(file_path_name):
            try:
                with open(file_path_name, "a+") as f:
                    f.write(text + "\n")
            except Exception as e:
                print(e)
                print("写入", file_path_name, "出错")
                sys.exit()

        else:
            with open(file_path_name, "a+") as f:
                f.write(text + "\n")

        print("写入成功")

    def read_from_detail(self):
        urls = []
        file_path_name = self.base_path + "haveRead.txt"
        print("开始读取已爬取url...")
        if os.path.isfile(file_path_name):
            try:
                with open(file_path_name) as f:
                    for line in f:
                        urls.append(line.strip('\n'))
            except Exception as e:
                print(e)
                print("读取已爬取文件出错，程序中止")
                sys.exit()

            print("读取成功...")
            return urls
        else:
            file = open(file_path_name, "w")
            file.close()
            return

    def read_urls(self):
        urls = []
        file_path_name = self.base_path + "url.txt"
        print("开始读取url...")
        try:
            with open(file_path_name) as f:
                for line in f:
                    urls.append(line.strip('\n'))
        except Exception as e:
            print(e)
            print("读取url出错，程序中止")
            sys.exit()

        print("读取成功...")
        return urls

    def start_requests(self):
        urls = self.read_urls()
        urls_read = self.read_from_detail()

        url = urls[0]
        if url not in urls_read:
            with open(self.data_json_filename, 'w', encoding="utf8") as file:
                file.write('[')
        urls = urls[0:100000]
        for url in urls:
            if url not in urls_read:
                print("开始爬取", url, "..")
                yield scrapy.Request(url)

    def parse(self, response):
        website_url = response.url
        job_title = response.css("h1.l::text").get()
        salary = response.css("div.info-money strong::text").get().split('元')[0].split('-')

        max_salary = int(salary[1])
        min_salary = int(salary[0])

        info = response.xpath("//*[@class='info-three l']/span").getall()
        experience_year = re.match('<span>(.*?)</span>', info[1]).group(1)

        education_needed = re.match('<span>(.*?)</span>', info[2]).group(1)
        number_of_people = re.match('<span>招(.*?)人</span>', info[3]).group(1)
        number_of_people = int(number_of_people)

        province = ""
        city = re.match('<span><a.*?>(.*?)</a>(.*?)</span>', info[0]).group(1)
        district = re.match('<span><a.*?>(.*?)</a>(.*?)</span>', info[0]).group(2).strip('-')

        position_info = response.xpath("//*/div[@class='pos-ul']/p/span/text()").getall()
        result = ""
        for position in position_info:
            result += position
        position_info = result

        job_advantage_tags = response.css('script:contains("JobWelfareTab")::text').get().split('\n')
        job_advantage_tag = job_advantage_tags[len(job_advantage_tags) - 3].strip(" ").strip("\r")
        job_advantage_tags = re.match("var.*?'(.*?)';", job_advantage_tag).group(1)
        job_advantage_tag = job_advantage_tags.split(",")

        functional_category = response.css("span.pos-name a::text").get().split("/")

        company_href = response.css("div.promulgator-info h3 a::attr(href)").get().split('/')
        company_htm = company_href[len(company_href) - 1].split('.')
        company_ht = company_htm[0].split('_')
        company_id = company_ht[len(company_ht) - 1]
        company_id = "ZL_" + company_id

        company_name = response.css("div.promulgator-info h3 a::text").get()

        company_info = response.css("ul.promulgator-ul li")
        company_type = company_info.css("strong::text").getall()[0]
        company_scale = company_info.css("strong::text").getall()[1]
        company_industry = company_info.css("strong a::text").get()

        dict = {
            "website_url": website_url,
            "job_title": job_title,
            "max_salary": max_salary,
            "min_salary": min_salary,
            "experience_year": experience_year,
            "education_needed": education_needed,
            "publish_date": "2019-03-06",
            "number_of_people": number_of_people,
            "province": province,
            "city": city,
            "district": district,
            "position_info": position_info,
            "job_advantage_tag": job_advantage_tag,
            "functional_category": functional_category,
            "key_words": [
                ""
            ],
            "compay": {
                "company_id": company_id,
                "company_name": company_name,
                "company_type": company_type,
                "company_scale": company_scale,
                "company_industry": company_industry
            },
        }
        with open(self.data_json_filename, 'a+', encoding="utf8") as file:
            json.dump(dict, file, ensure_ascii=False)  # data转换为json数据格式并写入文件
            file.write(",")

        self.write_to_detail(website_url)
        print(website_url, "爬取完成")
        # print(json.dumps(dict, ensure_ascii=False))
