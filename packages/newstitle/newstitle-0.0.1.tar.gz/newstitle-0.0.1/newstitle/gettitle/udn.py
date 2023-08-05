# -*- coding: utf-8 -*-

import httplib2
import lxml.html

base_url = "http://udn.com/"
news_list_url = "http://udn.com/NEWS/SITEMAP_TITLE/SitemapTitle_breakingnews.shtml"

h = httplib2.Http(".cache")

def get_realtime_title(encoding="UTF-8"):
    """
    Get ALL Category Realtime news from udn news
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(encoding="UTF-8")
    
    *encoding*: html text encoding
    
    return: dict{category, time, title, url}
    """
    
    response, content = h.request(news_list_url)
    
    html = lxml.html.fromstring(content)
    html.make_links_absolute(base_url)

    # Get news-list section
    table = html.findall("*table")[0]
    
    # Get all title-info to list
    tr = list(table.iterdescendants("tr"))[13: -3]
    
    result_list = []
    for title_info in tr:
        news_url = list(title_info.iterlinks())
        if not news_url or "gif" in news_url[0][2]:
            continue
        
        news_url = news_url[0][2]
        info_list = map(lambda x: x.text_content().encode(encoding), list(title_info))
        
        try:
            info_dict = {"title": info_list[1].strip("\r\n "), "time": info_list[0],
                        "category": info_list[2], "url": news_url}
        except IndexError, error_infomation:
            pass
    
        result_list.append(info_dict)
        
    return result_list
