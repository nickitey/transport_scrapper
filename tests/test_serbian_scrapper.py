import sys

sys.path.insert(1, "../serbian_lines_scrapper")

from main import BelgradTrasnportCrawler

headers = {
    "Accept": "text/html,application/xhtml+xml,"
              "application/xml;q=0.9,image/avif,"
              "image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/122.0.6261.952 "
                  "YaBrowser/24.4.1.952 (beta)"
                  "Yowser/2.5 Safari/537.36",
    # 'Content-Type': 'application/json, text/html; charset=UTF-8',
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept-Language": "ru,en;q=0.9",
}

base_url = "https://www.bgprevoz.rs/"


def test_language_change():
    crawler = BelgradTrasnportCrawler(base_url, headers=headers)
    latin_ver = crawler.change_to_latin()
    latin_soup = crawler.get_bs_object(latin_ver.text)
    assert latin_soup.html.attrs["lang"] == "sr-Latn-RS"
    slavic_ver = crawler.change_to_cyrillic()
    cyrillic_soup = crawler.get_bs_object(slavic_ver.text)
    assert cyrillic_soup.html.attrs["lang"] == "sr-Cyrl-RS"
    print("Test #1 passed. Correct letters are used.")


def test_list_collector():
    start_path = "/linije/red-voznje"
    with open(r"pdf_traces.txt", "r") as pdf_list:
        pdf_routes = set(pdf_list.read().split("\n"))
    with open(r"belgrad_routes_links.txt", "r") as links_list:
        clean_routes = set(links_list.read().split("\n"))
    with open(r"test_stylesheets.txt", "r") as test_stylesheets:
        stylesheets = set(test_stylesheets.read().split("\n"))

    whole_test_routes = {*pdf_routes, *clean_routes}
    crawler = BelgradTrasnportCrawler(base_url, headers=headers)
    crawler.change_to_latin()

    dirty_links = crawler.collect_links_to_crawl(start_path, "option")
    assert dirty_links == whole_test_routes

    clean_links = crawler.collect_links_to_crawl(
        start_path, "option", clear_from_pdf=True
    )
    assert clean_links == clean_routes

    stylesheet_links = crawler.collect_links_to_crawl(
        start_path, "link", "rel", "stylesheet"
    )
    assert stylesheet_links == stylesheets

    print("Test #2 passed. All links collected correctly.")
