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

def save_realtime_title(filename="udn_realtime_title", append=False,
                        encoding='UTF-8'):
    """
    Save realtime title to text file.
    the order is: title | time | url
    
    *filename*: the file you save, default is udn_realtime_title
    
    *append*: allow you just append new title to old file, if the file doesnt'
              exist, it will create a new one.
              
    *encoding*: html text encoding
    
    return: append=False: 1 = done;
            append=True: 0 = no change to title,
                         1 = append title finish (or a new one).
    """
    
    title_info = get_realtime_title(encoding)
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
                      (info['title'], info['time'], info['url']))
        
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

def save_realtime_title_csv(filename="udn_realtime_title.csv", append=False,
                            encoding="UTF-8"):
    
    title_info = get_realtime_title(encoding = encoding)
    
    if append:
        pass
    else:
        fo = open(filename, "w")
        fo.write('"title", "time", "url"\n')
        for info in title_info:
            fo.write('"%s", "%s", "%s"\n' %
                     (info['title'], info['time'], info['url']))
        
        fo.close()