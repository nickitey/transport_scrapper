import csv
import logging

from main import BelgradTrasnportCrawler, MyBSException


class BelgradRoute:
    def __init__(self):
        self.route_name = None
        self.description = None
        self.first_station = None
        self.last_station = None
        self.first_st_dep = None
        self.last_st_dep = None

    def get_dict(self):
        scrapped_data = {
            "route_name": self.route_name,
            "route_description": self.description,
            "first_station": {},
            "last_station": {},
        }
        scrapped_data["first_station"]["name"] = self.first_station
        scrapped_data["first_station"]["departures"] = self.first_st_dep
        scrapped_data["last_station"]["name"] = self.last_station
        scrapped_data["last_station"]["departures"] = self.last_st_dep
        return scrapped_data

    def get_station_csv(self, station, path):
        lower_station = station.lower()
        first_station_lower = self.first_station.lower()
        last_station_lower = self.last_station.lower()
        try:
            assert lower_station in [first_station_lower, last_station_lower]
        except AssertionError:
            err_msg = "This station is not parsed yet or you made a typo."
            raise MyBSException(err_msg)
        if lower_station == first_station_lower:
            proceeded_station = self.first_st_dep
        else:
            proceeded_station = self.last_st_dep
        csv_headers = list(proceeded_station.keys())
        with open(rf"{path}", "w") as output:
            writer = csv.writer(output)
            writer.writerow(csv_headers)
            # Определим самый длинный список времени отправления на маршруте.
            # Возьмем все списки отправлений транспорта из пункта
            departures = list(proceeded_station.values())
            # Отсортируем их по длине
            sorted_departures = sorted(departures, key=lambda lst: len(lst))
            # И возьмем в качестве количества строк длину самого большого
            # списка
            rows_amount = len(sorted_departures[-1])
            # Строка в csv-файле у нас будет состоять из каждого n-ного
            # элемента из каждого дня, для которого у нас есть время
            # отправления
            for i in range(rows_amount):
                dep_list = []
                for key in proceeded_station:
                    try:
                        dep_list.append(proceeded_station[key][i])
                    # Возникновение здесь ошибки IndexError обусловлено тем,
                    # что у нас могут быть столбцы разной величины. Очевидно,
                    # что в столбце отправлений транспорта в рабочие дни,
                    # будет больше значений, потому что транспорт ходит чаще,
                    # чем в выходные.
                    except IndexError:
                        continue
                writer.writerow(dep_list)


class RoutesScrapper(BelgradTrasnportCrawler):
    def __init__(self, host, headers):
        super().__init__(host, headers)

    def __get_schedule__(self, table_obj):

        def save_from_empty(string):
            newstring = string.strip()
            if newstring == "":
                return None
            return newstring

        # Для визуального удобства в заголовке таблицы первый и последний
        # столбцы - это часы отправления, но нам они здесь не нужны.
        table_head_cells = table_obj.thead.find_all("th")[1:-1]
        # Поскольку у нас будет древовидная структура расписания,
        # отправления будут разбиты по дням недели, каждому дню недели
        # будет соответствовать список времени отправления.
        departure_days = {tag.text.strip(): [] for tag in table_head_cells}
        # Отдельно подготовим список ключей-дней недели, чтобы можно
        # было обращаться к ним по индексам.
        departure_keys = list(departure_days.keys())
        # Тело таблицы - это совокупность строк с минутами отправления.
        # Соберем эти строки, отсеяв лишние переносы между тегами
        table_body = [
            tag for tag in table_obj.tbody.find_all("tr") if tag.text != "\n"
        ]
        # Для того, чтобы в нештатной ситуации у нас было понимание,
        # с какой строкой таблицы возникла проблема, введем счетчик строк
        table_row_count = 1
        for tr_tag in table_body:
            # Каждая строка таблицы - это тег <tr>, совокупность ячеек -
            # тегов <td>. Но BS объект, хоть и итерируемый, но все же
            # неиндексируемый, поэтому превратим каждую строку
            # из совокупности ячеек во вполне конкретный список, заодно
            # убрав ячейку со служебной информацией (с атрибутом colspan)

            # Как красиво это задумывалось
            """
            td_tags = [
                td_tag
                for td_tag in tr_tag
                #if td_tag.text != "\n" and
                if "colspan" not in td_tag.attrs
            ]"""

            # И как в итоге это получилось

            td_tags = []
            for td_tag in tr_tag:
                try:
                    if "colspan" not in td_tag.attrs:
                        continue
                except AttributeError:
                    continue
                td_tags.append(td_tag)

            # Практического смысла в отдельной переменной для range
            # никакого. Просто если дальше его вставлять в генератор
            # списка, то длина строки превысит численность Индии.
            range_generator = range(1, len(td_tags) - 1)
            # У нас есть совокупность ячеек: первая и последняя ячейки
            # в строке - это час (поэтому range у нас от второго до
            # предпоследнего элемента), между ними - строка с минутами
            # в формате "ММ ММ ММ". Между этими минутами произвольное
            # количество пробелов, знаков переноса строки, и все это
            # по-хорошему надо убрать.
            # Со стороны может показаться, что количество вызовов метода
            # strip() какое-то запредельное, но одним только фронтендерам
            # известно, сколько в результате в верстке оказалось лишних
            # пробелов, табуляций и переносов строки.

            # Как красиво это задумывалось
            """
            departure_minutes = [
                list(
                    map(
                        # Сэкономим немножко времени, добавим час
                        # отправления из первого столбца к каждому
                        # значению минут.
                        lambda x: td_tags[0].text + ":" + save_from_empty(x),
                        td_tags[i].text.strip().split("\n"),
                    )
                )
                for i in range_generator
            ]
            """

            # И как в итоге это получилось
            departure_minutes = []
            for i in range_generator:
                splittes_minutes = td_tags[i].text.strip().split("\n")
                if len(splittes_minutes) == 0:
                    departure_minutes.append(None)
                    continue
                for y in range(len(splittes_minutes)):
                    proc_minutes = save_from_empty(splittes_minutes[y])
                    if proc_minutes is not None:
                        splittes_minutes[y] = (
                            td_tags[0].text + ":" + proc_minutes
                        )
                    else:
                        splittes_minutes[y] = None
                departure_minutes.append(splittes_minutes)
            # В результате мы получили список списков, где каждый список
            # соответствует столбцу из заголовка.
            # Проверка, что все прошло успешно - утверждение, что длина
            # списков времени отправления равна списку заголовков таблицы
            try:
                assert len(departure_minutes) == len(departure_days)
            except AssertionError:
                # В результате всех очисток может получиться пустой список
                # Зато в браузере, наверное, красиво выглядит.
                if len(departure_minutes) == 0:
                    continue
                else:
                    err_msg = (
                        "Table row length doesn't match table "
                        f"headers length. Problem with "
                        f"#{table_row_count} row, here it is: "
                        f"{departure_minutes}"
                    )
                    raise MyBSException(err_msg)
            # Соберем теперь все получившиеся данные в один объект.
            for i in range(len(departure_keys)):
                schedule_day = departure_keys[i]
                departure_days[schedule_day].extend(departure_minutes[i])
            table_row_count += 1
        return departure_days

    def parse_route(self, link):
        route = BelgradRoute()
        soup = self.get_bs_object(path=link)
        route_name = soup.h1.get_text(strip=True)
        h2_headers = soup.find_all("h2")
        if len(h2_headers) == 2:
            description, first_station = map(
                lambda tag: tag.get_text(strip=True), h2_headers
            )

        else:
            description, first_station, dbl_description, last_station = map(
                lambda tag: tag.get_text(strip=True), h2_headers
            )
            route.last_station = last_station

        route.route_name = route_name
        route.description = description
        route.first_station = first_station

        # На странице находятся две таблицы: по одной со временем отправления
        # из каждой конечной точки. Получим эти две таблицы, чтобы было удобно
        # с ними работать, и каждую таблицу передадим в функцию.
        schedule_tables = soup.find_all("table")
        if len(schedule_tables) == 1:
            table = schedule_tables[0]
            route.first_st_dep = self.__get_schedule__(table)
        else:
            table_first, table_last = soup.find_all("table")
            route.first_st_dep = self.__get_schedule__(table_first)
            route.last_st_dep = self.__get_schedule__(table_last)
        return route

    def parse_all_routes(self, path, clear_from_pdf):
        links_to_crawl = self.collect_links_to_crawl(
            path, "option", clear_from_pdf=clear_from_pdf
        )
        parsed_objects = []
        counter = len(links_to_crawl)
        for link in links_to_crawl:
            print(f"Перехожу к ссылке {link}. Осталось {counter - 1} ссылок.")
            try:
                parsed_objects.append(self.parse_route(link))
            except Exception as e:
                msg = f"Problem with link {link}. "
                raise MyBSException(msg + str(e))
            finally:
                counter -= 1
        return parsed_objects
