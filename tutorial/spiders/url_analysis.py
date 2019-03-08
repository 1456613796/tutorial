# -*- coding:utf-8 -*-


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