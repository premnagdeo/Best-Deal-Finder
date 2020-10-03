import requests
from bs4 import BeautifulSoup
import time
from collections import defaultdict
from random import choice
import re


def search(product, total_products_count):
    # amazon_products_data = search_amazon(product, total_products_count)
    # flipkart_products_data = search_flipkart(product, total_products_count)
    # mdcomputers_products_data = search_mdcomputers(product, total_products_count)
    # neweggindia_products_data = search_neweggindia(product, total_products_count)
    # primeabgb_products_data = search_primeabgb(product, total_products_count)
    # theitdepot_products_data = search_theitdepot(product, total_products_count)

    master_data = {
        # 'amazon_products_data': amazon_products_data,
        # 'flipkart_products_data': flipkart_products_data,
        # 'mdcomputers_products_data': mdcomputers_products_data,
        # 'neweggindia_products_data': neweggindia_products_data,
        # 'primeabgb_products_data': primeabgb_products_data,
        #  'theitdepot_products_data': theitdepot_products_data
    }

    print(master_data)


def search_amazon(product, total_products_count):
    try:

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

        word_list = product.replace(' ', '+')
        url = 'https://www.amazon.in/s?k=' + word_list
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')

        main_div = soup.find_all('span', {'cel_widget_id': re.compile("^MAIN-SEARCH_RESULTS")})
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

        response.close()

        # If we still did not receive the results, return empty as amazon not reachable
        if main_div is None:
            print("Did not get results from Amazon")
            return {}

        amazon_products_data = defaultdict(dict)
        count = 0

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

            amazon_products_data[count]['item_name'] = item_name.strip().replace(u'\xa0', u' ')

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
            if count == total_products_count:
                return amazon_products_data

        return amazon_products_data

    except Exception as e:
        # Could not fetch data from Amazon
        return {}


def search_flipkart(product, total_products_count):
    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

        url_list = ['https://www.flipkart.com/search?q=']
        word_list = product.split()
        for word in word_list:
            url_list.append(word)
            url_list.append('%20')
        url = "".join(url_list[:-1])

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        all_divs = soup.find_all('div', {'class': 'bhgxx2 col-12-12'})[2:-2]

        flipkart_products_data = defaultdict(dict)

        # Regular expression used to find all strings
        regex = re.compile("^[a-zA-z]*")
        count = 0
        for div in all_divs:

            for item_div in soup.find_all("div", {"data-id": regex}):

                # Get the name
                item_name = item_div.find('img')['alt'].strip()
                if item_name == "":
                    # Try to find item name in anchor tags:
                    anchor_tags = item_div.find_all('a')
                    for tag in anchor_tags:
                        text = tag.get('title')
                        if text is not None:
                            item_name = text
                if item_name[-3:] == '...':
                    item_name = item_name[:-3]

                if item_name == "":
                    flipkart_products_data[count]['item_name'] = "Unavailable"
                else:
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
                if count == total_products_count:
                    return flipkart_products_data

        return flipkart_products_data

    except Exception as e:
        # Could not fetch data from Flipkart
        return {}


def search_mdcomputers(product, total_products_count):
    try:

        word_list = product.replace(' ', '+')
        url = 'https://mdcomputers.in/index.php?category_id=0&search=' + word_list + '&submit_search=&route=product%2Fsearch'
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        items_div = soup.find_all('div', {'class': 'product-item-container'})
        # print(items_div)

        mdcomputers_products_data = defaultdict(dict)

        loop_range = min(total_products_count, len(items_div))
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

    except Exception as e:
        # Could not fetch data from MDComputers
        return {}


def search_neweggindia(product, total_products_count):
    try:

        # Had to add cookies to header to display india price
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36',
                   'cookie': 'NVTC=248326808.0001.7wr7he7ix.1599927401.1599927401.1599927401.1; NID=9D6I4M9D2Q1j9D2Q6I; NSC_mc-xxx.ofxfhh.dpn-vsmibti=475ca3ddf9096b5394cdf2067cf96644e527b629071ac9e769a6067ee21d293c1b88d203; NV%5FW57=IND; NV%5FW62=en; NV%5FCONFIGURATION=#5%7B%22Sites%22%3A%7B%22USA%22%3A%7B%22Values%22%3A%7B%22w58%22%3A%22INR%22%7D%2C%22Exp%22%3A86400000000%7D%7D%7D; INGRESSCOOKIE=1599927405.297.1966.356529; NV_NVTCTIMESTAMP=1599927421'
                   }

        word_list = product.replace(' ', '+')
        url = 'https://www.newegg.com/global/in-en/p/pl?d=' + word_list
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        main_div = soup.find('div', {'class': 'row-body-inner'})

        items_div = main_div.find_all('div', {'class': 'item-cell'})

        count = 0
        neweggindia_products_data = defaultdict(dict)
        for item_div in items_div:

            # Skip ads and sponsored items
            sponsored_div = item_div.find('div', {'class': 'item-sponsored menu-box'})
            ad_content = item_div.find('a', {'class': 'txt-ads-box theme-gray'})
            if sponsored_div is not None or ad_content is not None:
                continue
            # Get the name
            item_name = item_div.find('a', {'class': 'item-title'})
            neweggindia_products_data[count]['item_name'] = item_name.get_text().strip()

            # Get the rating
            item_rating = item_div.find('a', {'class': 'item-rating'})
            if item_rating is None:
                neweggindia_products_data[count]['item_rating'] = 'Unavailable'
            else:
                item_rating = item_rating['title'][-1]
                neweggindia_products_data[count]['item_rating'] = "".join([str(item_rating), '/5'])

            # Get the price
            item_price = item_div.find('li', {'class': 'price-current'})
            if not item_price:
                neweggindia_products_data[count]['item_price'] = "Unavailable"
            else:
                item_price = item_price.get_text().split()[1]
                neweggindia_products_data[count]['item_price'] = item_price

            # Get the link
            item_link = item_div.find('a', {'class': 'item-title'})['href']
            neweggindia_products_data[count]['item_link'] = item_link

            count += 1
            if count == total_products_count:
                return neweggindia_products_data

        return neweggindia_products_data

    except Exception as e:
        # Could not fetch data from MDComputers
        return {}


def search_primeabgb(product, total_products_count):
    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

        word_list = product.replace(' ', '+')
        url = 'https://www.primeabgb.com/?post_type=product&taxonomy=product_cat&s=' + word_list + '&pa-_stock_status=instock&orderby=relevance'
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        main_div = soup.find('div', {'class': 'main-content col-md-9 col-sm-8'})
        regex = re.compile("^product-item")
        items_div = main_div.find_all('li', {'class': regex})

        primeabgb_products_data = defaultdict(dict)

        count = 0

        for item_div in items_div:
            # print(item_div)
            # print("NEXT")

            # Get the name
            name_div = item_div.find('h3', {'class': 'product-name short'})
            primeabgb_products_data[count]['item_name'] = name_div.get_text().strip()

            # Get the rating
            item_rating = item_div.find('div', {'class': 'star-rating'})
            if item_rating is not None:
                item_rating = item_rating.find('strong').get_text().strip()

                # Standardize data
                if item_rating[-3:] == '.00':
                    item_rating = item_rating[:-3]
                elif item_rating[-1] == '0':
                    item_rating = item_rating[:-1]

                primeabgb_products_data[count]['item_rating'] = "".join([str(item_rating), '/5'])

            else:
                primeabgb_products_data[count]['item_rating'] = 'Unavailable'

            # Get the price
            price_span = item_div.find('span', {'class': 'price'})
            if 'Call for Price' in price_span.get_text():
                primeabgb_products_data[count]['item_price'] = 'Unavailable'
            else:
                item_price = price_span.get_text().split()[-1]

                # Skip the '₹' symbol
                item_price = item_price[1:]

                # Get rid of commas in the string
                item_price = item_price.replace(',', '')
                primeabgb_products_data[count]['item_price'] = item_price

            # Get the link
            item_link = name_div.find('a')['href']
            primeabgb_products_data[count]['item_link'] = item_link

            count += 1
            if count == total_products_count:
                return primeabgb_products_data

        return primeabgb_products_data

    except Exception as e:
        # Could not fetch data from MDComputers
        return {}


def search_theitdepot(product, total_products_count):
    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36'}

        word_list = product.replace(' ', '+')
        url = 'https://www.theitdepot.com/search.html?keywords=' + word_list
        response = requests.get(url, headers=headers)

        soup = BeautifulSoup(response.content, 'html.parser')
        response.close()

        main_div = soup.find_all('div', {'class': 'col'})[3]

        items_div = main_div.find_all('div', {'class': 'product-item'})

        theitdepot_products_data = defaultdict(dict)

        count = 0

        for item_div in items_div:

            # Skip the item if it is out of stock
            if "Out of Stock" in item_div.get_text():
                continue

            # Get the name
            item_name_div = item_div.find('div', {'itemprop': 'name'})
            item_name = item_name_div.find('a').get_text()
            theitdepot_products_data[count]['item_name'] = item_name

            # Rating is unavailable on the website
            theitdepot_products_data[count]['item_rating'] = "Unavailable"

            # Get the price

            item_price = item_div.find('strong').get_text().strip()

            theitdepot_products_data[count]['item_price'] = item_price

            # Get the link
            item_link = item_name_div.find('a')['href']
            theitdepot_products_data[count]['item_link'] = "".join(["https://www.theitdepot.com/", item_link])

            count += 1

            if count == total_products_count:
                return theitdepot_products_data

        return theitdepot_products_data

    except Exception as e:
        # Could not fetch data from The IT Depot
        return {}
