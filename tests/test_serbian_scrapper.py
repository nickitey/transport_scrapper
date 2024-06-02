import csv
import logging
import os
import random
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


def test_links_collector():
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

    dirty_links = crawler.collect_links_to_crawl(
        start_path, "option", clear_from_pdf=False
    )
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
        first_string = next(reader)
        assert ["Spoljašnji Krug"] == first_string
        second_string_empty = next(reader)
        third_string = next(reader)
        assert ["Radni dan", "Subota", "Nedelja"] == third_string
        lines_in_csv = []
        for line in reader:
            lines_in_csv.append(line)
        assert ["09:11", "10:40", "10:40"] in lines_in_csv
        assert ["12:00", "14:00", "14:00"] in lines_in_csv
        assert ["14:51", "18:00", "18:00"] in lines_in_csv
        assert ["23:50"] in lines_in_csv

        print("Test #3 passed. Route parsed and wrote to file correctly.")


def test_wrapper():
    crawler = RoutesScrapper(base_url, headers)
    crawler.change_to_latin()

    # План изначально был каков: задаем начальное состояние генератора,
    # получаем один и тот же набор случайных чисел, используем их
    # в качестве индексов из общего списка собранных ссылок,
    # проводим одни и те же манипуляции, получаем предсказуемый результат.

    # Фиаско заключается в том, что метод collect_links_to_crawl() собирает
    # и возвращает множество ссылок. Поэтому даже при конвертации в список
    # элементы находятся в нем при каждом запуске в произвольном порядке.
    # Поэтому предлагается мне поверить, что краулер собирает и проходит 450
    # ссылок без ошибок и проблем.

    # random.seed(5)
    # links = list(crawler.collect_links_to_crawl('/linije/red-voznje', 'option'))
    # indices = [random.randint(0, len(links)) for i in range(10)]
    # lim_links = [links[i] for i in indices]

    test_links = [
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60192/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60314/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/10021/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60243/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60249/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/23/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60260/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/18/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/400/prikaz",
        "https://www.bgprevoz.rs/linije/red-voznje/linija/60271/prikaz",
    ]

    result = crawler.parse_all_routes(direct_links=test_links)
    result_iterator = iter(result)
    first = next(result_iterator)
    assert (
        "Sopot - Sibnica groblje - Mirosaljci - Junkovac" == first.description
    )
    assert "13:20" in first.first_st_dep["Radni dan"]
    assert "14:10" in first.last_st_dep["Radni dan"]

    second = next(result_iterator)
    assert "Beograd - Stojnik" == second.description
    assert "19:25" in second.first_st_dep["Radni dan"]
    assert "17:25" in second.first_st_dep["Subota"]

    third = next(result_iterator)
    assert "Trg Slavija - Učiteljsko naselje" == third.description
    assert "06:01" in third.first_st_dep["Radni dan"]
    assert "06:15" in third.first_st_dep["Subota"]
    assert "23:30" in third.first_st_dep["Nedelja"]
    assert "04:40" in third.last_st_dep["Radni dan"]
    assert "05:15" in third.last_st_dep["Subota"]
    assert "21:22" in third.last_st_dep["Nedelja"]

    fourth = next(result_iterator)
    fifth = next(result_iterator)
    sixth = next(result_iterator)
    seventh = next(result_iterator)
    assert "Beograd - Mladenovac (autoputem)" == seventh.description
    assert "04:45" in seventh.first_st_dep["Radni dan"]
    assert "08:00" in seventh.first_st_dep["Subota"]
    assert "19:50" in seventh.first_st_dep["Nedelja"]
    assert "04:00" in seventh.last_st_dep["Radni dan"]
    assert "19:40" in seventh.last_st_dep["Nedelja"]

    eighth = next(result_iterator)
    nineth = next(result_iterator)
    tenth = next(result_iterator)
    assert "Beograd - Lazarevac (Dom zdravlja)" == tenth.description
    assert "05:30" in tenth.first_st_dep["Radni dan"]
    assert "11:30" in tenth.first_st_dep["Subota"]
    assert "11:30" in tenth.first_st_dep["Nedelja"]
    assert "19:10" in tenth.last_st_dep["Radni dan"]
    assert "13:15" in tenth.last_st_dep["Nedelja"]

    for item in result:
        item.get_route_csv(f"{item.description}.csv")

    generator = os.walk("./")
    csvs = next(generator)[2]
    assert "Sopot - Sibnica groblje - Mirosaljci - Junkovac.csv" in csvs
    assert "Beograd - Mali Popović - Mala Ivanča (autoputem).csv" in csvs
    assert "Sopot (Stanojevac) - Beograd (Autoputem).csv" in csvs
    assert "Karaburma 2 - Vidikovac.csv" in csvs
    assert "Medaković 3 - Zemun Bačka.csv" in csvs
    assert "Voždovac - Vrh Avale.csv" in csvs

    with open(r"Trg Slavija - Učiteljsko naselje.csv", "r") as output:
        reader = csv.reader(output)
        first_string = next(reader)
        assert "Trg Slavija" in first_string
        test_status1 = False
        test_status2 = False
        for string in reader:
            if ["15:38", "22:15", "22:15"] == string:
                test_status1 = True
            elif ["16:13", "23:10", "23:10"] == string:
                test_status2 = True
        assert test_status1 and test_status2

    with open(r"Sopot (Stanojevac) - Beograd (Autoputem).csv", "r") as output:
        reader = csv.reader(output)
        first_string = next(reader)
        assert "Sopot (Stanojevac)" in first_string
        test_status1 = False
        test_status2 = False
        for string in reader:
            if ["06:30", "09:40", "09:40"] == string:
                test_status1 = True
            elif ["22:10"] == string:
                test_status2 = True
        assert test_status1 and test_status2
        print("Test #4 passed. Crawler works.")
