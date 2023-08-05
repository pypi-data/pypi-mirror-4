# -*- coding: utf-8 -*-

import httplib2
import lxml.html

base_url = "http://news.chinatimes.com"
news_list_url = "http://news.chinatimes.com/rtnlist/0/0/100/1.html"

h = httplib2.Http(".cache")

def get_realtime_title(encoding="UTF-8"):
    """
    Get ALL Category and Source Realtime news from chinatimes
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(encoding="UTF-8")
    
    *encoding*: html text encoding
    
    return: dict{category, source, time, title, url}
    """
    response, content = h.request(news_list_url)

    html = lxml.html.fromstring(content)
    html.make_links_absolute(base_url)

    # Get news-list section
    div = html.findall("*div")[1]

    # Get all title-info to list
    tr = list(div.iterdescendants("tr"))[1:]

    result_list = []
    for title_info in tr:
        news_url = list(title_info.iterlinks())[0][2]
        info_list = map(lambda x: x.text_content().encode(encoding), list(title_info))
    
        info_dict = {"title": info_list[0].strip("\r\n "), "time": info_list[1],
                     "category": info_list[2], "source": info_list[3],
                     "url": news_url}
    
        result_list.append(info_dict)
        
    return result_list