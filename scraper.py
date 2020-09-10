import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict



class Scraper:

    def __init__(self, product):



        self.product = product
        self.total_products_count = 5

    def search(self):
        # amazon_start_time = time.time()
        # amazon_products_data = self.search_amazon()
        # amazon_end_time = time.time()


        flipkart_start_time = time.time()
        flipkart_products_data = self.search_flipkart()
        flipkart_end_time = time.time()

        # mdcomputers_start_time = time.time()
        # mdcomputers_products_data = self.search_mdcomputers()
        # mdcomputers_end_time = time.time()

        # master_data = {'amazon_products_data': amazon_products_data, 'flipkart_products_data': flipkart_products_data, 'mdcomputers_products_data': mdcomputers_products_data}
        # print(master_data)

        # Debug
        # print(amazon_products_data)
        print(flipkart_products_data)

        # Times
        # print("Time to scrape Amazon =", amazon_end_time - amazon_start_time)
        print("Time to scrape Flipkart =", flipkart_end_time - flipkart_start_time)
        # print("Time to scrape MDComputers =", mdcomputers_end_time - mdcomputers_start_time)



    def search_amazon(self):
        try:
            # Define headers for request
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}
            '''
            url_list = ['https://www.amazon.in/s?k=']
            search_list = self.product.split()
            for word in search_list:
                url_list.append(word)
                url_list.append('+')

            url = "".join(url_list[:-1])
            '''
            url = 'https://www.amazon.in/s?k=' + self.product
            response = requests.get(url, headers=headers)


            soup = BeautifulSoup(response.content, 'html.parser')

            main_div = soup.find('div', {'class': 's-main-slot s-result-list s-search-results sg-row'})
            retry_count = 0

            # If the results are not present, retry by sending a request again until we hit the retry limit
            if main_div is None:

                retry_limit = 10
                while retry_count < retry_limit and main_div is None:

                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    main_div = soup.find('div', {'class': 's-main-slot s-result-list s-search-results sg-row'})

                    retry_count += 1

            # If we still did not receive the results, return -1 as amazon not reachable
            if main_div is None:
                return -1

            amazon_products_data = defaultdict(dict)

            count = 0
            i = 0
            while count < self.total_products_count:
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
                    item_rating = "".join([item_rating.split()[0], '/5'])

                    amazon_products_data[count]['item_rating'] = item_rating
                else:
                    amazon_products_data[count]['item_rating'] = 'Unavailable'

                # Get the price
                item_price = item_div.find('span', {'class': 'a-price-whole'})
                if item_price is not None:
                    # Get rid of commas in the string
                    item_price = item_price.get_text().strip().replace(',', '')
                    amazon_products_data[count]['item_price'] = item_price
                else:
                    amazon_products_data[count]['item_price'] = 'Unavailable'

                # Get the link
                item_link = item_div.find('a', {'class': 'a-link-normal a-text-normal'})
                amazon_products_data[count]['item_link'] = "".join(['https://www.amazon.in', item_link['href']])

                i += 1
                count += 1

            return amazon_products_data

        except Exception as e:
            # Could not fetch data from Amazon
            return -1

    def search_flipkart(self):
        # try:

            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

            url_list = ['https://www.flipkart.com/search?q=']
            search_list = self.product.split()
            for word in search_list:
                url_list.append(word)
                url_list.append('%20')
            url = "".join(url_list[:-1])

            response = requests.get(url, headers=headers)
            # print(response.content)
            soup = BeautifulSoup(response.content, 'html.parser')
            # print(soup.prettify())

            all_divs = soup.find_all('div', {'class': 'bhgxx2 col-12-12'})


            for div in all_divs:
                print(div.prettify())
                print("NEXT")

        # except Exception as e:
        #     # Could not fetch data from Flipkart
        #     return -1

    def search_mdcomputers(self):
        # try:
            self.browser.get('https://mdcomputers.in/')

            search_bar = self.browser.find_element_by_xpath('/html/body/div[1]/header/div[2]/div/div/div[2]/div[1]/div/form/div/input')

            search_bar.send_keys(self.product)
            search_bar.submit()
            time.sleep(5)

            src = self.browser.page_source
            soup = BeautifulSoup(src, 'html.parser')

            items_div = soup.find_all('div', {'class': 'product-item-container'})
            # print(items_div)

            mdcomputers_products_data = defaultdict(dict)

            loop_range = min(self.total_products_count, len(items_div))
            for count in range(loop_range):
                item_div = items_div[count]

                # Get the name
                item_name = item_div.find('a')['title']
                mdcomputers_products_data[count]['item_name'] = item_name.strip()

                # Get the rating

                # First we check if the product has 0 reviews, if no reviews -> rating = Unavailable
                item_rating = item_div.find('a', {'class': 'rating-num'}).get_text()

                if '0 reviews' in item_rating:
                    mdcomputers_products_data[count]['item_rating'] = 'Unavailable'

                else:
                    # Rating is present
                    # For rating we find the number of stars that are colored out of 5 stars
                    colored_stars = item_div.find_all('i', {'class': 'fa fa-star fa-stack-1x'})
                    item_rating = len(colored_stars)

                    mdcomputers_products_data[count]['item_rating'] = "".join([str(item_rating), '/5'])

                # Get the price
                item_price = item_div.find('span', {'class': 'price-new'})
                # Remove the rupees symbol at the beginning
                # Get rid of commas in the string
                item_price = item_price.get_text().strip()[1:].replace(',', '')
                mdcomputers_products_data[count]['item_price'] = item_price

                # Get the link
                item_link = item_div.find('a')['href']
                mdcomputers_products_data[count]['item_link'] = item_link.strip()

            return mdcomputers_products_data

        # except Exception as e:
        #     # Could not fetch data from MDComputers
        #     return -1


'''
tt = time.time()
for t in range(10):

    t1 = time.time()

    scraper = Scraper('rtx 2060')
    scraper.search()

    print("Total Time taken to complete scraping test {} = {}".format(t, time.time() - t1))

print("Total Time taken to complete scraping", time.time() - tt)

'''

t1 = time.time()
scraper = Scraper('rtx')
scraper.search()
print("Total Time taken to complete scraping test = {}".format(time.time() - t1))