# -*- coding: utf-8 -*-

import httplib2
import lxml.html

base_url = "http://www.appledaily.com.tw/"
news_list_url = "http://www.appledaily.com.tw/realtimenews"

h = httplib2.Http(".cache")

def get_realtime_title(pages=5, encoding="UTF-8"):
    """
    Get ALL Category Realtime news from appledaily
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(pages=5, encoding="UTF-8")
    
    *pages*: get page 1 to pages, default is 5 pages
    
    *encoding*: html text encoding
    
    return: dict{time, title, url}
    
    """
    
    result_list = []
    
    for page in xrange(1, pages + 1):
        response, content = h.request("%s/index/type/apple/page/%d" % (news_list_url, page))
        html = lxml.html.fromstring(content)
        html.make_links_absolute(base_url)

        # Get news-list section
        div = html.findall("*div")[0]
        
        # Get all title-info to list
        li = list(div.iterdescendants("li"))[10:-29]
    
        for title_info in li:
            news_url = list(title_info.iterlinks())[0][2]
            info_list = map(lambda x: x.text_content().encode(encoding), list(title_info))
            info_list = info_list[0].strip("\r\n ").replace("\n", "")
            
            time = info_list[:5]
            category = info_list[5:11]
            title = info_list[11:].strip("\r\n ")
            title = title[: title.rfind("(") - 1]
                        
            try:
                info_dict = {"title": title, "time": time,
                            "category": category, "url": news_url}
            except IndexError, error_infomation:
                pass
    
            result_list.append(info_dict)

    return result_list