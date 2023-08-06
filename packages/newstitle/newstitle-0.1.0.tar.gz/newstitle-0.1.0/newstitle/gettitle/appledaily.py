#
# appledaily.py
#
# Copyright 2012 - 2013 Louie Lu <grapherd at gmail.com>
#
#

"""
newstitle appledaily module
"""

import codecs
import httplib2
import lxml.html

base_url = "http://www.appledaily.com.tw/"
news_list_url = "http://www.appledaily.com.tw/realtimenews"

h = httplib2.Http(".cache")

def get_realtime_title(pages=5):
    """
    Get ALL Category Realtime news from appledaily
    realtime url may change or invaild when it is not **realtime**
    
    get_realtime_title(pages=5)
    
    *pages*: get page 1 to pages, default is 5 pages
        
    return: dict{time, title, url}
    
    """
    
    result_list = []
    
    for page in xrange(1, pages + 1):
        response, content = h.request("%s/index/type/apple/page/%d" % (news_list_url, page))
        html = lxml.html.fromstring(content.decode('utf-8', 'ignore'))
        html.make_links_absolute(base_url)

        # Get news-list section
        div = html.findall("*div")[0]
        
        # Get all title-info to list
        li = list(div.iterdescendants("li"))[10:-29]
    
        for title_info in li:
            news_url = list(title_info.iterlinks())[0][2]
            info_list = [i.strip() for i in title_info.text_content().strip().split("\n")]

            time = info_list[0][: 5]
            category = info_list[0][5: ]
            title = info_list[1]
            title = title[: title.rfind("(") - 1]
            
            try:
                info_dict = {"title": title, "time": time,
                            "category": category, "url": news_url}
            except IndexError, error_infomation:
                pass
    
            result_list.append(info_dict)

    return result_list

def save_realtime_title(filename="appledaily_realtime_title.csv",
                        append=False, pages=5, sep=","):
    """Save appledaily realtime title to CSV file.

    *kwargs*:
        filename -- csv file name
        append -- append to old file
        pages -- the page get from appledaily
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