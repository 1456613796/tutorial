# tutorial
================
爬取网站https://jobs.zhaopin.com/招聘数据

## 代码文件结构
------------------
> + tutorial
> 	+ tutorial
> 		+ spiders
> 			+ quote_detail_data.py &nbsp;&nbsp;&nbsp;*//用于爬取页面数据*
> 			+ quotes_spider.py &nbsp;&nbsp;&nbsp;*//测试使用的demo*
> 			+ url_analysis.py &nbsp;&nbsp;&nbsp;*//分析url*
> 			+ zhaopin_geturls.py &nbsp;&nbsp;&nbsp;*//获取全部的url*
> 		+ items.py
> 		+ middlewares.py
> 		+ pipelines.py
> 		+ setting.py
> 	+ data.json &nbsp;&nbsp;&nbsp;*//结果存储的文件，json格式的数据*
> 	+ haveRead.json &nbsp;&nbsp;&nbsp;*//已经读取的网页的url*
> 	+ result.json &nbsp;&nbsp;&nbsp;*//爬取的url*
> 	+ url.txt &nbsp;&nbsp;&nbsp;*//经过分析的有用的url*

### 整体流程：
* 1、使用 *zhaopin_geturls.py* 从网页中进行数据爬取
* 2、使用 *url_analysis.py* 对爬取的数据进行分析，判断重复的数据，删除重复的url
* 3、使用 *quote_detail_data.py* 进行数据爬取

## 文件内容
------------------------
### zhaopin_geturls.py
```python
import scrapy

class QuotesTalent(scrapy.Spider):
    name = "talent"

    def start_requests(self):
        url = "https://jobs.zhaopin.com/"
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        content_lists = response.css('div.main div[class="content clearfix"] .rightTab .content-list')
        for li in content_lists:
            urls = li.css('.listcon a::attr(href)').getall()
            for url in urls:
                yield response.follow(url, self.parse_detail_job)

    def parse_detail_job(self, response):

        is_page = response.css("div.returnpage h1::text").get() is None

        if is_page:
            urls = response.css(
                '.search_list div[class="details_container bg_container "] span.post a::attr(href)').getall()
            next_url = response.css('span.search_page_next a::attr(href)').get()
            yield response.follow(next_url, self.parse_detail_job)
            yield {
                "url": urls
            }
 ```

> 在命令行输入：*scrapy crawl talent*

### url_analysis.py
```python
import json
import os
import re


def verify_repeat():
    urls = []

    # 按行读取url
    with open(base_dir + "\\urls.txt", "r") as f:
        for line in f:
            urls.append(line.strip('\n'))

    list = []
    for url in urls:
        if url not in list:
            list.append(url)

    print(len(urls))
    print(len(list))
    pass


def analysis():
    '''
    分析爬取的所有的链接中重复的链接
    :return:
    '''
    file_path = base_dir + "\\result.json"
    with open(file_path, encoding="utf8") as file:
        all_urls = json.load(file)

    url_result_list = []

    for url_list in all_urls:
        urls = url_list["url"]
        for url in urls:
            result = re.match("(http://jobs.*?.htm)", url)
            if result is not None:
                url_result_list.append(result.group())

    print(len(url_result_list))
    result_list = []
    with open(base_dir + "\\url.txt", "a+") as f:
        for url in url_result_list:
            if url not in result_list:
                result_list.append(url)

                f.write(url + "\n")

                print(url, "写入")
            else:
                print("重复，未写入")

    print("成功写入", len(result_list), "条数据")


if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.getcwd()))
    analysis()
    # verify_repeat()
```

> 直接执行main函数即可

### quote_detail_data.py

```python
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

```

> 在当前的路径下的cmd中输入：*'scrapy crawl getData'*就可以得到最后的结果

