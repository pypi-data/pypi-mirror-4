"""
This is the code for testing newstitle
It have two function:
    1. Time the grabing time
    2. Generate all the support realtime news under this folder

now including chinatimes, udn, libertytimes, appledaily
"""

import httplib2
import lxml.html
from newstitle import chinatimes
from newstitle import udn
from newstitle import libertytimes
from newstitle import appledaily
import newstitle
import timeit

# Timer for each news
#t = timeit.Timer("chinatimes.get_realtime_title()", "from newstitle import chinatime")
#t = timeit.Timer("udn.get_realtime_title()", "from newstitle import udn")
#t = timeit.Timer("libertytimes.get_realtime_title(pages=5)", "from newstitle import libertytimes")
#t = timeit.Timer("appledaily.get_realtime_title(pages=5)", "from newstitle import appledaily")
#print t.timeit(number=10)

# RealTime news title test
newspaper = newstitle.support_news
for publisher in newspaper:
    fi = open("%s_realtime_title" % (publisher), "w")
    title = eval("%s.get_realtime_title()" % (publisher))
    for info in title:
        fi.write("%s | %s | %s\n" % (info['title'], info['time'], info['url'].encode('utf-8')))
    
    fi.close()
    
print "END OF TEST!"