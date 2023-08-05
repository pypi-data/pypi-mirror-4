# -*- coding: utf-8 -*-

import httplib2
import lxml.html

base_url = "http://iservice.libertytimes.com.tw/"
news_list_url = "http://iservice.libertytimes.com.tw/liveNews/list.php?type=%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E"

h = httplib2.Http(".cache")

def get_realtime_title(pages=5, encoding="UTF-8"):
    """
    Get ALL Category Realtime news from libertytimes
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(pages=5, encoding="UTF-8")
    
    *pages*: get page 1 to pages, default is 5 pages
    
    *encoding*: html text encoding
    
    return: dict{time, title, url}
    """
    
    result_list = []
    
    for page in xrange(1, pages + 1):
        response, content = h.request("%s&ipage=%d" % (news_list_url, page))
        html = lxml.html.fromstring(content)
        html.make_links_absolute(base_url)

        # Get news-list section
        div = html.findall("*div")[0]
    
        # Get all title-info to list
        tr = list(div.iterdescendants("tr"))[1:-1]
    
        for title_info in tr:
            news_url = list(title_info.iterlinks())[1][2]
            info_list = map(lambda x: x.text_content().encode(encoding), list(title_info))
        
            try:
                info_dict = {"title": info_list[0].strip("\r\n "), "time": info_list[1],
                            "url": news_url}
            except IndexError, error_infomation:
                pass
    
            result_list.append(info_dict)
        
    return result_list
