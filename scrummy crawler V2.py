import requests
from bs4 import BeautifulSoup
import csv
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def load_user_agents(filepath):
    user_agents = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            user_agent = line.split('\t')[0].strip()
            if user_agent:
                user_agents.append(user_agent)
    return user_agents


def get_page_data(url, user_agent):
    headers = {
        'User-Agent': user_agent
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    products = soup.find_all('article', class_='products__miniature')
    results = []

    for product in products:
        link = product.find('meta', {'itemprop': 'url'})['content']
        name = product.find('h1', class_='products__miniature__name').find('a').text.strip()

        gtin_meta = product.find('meta', {'itemprop': 'gtin'})
        ean = gtin_meta['content'] if gtin_meta else None

        category = product.find('meta', {'itemprop': 'category'})['content']

        results.append({
            'link': link,
            'name': name,
            'ean': ean,
            'category': category,
        })

    return results


def main():
    start_url = "https://www.scrummy.pl/2-strona-glowna"
    user_agents = load_user_agents('user-agents.tsv')

    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    pages_count = int(soup.find('input', {'data-max-page': True})['data-max-page'])

    with open('dataV2.csv', 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['link', 'name', 'ean', 'category'])
        if csvfile.tell() == 0:
            writer.writeheader()

        for page_number in range(226, pages_count + 1):
            logging.info(f'Przetwarzanie strony {page_number} z {pages_count}')
            new_url = f"{start_url}?page={page_number}"

            random_sleep_time = random.uniform(1, 7)
            time.sleep(random_sleep_time)

            user_agent = random.choice(user_agents)
            new_products = get_page_data(new_url, user_agent)

            for product in new_products:
                writer.writerow(product)


if __name__ == "__main__":
    main()
