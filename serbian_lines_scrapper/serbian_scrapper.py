import random
from main import MyBSException, BelgradTrasnportCrawler
from routes_scrapper import BelgradRoute, RoutesScrapper
import csv
from pprint import pprint

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,'
              'application/signed-exchange;v=b3;q=0.7',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.952 '
                  'YaBrowser/24.4.1.952 (beta) Yowser/2.5 Safari/537.36',
    # 'Content-Type': 'application/json, text/html; charset=UTF-8',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept-Language': 'ru,en;q=0.9'
}

base_url = "https://www.bgprevoz.rs/"


crawler = RoutesScrapper(base_url, headers)
crawler.change_to_latin()

links = list(crawler.collect_links_to_crawl('/linije/red-voznje', 'option'))


indices = [random.randint(0, len(links)) for i in range(10)]

lim_links = [links[i] for i in indices]

result = crawler.parse_all_routes(direct_links=lim_links)
for item in result:
    item.get_route_csv(f'{item.description}.csv')



















'''
crawler = RoutesScrapper(base_url, headers)
crawler.change_to_latin()
route = crawler.parse_route('https://www.bgprevoz.rs/linije/red-voznje/linija/2/prikaz')
route.get_station_csv('Unutrašnji Krug', 'Unutrašnji Krug.csv')
with open('Unutrašnji Krug.csv', 'r') as r:
    reader = csv.reader(r)
    print(next(reader))
    for line in reader:
        print(line)
        break
        



def list_collector():
    crawler = BelgradTrasnportCrawler(base_url, headers=headers)
    crawler.change_to_latin()
    dirty_links = crawler.collect_links_to_crawl('/linije/red-voznje',
                                                 'link', 'rel', 'stylesheet')
    output = open(r'test_stylesheets.txt', 'w')
    print('\n'.join(list(dirty_links)), file=output)
    output.close()


list_collector()

slavic_ver = crawler.change_to_cyrillic()
print(slavic_ver.request)
cyrillic_soup = crawler.get_bs_object(slavic_ver.text)
try:
    assert cyrillic_soup.html.attrs['lang'] == 'sr-Cyrl-RS'
except AssertionError:
    print(slavic_ver.status_code,
          cyrillic_soup.html.attrs['lang'])
print('Test #1 passed. Correct letters are used.')


url2 = 'https://www.bgprevoz.rs/locale/change'


session = requests.Session()
session.headers.update(headers)
first_request = session.get(url1)
full_html = first_request.text


srpski_soup = bs(full_html, 'html.parser')
token = srpski_soup.find('meta', {'name': 'csrf-token'}).attrs['content']
payload = {'latin': 'true', '_token': token}
second_request = session.post(url2, data=payload)
pdf_list = open(r'../tests/test_pdf_routes.txt', 'w')
if second_request.status_code == 200:
    latin_srpski_soup = bs(second_request.text, 'html.parser')
    select_form = latin_srpski_soup.find('select')
    links = []
    for option in select_form.children:
        try:
            link = option.attrs['value'].strip()
        except AttributeError:
            continue
        if link.endswith('.pdf'):
            print(link, file=pdf_list)
            continue
        links.append(link)
    with open(r'../tests/test_html_routes.txt', 'w') as out:
        out.write('\n'.join(links).strip())
else:
    #print(second_request.status_code, second_request.headers, sep='\n')
    print('not ok')

pdf_list.close()
print('Готово')
'''
