from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time
from collections import defaultdict




class Scraper:

    def __init__(self):
        # Initialize Options to start Chrome as headless in selenium
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument("--headless")
        self.capabilities = DesiredCapabilities.CHROME.copy()
        self.capabilities['acceptSslCerts'] = True
        self.capabilities['acceptInsecureCerts'] = True

        # Initialize the chrome webdriver as 'browser'
        # self.browser = webdriver.Chrome(options=self.chrome_options, desired_capabilities=self.capabilities)

        # To initialize the webdriver in a new window for Debugging:
        self.browser = webdriver.Chrome('chromedriver.exe')

    def search(self, product):
        self.product = product
        amazon_products_data = self.search_amazon()
        print(amazon_products_data)
        flipkart_products_data = self.search_flipkart()
        print(flipkart_products_data)

    def search_amazon(self):
        self.browser.get('https://www.amazon.in/')

        search_bar = self.browser.find_element_by_id('twotabsearchtextbox')
        search_bar.send_keys(self.product)
        search_bar.submit()
        time.sleep(5)

        src = self.browser.page_source
        soup = BeautifulSoup(src, 'html.parser')

        main_div = soup.find('div', {'class': 's-main-slot s-result-list s-search-results sg-row'})

        amazon_products_data = defaultdict(dict)

        # Collect data of top 5 items:
        count = 0
        i = 0
        while count < 5:
            item_div = main_div.find('div', {'data-index': str(i)})

            # Check if item is sponsored, skip it
            sponsored_div = item_div.find('div', {'data-component-type': 'sp-sponsored-result'})
            if sponsored_div is not None:
                i += 1
                continue

            # Check if item is not listed on the amazon page
            item_name = item_div.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
            if item_name is None:
                i += 1
                continue

            amazon_products_data[count]['item_name'] = item_name.get_text().strip()

            # Get the rating
            item_rating = item_div.find('span', {'class': 'a-declarative'})
            if item_rating is not None:
                item_rating = item_rating.get_text().strip()
                item_rating = item_rating.split()[0]
                item_rating = item_rating + '/5'
                amazon_products_data[count]['item_rating'] = item_rating
            else:
                amazon_products_data[count]['item_rating'] = 'Unavailable'

            # Get the price
            item_price = item_div.find('span', {'class': 'a-price-whole'})
            if item_price is not None:
                amazon_products_data[count]['item_price'] = item_price.get_text().strip()
            else:
                amazon_products_data[count]['item_price'] = 'Unavailable'

            # Get the link
            item_link = item_div.find('a', {'class': 'a-link-normal a-text-normal'})
            amazon_products_data[count]['item_link'] = 'https://www.amazon.in' + item_link['href']

            i += 1
            count += 1

        return amazon_products_data

    def search_flipkart(self):

        self.browser.get('https://www.flipkart.com/')

        # Skip login prompt if it pops up:
        try:
            close_login_prompt_button = self.browser.find_element_by_xpath("/html/body/div[2]/div/div/button")

            close_login_prompt_button.click()
        except Exception as e:
            print("Exception when tried to close login pop up:", e)

        search_bar = self.browser.find_element_by_class_name('LM6RPg')

        search_bar.send_keys(self.product)
        search_bar.submit()
        time.sleep(5)

        src = self.browser.page_source
        soup = BeautifulSoup(src, 'html.parser')

        items_div = soup.find_all('div', {'class': '_3O0U0u'})


        flipkart_products_data = defaultdict(dict)

        for count in range(min(5, len(items_div))):

            item_div = items_div[count]

            # Get the name
            item_name = item_div.find('div', {'class': '_3wU53n'}).get_text().strip()
            if item_name[-3:] == '...':
                item_name = item_name[:-3]
            flipkart_products_data[count]['item_name'] = item_name


            # Get the rating
            item_rating = item_div.find('div', {'class': 'hGSR34'})
            if item_rating is not None:
                flipkart_products_data[count]['item_rating'] = item_rating.get_text().strip() + '/5'
            else:
                flipkart_products_data[count]['item_rating'] = 'Unavailable'


            # Get the price
            item_price = item_div.find('div', {'class': '_1vC4OE _2rQ-NK'})
            if item_price is not None:
                # Remove the rupees symbol at the beginning
                flipkart_products_data[count]['item_price'] = item_price.get_text().strip()[1:]
            else:
                flipkart_products_data[count]['item_price'] = 'Unavailable'

            # Get the link
            item_link = item_div.find('a', {'class': '_31qSD5'})
            flipkart_products_data[count]['item_link'] = 'https://www.flipkart.com' + item_link['href']


        return flipkart_products_data


t1 = time.time()


scraper = Scraper()
scraper.search('rtx 2060')

print(time.time() - t1)