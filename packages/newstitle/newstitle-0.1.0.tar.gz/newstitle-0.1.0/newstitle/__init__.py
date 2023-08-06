"""
newstitle

A caching news title interface support 4 taiwan (ROC) main news paper.
Including realtime news and old article.

4 news paper are:
    chinatimes
    udn
    libertytimes
    appledaily
"""

__author__ = "Louie Lu (GrapherD) <grapherd at gmail.com>"
__license__ = "MIT"
__version__ = "0.1.0"

from newstitle.gettitle import *

support_news = gettitle.__all__
