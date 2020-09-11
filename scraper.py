import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from random import choice
import re


class Scraper:

    def __init__(self, product):

        self.product = product
        self.total_products_count = 5

    def search(self):
        amazon_start_time = time.time()
        amazon_products_data = self.search_amazon()
        amazon_end_time = time.time()

        flipkart_start_time = time.time()
        flipkart_products_data = self.search_flipkart()
        flipkart_end_time = time.time()

        # mdcomputers_start_time = time.time()
        # mdcomputers_products_data = self.search_mdcomputers()
        # mdcomputers_end_time = time.time()

        # master_data = {'amazon_products_data': amazon_products_data, 'flipkart_products_data': flipkart_products_data, 'mdcomputers_products_data': mdcomputers_products_data}
        # print(master_data)

        # Debug
        print(amazon_products_data)
        print(flipkart_products_data)

        # Times
        print("Time to scrape Amazon =", amazon_end_time - amazon_start_time)
        print("Time to scrape Flipkart =", flipkart_end_time - flipkart_start_time)
        # print("Time to scrape MDComputers =", mdcomputers_end_time - mdcomputers_start_time)

    def search_amazon(self):
        # try:

            # Define headers for request
            user_agent_list = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
            ]

            user_agent = choice(user_agent_list)
            headers = {"User-Agent": user_agent}

            search_url = self.product.replace(' ', '+')
            url = 'https://www.amazon.in/s?k=' + search_url
            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.content, 'html.parser')

            main_div = soup.find_all('span', {'cel_widget_id': 'MAIN-SEARCH_RESULTS'})
            retry_count = 0

            # If the results are not present, retry by sending a request again until we hit the retry limit
            if main_div is None:

                retry_limit = 10
                while retry_count < retry_limit and main_div is None:
                    user_agent = choice(user_agent_list)
                    headers = {"User-Agent": user_agent}

                    response = requests.get(url, headers=headers)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    main_div = soup.find_all('span', {'cel_widget_id': 'SEARCH_RESULTS'})

                    retry_count += 1

            print(retry_count, url)
            # print(response.content)

            # If we still did not receive the results, return -1 as amazon not reachable
            if main_div is None:
                print("Did not get results from amazon")
                return -1

            amazon_products_data = defaultdict(dict)
            count = 0
            # print(main_div)
            for item_div in main_div:


                # Check if item is sponsored, skip it
                sponsored_div = item_div.find('div', {'data-component-type': 'sp-sponsored-result'})
                if sponsored_div is not None:
                    continue

                # item_name = item_div.find('span', {'class': 'a-size-medium a-color-base a-text-normal'})
                item_name = item_div.find('img')['alt']

                # Check if item is not listed on the amazon page
                if item_name is None:
                    continue

                amazon_products_data[count]['item_name'] = item_name.strip()

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

                count += 1
                if count == self.total_products_count:
                    return amazon_products_data

            return amazon_products_data


        #
        # except Exception as e:
        #     # Could not fetch data from Amazon
        #     return -1

    def search_flipkart(self):
        try:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

            url_list = ['https://www.flipkart.com/search?q=']
            search_list = self.product.split()
            for word in search_list:
                url_list.append(word)
                url_list.append('%20')
            url = "".join(url_list[:-1])

            response = requests.get(url, headers=headers)

            soup = BeautifulSoup(response.content, 'html.parser')

            all_divs = soup.find_all('div', {'class': 'bhgxx2 col-12-12'})[2:-2]

            flipkart_products_data = defaultdict(dict)

            # Regular expression used to find all strings
            regex = re.compile("^[a-zA-z]*")
            count = 0
            for div in all_divs:

                for item_div in soup.find_all("div", {"data-id": regex}):

                    # Get the name
                    item_name = item_div.find('img')['alt'].strip()
                    if item_name[-3:] == '...':
                        item_name = item_name[:-3]
                    flipkart_products_data[count]['item_name'] = item_name

                    # Get the rating
                    item_rating = item_div.find('span', {'id': re.compile("^productRating_")})
                    if item_rating is not None:
                        flipkart_products_data[count]['item_rating'] = "".join([item_rating.get_text().strip(), '/5'])
                    else:
                        flipkart_products_data[count]['item_rating'] = 'Unavailable'

                    # Get the price
                    # item_price = item_div.find_all('div', string='₹')
                    item_price = item_div.get_text().strip()
                    # Find a '₹'
                    index = item_price.find('₹')

                    if index == -1:
                        flipkart_products_data[count]['item_price'] = 'Unavailable'
                    else:
                        # Using a list because it is faster and more efficient than using strings
                        price = []
                        index += 1
                        while index < len(item_price) and (item_price[index] == ',' or item_price[index].isdigit()):

                            # Skip commas
                            if item_price[index].isdigit():
                                price.append(item_price[index])

                            index += 1

                        # Recombine list into string
                        item_price = "".join(price)
                        flipkart_products_data[count]['item_price'] = item_price

                        # Get the link
                        item_link = item_div.find("a", {"href": regex})
                        item_link = 'https://www.flipkart.com' + item_link['href']
                        flipkart_products_data[count]['item_link'] = item_link

                    count += 1
                    if count == self.total_products_count:
                        return flipkart_products_data

            return flipkart_products_data


        except Exception as e:
            # Could not fetch data from Flipkart
            return -1

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
# Time Test
tt = time.time()
for t in range(10):

    t1 = time.time()

    scraper = Scraper('rtx 2060')
    scraper.search()

    print("Total Time taken to complete scraping test {} = {}".format(t, time.time() - t1))

print("Total Time taken to complete scraping", time.time() - tt)

'''

t1 = time.time()
scraper = Scraper('make up')
scraper.search()
print("Total Time taken to complete scraping test = {}".format(time.time() - t1))
