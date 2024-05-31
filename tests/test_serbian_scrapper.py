import sys
from bs4 import BeautifulSoup as bs

sys.path.insert(1, "../serbian_lines_scrapper")

from main import BelgradTrasnportCrawler, MyBSException


headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
    "application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.952 "
    "YaBrowser/24.4.1.952 (beta) Yowser/2.5 Safari/537.36",
    # 'Content-Type': 'application/json, text/html; charset=UTF-8',
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Language": "ru,en;q=0.9",
}


def test_language_change():
    crawler = BelgradTrasnportCrawler("https://www.bgprevoz.rs/", headers=headers)
    latin_ver = crawler.change_to_latin()
    latin_soup = crawler.get_bs_object(latin_ver.text)
    assert latin_soup.html.attrs["lang"] == "sr-Latn-RS"
    slavic_ver = crawler.change_to_cyrillic()
    cyrillic_soup = crawler.get_bs_object(slavic_ver.text)
    assert cyrillic_soup.html.attrs["lang"] == "sr-Cyrl-RS"
    print("Test #1 passed. Correct letters are used.")


def test_list_collector():
    with open(r"pdf_traces.txt", "r") as pdf_list:
        list_of_pdfs = pdf_list.read().split("\n")

    with open(r"serbian_links.txt", "r") as links_list:
        clean_routes = links_list.read().split("\n")
