import csv
import logging
import os
import sys

sys.path.insert(1, "../serbian_lines_scrapper")

from serbian_lines_scrapper.main import BelgradTrasnportCrawler
from serbian_lines_scrapper.routes_scrapper import BelgradRoute, RoutesScrapper

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
    # 'host': "www.example.com"
}

external_base_url = "https://www.bgprevoz.rs/"
local_base_url = "http://127.0.0.1:5000/"

if os.getcwd().endswith("tests"):
    base_path = "./"
else:
    base_path = "./tests/"


static_route_example = f"{local_base_url}linije/red-voznje/linija/2/prikaz"

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
    f"{local_base_url}linije/red-voznje/linija/60192/prikaz",
    f"{local_base_url}linije/red-voznje/linija/60314/prikaz",
    f"{local_base_url}linije/red-voznje/linija/10021/prikaz",
    f"{local_base_url}linije/red-voznje/linija/60243/prikaz",
    f"{local_base_url}linije/red-voznje/linija/60249/prikaz",
    f"{local_base_url}linije/red-voznje/linija/23/prikaz",
    f"{local_base_url}linije/red-voznje/linija/60260/prikaz",
    f"{local_base_url}linije/red-voznje/linija/18/prikaz",
    f"{local_base_url}linije/red-voznje/linija/400/prikaz",
    f"{local_base_url}linije/red-voznje/linija/60271/prikaz",
]

test_counter = 0


def get_iterator_state(iterator, index):
    i = -1
    while i < index:
        cur = next(iterator)
        i += 1
    return cur


def test_full_links_collector():
    start_path = "/linije/red-voznje"
    with open(rf"{base_path}test_pdf_routes.txt", "r") as pdf_list:
        pdf_routes = set(pdf_list.read().split("\n"))
    with open(rf"{base_path}test_html_routes.txt", "r") as links_list:
        clean_routes = set(links_list.read().split("\n"))

    whole_test_routes = {*pdf_routes, *clean_routes}
    crawler = BelgradTrasnportCrawler(local_base_url, headers=headers)

    dirty_links = crawler.collect_links_to_crawl(
        start_path, "option", clear_from_pdf=False
    )
    assert dirty_links == whole_test_routes

    global test_counter
    test_counter += 1
    print(f"Test #{test_counter} passed. All links are collected correctly.")


def test_pdfless_links_collector():
    start_path = "/linije/red-voznje"
    with open(rf"{base_path}test_html_routes.txt", "r") as links_list:
        clean_routes = set(links_list.read().split("\n"))
    crawler = BelgradTrasnportCrawler(local_base_url, headers=headers)
    clean_links = crawler.collect_links_to_crawl(
        start_path, "option", clear_from_pdf=True
    )
    assert clean_links == clean_routes

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Links without *.pdf are collected "
        "correctly."
    )


def test_getting_class_instance():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    assert isinstance(parsed_route, BelgradRoute)

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Route is instance of BelgradRoute "
        "class."
    )


def test_route_name_attribute():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    assert parsed_route.route_name == "Red vožnje linija 2"

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Route's name is correct in class "
        "instance."
    )


def test_first_station_attribute():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    assert parsed_route.first_station == "Unutrašnji Krug"

    global test_counter
    test_counter += 1
    print(f"Test #{test_counter} passed. First station in route is correct.")


def test_last_station_attribute():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    assert parsed_route.last_station == "Spoljašnji Krug"

    global test_counter
    test_counter += 1
    print(f"Test #{test_counter} passed. Last station in route is correct.")


def test_route_dict_headers():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    route_dict = parsed_route.get_dict()
    assert (
        "Radni dan" in route_dict["first_station"]["departures"]
        and "Subota" in route_dict["last_station"]["departures"]
        and "Nedelja" in route_dict["first_station"]["departures"]
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Headers in station schedule dict "
        "are correct."
    )


def test_daily_departure_time():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    route_dict = parsed_route.get_dict()
    daily_departures = route_dict["first_station"]["departures"]["Nedelja"]
    morning_dep_example = "04:10"
    afternoon_dep_example = "17:07"
    night_dep_example = "23:10"
    assert (
        morning_dep_example in daily_departures
        and afternoon_dep_example in daily_departures
        and night_dep_example in daily_departures
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Daily schedule is scrapped correctly."
    )


def test_saturday_weekly_departure_time():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    route_dict = parsed_route.get_dict()
    saturday_departures = route_dict["first_station"]["departures"]["Subota"]
    morning_dep_example = "04:35"
    afternoon_dep_example = "15:20"
    night_dep_example = "22:04"
    assert "07:20" in saturday_departures
    assert (
        morning_dep_example in saturday_departures
        and afternoon_dep_example in saturday_departures
        and night_dep_example in saturday_departures
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Saturday schedule is scrapped "
        "correctly."
    )


def test_sunday_weekly_departure_time():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    route_dict = parsed_route.get_dict()
    sunday_departures = route_dict["first_station"]["departures"]["Nedelja"]
    morning_dep_example = "04:55"
    afternoon_dep_example = "13:34"
    night_dep_example = "23:50"
    assert (
        morning_dep_example in sunday_departures
        and afternoon_dep_example in sunday_departures
        and night_dep_example in sunday_departures
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Sunday schedule is scrapped correctly."
    )


def test_csv_schedule_table():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    parsed_route.get_station_csv(
        "Spoljašnji Krug", f"{base_path}test_station.csv"
    )

    with open(f"{base_path}test_station.csv", "r") as r:
        reader = csv.reader(r)
        schedule_table_header = next(reader)
        assert ["Spoljašnji Krug"] == schedule_table_header

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Schedule table header is written "
        "to csv correctly."
    )
    os.remove(f"{base_path}test_station.csv")


def test_csv_schedule_days():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    parsed_route.get_station_csv(
        "Spoljašnji Krug", f"{base_path}test_station.csv"
    )

    with open(f"{base_path}test_station.csv", "r") as r:
        reader = csv.reader(r)
        schedule_days_string = get_iterator_state(reader, 2)
        assert ["Radni dan", "Subota", "Nedelja"] == schedule_days_string

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Schedule days is written "
        "to csv correctly."
    )
    os.remove(f"{base_path}test_station.csv")


def test_csv_morning_schedule():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    parsed_route.get_station_csv(
        "Spoljašnji Krug", f"{base_path}test_station.csv"
    )

    with open(f"{base_path}test_station.csv", "r") as r:
        reader = csv.reader(r)
        morning_schedule_string = get_iterator_state(reader, 6)
        assert morning_schedule_string == ["05:10", "05:15", "05:15"]

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Morning schedule is written "
        "to csv correctly."
    )
    os.remove(f"{base_path}test_station.csv")


def test_csv_afternoon_schedule():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    parsed_route.get_station_csv(
        "Spoljašnji Krug", f"{base_path}test_station.csv"
    )

    with open(f"{base_path}test_station.csv", "r") as r:
        reader = csv.reader(r)
        afternoon_schedule = get_iterator_state(reader, 66)
        assert afternoon_schedule == ["15:18", "18:40", "18:40"]

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Afternoon schedule is written "
        "to csv correctly."
    )
    os.remove(f"{base_path}test_station.csv")


def test_csv_night_schedule():
    scrapper = RoutesScrapper(local_base_url, headers)

    parsed_route = scrapper.parse_route(static_route_example)
    parsed_route.get_station_csv(
        "Spoljašnji Krug", f"{base_path}test_station.csv"
    )

    with open(f"{base_path}test_station.csv", "r") as r:
        reader = csv.reader(r)
        night_schedule = get_iterator_state(reader, 108)
        assert night_schedule == ["23:50"]

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Night schedule is written "
        "to csv correctly."
    )
    os.remove(f"{base_path}test_station.csv")


def test_first_element_in_crawler_result():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    result_iterator = iter(result)
    first = next(result_iterator)
    assert (
        "Sopot - Sibnica groblje - Mirosaljci - Junkovac" == first.description
        and "13:20" in first.first_st_dep["Radni dan"]
        and "14:10" in first.last_st_dep["Radni dan"]
    )
    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. First route of ten links is scrapped "
        "correctly."
    )


def test_second_element_in_crawler_result():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    result_iterator = iter(result)
    second = get_iterator_state(result_iterator, 1)
    assert (
        "Beograd - Stojnik" == second.description
        and "19:25" in second.first_st_dep["Radni dan"]
        and "17:25" in second.first_st_dep["Subota"]
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Second route of ten links is scrapped "
        "correctly."
    )


def test_seventh_element_in_crawler_result():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    result_iterator = iter(result)
    seventh = get_iterator_state(result_iterator, 6)
    assert (
        "Beograd - Mladenovac (autoputem)" == seventh.description
        and "04:45" in seventh.first_st_dep["Radni dan"]
        and "08:00" in seventh.first_st_dep["Subota"]
        and "19:50" in seventh.first_st_dep["Nedelja"]
        and "04:00" in seventh.last_st_dep["Radni dan"]
        and "19:40" in seventh.last_st_dep["Nedelja"]
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Seventh route of ten links is scrapped "
        "correctly."
    )


def test_tenth_element_in_crawler_result():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    result_iterator = iter(result)
    tenth = get_iterator_state(result_iterator, 9)
    assert (
        "Beograd - Lazarevac (Dom zdravlja)" == tenth.description
        and "05:30" in tenth.first_st_dep["Radni dan"]
        and "11:30" in tenth.first_st_dep["Subota"]
        and "11:30" in tenth.first_st_dep["Nedelja"]
        and "19:10" in tenth.last_st_dep["Radni dan"]
        and "13:15" in tenth.last_st_dep["Nedelja"]
    )

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Tenth route of ten links is scrapped "
        "correctly."
    )


def test_fourth_route_csv_table():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    fourth_route = result[3]
    fourth_route.get_route_csv(f"{base_path}{fourth_route.description}.csv")

    file_system = os.walk(base_path)
    csvs = next(file_system)[2]
    assert "Beograd - Mali Popović - Mala Ivanča (autoputem).csv" in csvs

    global test_counter
    test_counter += 1
    print(f"Test #{test_counter} passed. There is csv-table of fourth route.")
    os.remove(f"{base_path}{fourth_route.description}.csv")


def test_fifth_route_csv_table():
    crawler = RoutesScrapper(local_base_url, headers)

    result = crawler.parse_all_routes(direct_links=test_links)
    fifth_route = result[4]
    fifth_route.get_route_csv(f"{base_path}{fifth_route.description}.csv")

    with open(f"{base_path}{fifth_route.description}.csv", "r") as output:
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

    global test_counter
    test_counter += 1
    print(
        f"Test #{test_counter} passed. Fifth route is successfully written"
        " to csv."
    )
    os.remove(f"{base_path}{fifth_route.description}.csv")
