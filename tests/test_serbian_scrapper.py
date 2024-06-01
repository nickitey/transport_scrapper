import csv
import logging
import sys

sys.path.insert(1, "../serbian_lines_scrapper")

from main import BelgradTrasnportCrawler
from routes_scrapper import BelgradRoute, RoutesScrapper

date_format = "%d/%m/%Y"
time_format = "%H:%M:%S"

logging.basicConfig(
    filemode="w",
    format="%(asctime)s %(levelname)s:%(message)s\n",
    datefmt=f"{date_format} {time_format}",
    filename="scrapper_test.log",
    encoding="utf-8",
    level=logging.INFO,
)


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


def test_route_scrapper():
    route_example = "https://www.bgprevoz.rs/linije/red-voznje/linija/2/prikaz"
    scrapper = RoutesScrapper(base_url, headers)
    scrapper.change_to_latin()

    parsed_route = scrapper.parse_route(route_example)
    assert parsed_route.route_name == "Red vožnje linija 2"
    assert parsed_route.first_station == "Unutrašnji Krug"
    assert parsed_route.last_station == "Spoljašnji Krug"

    route_dict = parsed_route.get_dict()
    assert (
        "Radni dan" in route_dict["first_station"]["departures"]
        and "Subota" in route_dict["last_station"]["departures"]
        and "Nedelja" in route_dict["first_station"]["departures"]
    )
    assert "17:07" in route_dict["first_station"]["departures"]["Nedelja"]
    assert "07:20" in route_dict["last_station"]["departures"]["Subota"]
    assert "22:04" in route_dict["first_station"]["departures"]["Radni dan"]

    parsed_route.get_station_csv("Spoljašnji Krug", "test_station.csv")
    with open("test_station.csv", "r") as r:
        reader = csv.reader(r)
        assert ["Radni dan", "Subota", "Nedelja"] == next(reader)
        lines_in_csv = []
        for line in reader:
            lines_in_csv.append(line)
        assert ["09:11", "10:40", "10:40"] in lines_in_csv
        assert ["12:00", "14:00", "14:00"] in lines_in_csv
        assert ["14:51", "18:00", "18:00"] in lines_in_csv
        assert ["23:50"] in lines_in_csv

        print("Test #3 passed. Route parsed and wrote to file correctly.")
