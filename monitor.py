import os
import sys
import time
import string
import urllib

from datetime import date, datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import StaleElementReferenceException

wales_online_page = 'http://www.walesonline.co.uk/'

dev_weeks = [
    {"from": "2016-03-04", "to": "2016-03-08"},
    {"from": "2016-02-12", "to": "2016-02-18"},
]

weeks = [
    {"from": "2016-04-04", "to": "2016-04-08"},
    {"from": "2016-04-18", "to": "2016-04-22"},
    {"from": "2016-05-02", "to": "2016-05-06"},
    {"from": "2016-05-16", "to": "2016-05-20"},
    {"from": "2016-05-30", "to": "2016-06-03"},
    {"from": "2016-06-13", "to": "2016-06-17"},
    {"from": "2016-06-27", "to": "2016-07-01"},
    {"from": "2016-07-11", "to": "2016-07-15"},
]

terms = ['poverty', 'economic', 'financial', 'impoverish']

start_day = "00:00:00"
end_day = "23:59:59"

base_url = "http://www.walesonline.co.uk/search/advanced.do"

params = {
    "destinationSectionId": 3657,
    "publicationName": "walesonline",
    "sortString": "publishdate",
    "sortOrder": "desc",
    "sectionId": "3533",
    "articleTypes": " news opinion advice live-event ive-event-clone",
    "pageNumber": 1,
    "pageLength": 1000,
    "searchString": "",
    "dateRange": ""
}
 

def wait_for(condition_function):
    start_time = time.time()
    while time.time() < start_time + 3:
        if condition_function():
            return True
        else:
            time.sleep(0.1)
    raise Exception(
        'Timeout waiting for {}'.format(condition_function.__name__)
    )


if __name__ == "__main__":

    # current working directory
    cwd = os.getcwd()

    chrome_options = Options()
    chrome_options.add_extension('adblockpluschrome.crx')

    # start a webbrowser
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.implicitly_wait(5)
    driver.maximize_window()

    for week in dev_weeks:

        date_from = '%s %s' % (week['from'], start_day)
        date_to = '%s %s' % (week['to'], end_day)

        dt_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
        dt_from_str = '%sZ' % dt_from.isoformat()

        dt_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
        dt_to_str = '%sZ' % dt_to.isoformat()

        date_range = "%s TO %s" % (dt_from_str, dt_to_str)

        out_dir = '%s to %s' % (dt_from.date().isoformat(), dt_to.date().isoformat())

        # if no directory for today, make one
        out_dir = os.path.join(cwd, out_dir)
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

        params['dateRange'] = date_range

        for term in terms:
            params['searchString'] = term

            data = urllib.parse.urlencode(params)
            search_url = '%s?%s' % (base_url, data)

            driver.get(search_url)
            
            page_list = driver.find_elements_by_css_selector('.article.ma-teaser h3 a')
            page_addresses = []
            for page in page_list:
                page_addresses.append(page.get_attribute('href'))

            next_button = driver.find_elements_by_css_selector('.pagination a[rel=next].ir')

            while len(next_button) > 0:

                next_button[0].click()

                def link_has_gone_stale():
                    try:
                        # poll the link with an arbitrary call
                        next_button[0].find_elements_by_id('doesnt-matter') 
                        return False
                    except StaleElementReferenceException:
                        return True        

                wait_for(link_has_gone_stale)

                new_page_list = driver.find_elements_by_css_selector('.article.ma-teaser h3 a')
                for page in new_page_list:
                    page_addresses.append(page.get_attribute('href'))
                next_button = driver.find_elements_by_css_selector('.pagination a[rel=next].ir')
            
            print(page_addresses)
            print(len(page_addresses))

            for page_address in page_addresses:

                driver.get(page_address)

                title_loc = page_address.rfind('/')
                title = page_address[title_loc+1:]

                print(title)

                file_prefix = os.path.join(out_dir, title)

                headline = driver.find_elements_by_css_selector('.article-page h1')
                headline = headline[0].text

                lead = driver.find_elements_by_css_selector('.lead-text h2')
                lead = lead[0].text

                article_paragraphs = driver.find_elements_by_css_selector('div.body[itemprop=articleBody] p')
                article_text = "\n".join([p.text for p in article_paragraphs])

                with open('%s.txt' % (file_prefix), 'w') as text_file:
                    text_file.write('%s\n\n' % headline)
                    text_file.write('%s\n\n' % lead)
                    text_file.write('%s' % article_text)

                page_code = driver.execute_script("return document.documentElement.innerHTML;")
                with open('%s.html' % (file_prefix), 'w') as html_file:
                    html_file.write(page_code)

                page_height = driver.execute_script("return document.body.scrollHeight;")
                window_height = driver.execute_script("return window.innerHeight - 200;")

                total_scrolled = window_height
                
                count = 0
                driver.save_screenshot('%s-%d.png' % (file_prefix, count))

                while(total_scrolled <= page_height):
                    count += 1
                    driver.execute_script('window.scrollTo(0, %d);' % (count * window_height))
                    time.sleep(1)
                    driver.save_screenshot('%s-%d.png' % (file_prefix, count))
                    total_scrolled += window_height


    driver.quit()


