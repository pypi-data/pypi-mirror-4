#
# libertytimes.py
#
# Copyright 2012 - 2013 Louie Lu <grapherd at gmail.com>
#
#

"""
newstitle libertytimes module
"""

import codecs
import httplib2
import lxml.html

base_url = "http://iservice.libertytimes.com.tw/"
news_list_url = "http://iservice.libertytimes.com.tw/liveNews/list.php?type=%E5%8D%B3%E6%99%82%E6%96%B0%E8%81%9E"

h = httplib2.Http(".cache")

def get_realtime_title(pages=5):
    """
    Get ALL Category Realtime news from libertytimes
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(pages=5, encoding="UTF-8")
    
    *pages*: get page 1 to pages, default is 5 pages
        
    return: dict{time, title, url}
    """
    
    result_list = []
    
    for page in xrange(1, pages + 1):
        response, content = h.request("%s&ipage=%d" % (news_list_url, page))
        html = lxml.html.fromstring(content.decode('utf-8', 'ignore'))
        html.make_links_absolute(base_url)

        # Get news-list section
        div = html.findall("*div")[0]
    
        # Get all title-info to list
        tr = list(div.iterdescendants("tr"))[1:-1]
    
        for title_info in tr:
            news_url = list(title_info.iterlinks())[1][2]
            info_list = map(lambda x: x.text_content(), list(title_info))
        
            try:
                info_dict = {"title": info_list[0].strip("\r\n "), "time": info_list[1],
                            "url": news_url}
            except IndexError, error_infomation:
                pass
    
            result_list.append(info_dict)
        
    return result_list

def save_realtime_title(filename="libretytimes_realtime_title.csv",
                        append=False, pages=5, sep=","):
    """Save libertytimes realtime title to CSV file.

    *kwargs*:
        filename -- csv file name
        append -- append to old file
        pages -- the page get from libertytimes
        sep -- the separated value for csv file
    """
    
    title_info = get_realtime_title(pages = pages)
    
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