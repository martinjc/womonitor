import os
import sys
import time
import string
import urllib

from datetime import date, datetime
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException

wales_online_page = 'http://www.walesonline.co.uk/'

weeks = [
    {"from": "2016-03-04", "to": "2016-03-08"}
]

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

    # get todays date
    today = date.today().isoformat()

    # if no directory for today, make one
    today_dir = os.path.join(cwd, today)
    if not os.path.isdir(today_dir):
        os.makedirs(today_dir)

    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    driver.maximize_window()

    date_from = '2016-03-03 00:00:00'
    date_to = '2016-03-08 23:59:59'

    dt_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
    dt_from_str = '%sZ' % dt_from.isoformat()

    dt_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
    dt_to_str = '%sZ' % dt_to.isoformat()

    date_range = "%s TO %s" % (dt_from_str, dt_to_str)

    params['dateRange'] = date_range
    params['searchString'] = "rugby"

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

        byline_time = driver.find_elements_by_css_selector('time.byline-time')

        messages = driver.find_elements_by_css_selector('.normalgroup a')
        
        message_addresses = []
        for message in messages:
            message_addresses.append(message.get_attribute('href'))

        for message_address in message_addresses:
            p = string.find(message_address, 'P=')
            p = message_address[p+2:]
            print(p)

            if not '%s.html' % p in files:

                # go to sleep for as long as necessary to avoid making more than 
                # one call to the website every 2 seconds
                while time.time() < earliest_query_time:
                    sleep_dur = earliest_query_time - time.time()
                    if sleep_dur > 0:
                        time.sleep(sleep_dur)

                earliest_query_time = time.time() + (query_interval)

                driver.get(message_address)
                page_code = driver.execute_script("return document.documentElement.innerHTML;")
                with open('%s.html' % (p), 'w') as output_file:
                    output_file.write(page_code.encode('utf-8'))

    driver.quit()


