import requests
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


'''
爬取：纵横小说，采集最新免费小说

结构：Soup 数据爬取，Pager 数据整理
待做：提交验证码
作者：不才
日期：2019年5月15日
修改：2019年5月15日
协作：

'''


class Soup():
    def __init__(self, target):
        self._http = requests.Session()
        self.soup = self.get_soup(target)

    def get_html(self, target):
        res = self._http.get(url=target)
        return res.text

    def get_soup(self, target):
        html = self.get_html(target)
        soup = BeautifulSoup(html, 'lxml')
        return soup


class Parser():
    def __init__(self, target):
        self.soup = Soup(target).soup

    def get_element(self, tag, attrs, find_all=False):
        if find_all is False:
            return self.soup.find(name=tag, attrs=attrs)
        else:
            return self.soup.find_all(name=tag, attrs=attrs)

    @staticmethod
    def get_element_by_subsoup(soup, tag, attrs, find_all=False):
        if find_all is False:
            return soup.find(name=tag, attrs=attrs)
        else:
            return soup.find_all(name=tag, attrs=attrs)

class Pager(Parser):
    def __init__(self, target):
        super().__init__(target)

    def content(self):
        element = self.get_element('div', {'class': 'content'})
        text = element.text
        logger.info(text)
        return text

    def next_page(self):
        element = self.get_element('a', {'class': 'nextchapter'})
        logger.info(element['href'])
        return element['href']

    def location(self):
        element = self.get_element('div', {'class': 'reader_crumb'})
        logger.info(element.text)
        return element.text

    def bookinfo(self):
        element = self.get_element('div', {'class': 'bookinfo'})
        logger.info(element.text)
        return element.text

    def title(self):
        element = self.get_element('div', {'class': 'title_txtbox'})
        logger.info(element.text)
        return element.text

    def new_chapter(self):
        element = self.get_element('span', {'class': 'tabT active'})
        element = self.get_element_by_subsoup(element, 'a', {'class': 'more-link'})
        logger.info(element['href'])
        return element['href']

    def storys(self):
        element = self.get_element('div', {'class': 'store_collist'})
        logger.info(element)
        element = self.get_element_by_subsoup(element, 'div', {'class': 'bookname'}, find_all=True)
        dic = {}
        for i in element:
            dic[i.a.text] = i.a['href']
        logger.info(dic)
        return dic

    def read_button(self):
        element = self.get_element('a', {'class': 'btn read-btn'})
        logger.info(element['href'])
        return element['href']


if __name__ == '__main__':
    import time
    homepage = 'http://www.zongheng.com/'
    page = Pager(homepage)
    new_chapter = page.new_chapter()

    page = Pager(new_chapter)
    storys = page.storys()
    # 列表遍历
    for key in storys:
        logger.info('%s %s' % (key, storys[key]))

        page = Pager(storys[key])
        read_button = page.read_button()
        target = read_button
        # 章节遍历
        while(True):
            page = Pager(target)
            content = page.content()
            next_page = page.next_page()
            if next_page == 'javascript:void(0)':
                logger.info('done')
                time.sleep(5)
                break
            target = next_page
            location = page.location()
            title = page.title()
            bookinfo = page.bookinfo()
