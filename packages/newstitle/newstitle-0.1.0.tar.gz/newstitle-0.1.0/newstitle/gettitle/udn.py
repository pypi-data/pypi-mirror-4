#
# udn.py
#
# Copyright 2012 - 2013 Louie Lu <grapherd at gmail.com>
#
#

"""
newstitle udn module
"""

import codecs
import httplib2
import lxml.html

base_url = "http://udn.com/"
news_list_url = "http://udn.com/NEWS/SITEMAP_TITLE/SitemapTitle_breakingnews.shtml"

h = httplib2.Http(".cache")

def get_realtime_title():
    """
    Get ALL Category Realtime news from udn news
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(encoding="UTF-8")
        
    return: dict{category, time, title, url}
    """
    
    response, content = h.request(news_list_url)
    
    html = lxml.html.fromstring(content.decode('big5', 'ignore'))
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
        info_list = map(lambda x: x.text_content(), list(title_info))
        
        try:
            info_dict = {"title": info_list[1].strip("\r\n "), "time": info_list[0],
                        "category": info_list[2], "url": news_url}
        except IndexError, error_infomation:
            pass
    
        result_list.append(info_dict)
        
    return result_list

def save_realtime_title(filename="udn_realtime_title.csv",
                            append=False, sep=","):
    """Save udn realtime title to CSV file.

    *kwargs*:
        filename -- csv file name
        append -- append to old file
        sep -- the separated value for csv file
    """
    
    title_info = get_realtime_title()
    
    if append:
        pass
    else:
        fo = codecs.open(filename, "w", "utf-8")
        fo.write('"title", "time", "url"\n')
        for info in title_info:
            fo.write('"%s"%s "%s"%s "%s"\n' %
                     (info['title'], sep, info['time'], sep, info['url']))
        
        fo.close()

if __name__ == '__main__':
    pass