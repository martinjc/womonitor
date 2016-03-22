import os
import sys
import time
import string
import urllib

from datetime import date, datetime
from selenium import webdriver

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
    "searchString": "test",
    "dateRange": "2016-03-03T00:00:001Z TO 2016-03-08T23:59:59Z"
}
    

if __name__ == "__main__":

    # current working directory
    cwd = os.getcwd()

    # get todays date
    today = date.today().isoformat()

    # if no directory for today, make one
    today_dir = os.path.join(cwd, today)
    if not os.path.isdir(today_dir):
        os.makedirs(today_dir)

    # driver = webdriver.Chrome()
    # driver.implicitly_wait(10)
    # driver.maximize_window()
    
    # only want to access a page once every 2 seconds 
    #so we don't thrash the mfp server too much
    earliest_query_time = time.time()
    query_interval = 4

    # driver.get(simple_search_url)

    data = urllib.parse.urlencode(params)

    print('%s?%s' % (base_url, data))

    date_from = '2016-03-03 00:00:00'
    date_to = '2016-03-08 23:59:59'

    dt_from = datetime.strptime(date_from, "%Y-%m-%d %H:%M:%S")
    dt_from_str = '%sZ' % dt_from.isoformat()

    dt_to = datetime.strptime(date_to, "%Y-%m-%d %H:%M:%S")
    dt_to_str = '%sZ' % dt_to.isoformat()

    date_range = "%s TO %s" % (dt_from_str, dt_to_str)

    print(date_range)

    # driver.quit()
    sys.exit(0)

    page_list = driver.find_elements_by_css_selector('ul li a')
    page_addresses = []
    for page in page_list:
        page_addresses.append(page.get_attribute('href'))

    for page_address in page_addresses:

        # go to sleep for as long as necessary to avoid making more than 
        # one call to the website every 2 seconds
        while time.time() < earliest_query_time:
            sleep_dur = earliest_query_time - time.time()
            print(sleep_dur)
            if sleep_dur > 0:
                time.sleep(sleep_dur)

        earliest_query_time = time.time() + (query_interval)

        driver.get(page_address)
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


