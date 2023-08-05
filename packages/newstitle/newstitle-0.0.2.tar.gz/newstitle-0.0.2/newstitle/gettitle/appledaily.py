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

def save_realtime_title(filename="appledaily_realtime_title", append=False,
                        pages=5, encoding='UTF-8'):
    """
    Save realtime title to text file.
    the order is: title | time | url
    
    *filename*: the file you save, default is appledaily_realtime_title
    
    *append*: allow you just append new title to old file, if the file doesnt'
              exist, it will create a new one.
    
    *pages*: get page 1 to pages, default is 5 pages
              
    *encoding*: html text encoding
    
    return: append=False: 1 = done;
            append=True: 0 = no change to title,
                         1 = append title finish (or a new one).
    """
    
    title_info = get_realtime_title(pages=pages, encoding=encoding)
    if append:
        try:
            fi = open(filename, "r")
            fi = list(open(filename, "r").readlines())
            if fi == []:
                raise IOError
        except IOError, error_message:
            f = open(filename, "w")
            f.close()
            fi = [""]
        
        if title_info[0]['title'] in fi[0]:
            return 0
        
        append_list = []
        for info in title_info:
            if info['title'] in fi[0]:
                break
            
            #print info['title']
            
            append_list.append("%s | %s | %s\n" %
                      (info['title'], info['time'], info['url'].encode(encoding)))
        
        fo = open(filename, "w")
        for info in append_list:
            fo.write(info)
        for info in fi:
            fo.write(info)
        fo.close()        
    else:
        fo = open(filename, "w")
        for info in title_info:
            fo.write("%s | %s | %s\n" %
                     (info['title'], info['time'], info['url']))
        
        fo.close()
        
    return 1