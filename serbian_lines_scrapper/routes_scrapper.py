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


class RoutesScrapper(BelgradTrasnportCrawler):
    def __init__(self, host, headers):
        super().__init__(host, headers)

    def __get_schedule__(self, table_obj):
        # Для визуального удобства в заголовке таблицы первый и последний
        # столбцы - это часы отправления, но нам он здесь не нужны.
        table_head_cells = table_obj.thead.find_all('th')[1:-1]
        # Поскольку у нас будет древовидная структура расписания,
        # отправления будут разбиты по дням недели, каждому дню недели
        # будет соответствовать список времени отправления.
        departure_days = {tag.text.strip(): [] for tag in table_head_cells}
        # Отдельно подготовим список ключей-дней недели, чтобы можно
        # было обращаться к ним по индексам.
        departure_keys = list(departure_days.keys())
        # Тело таблицы - это совокупность строк с минутами отправления.
        # Соберем эти строки, отсеяв лишние переносы между тегами
        table_body = [tag
                      for tag in table_obj.tbody.find_all('tr')
                      if tag.text != '\n']
        # Для того, чтобы в нештатной ситуации у нас было понимание,
        # с какой строкой таблицы возникла проблема, введем счетчик строк
        table_row_count = 1
        for tr_tag in table_body:
            # Каждая строка таблицы - это тег <tr>, совокупность ячеек -
            # тегов <td>. Но BS объект, хоть и итерируемый, но все же
            # неиндексируемый, поэтому превратим каждую строку
            # из совокупности ячеек во вполне конкретный список, заодно
            # убрав ячейку со служебной информацией (с атрибутом colspan)
            td_tags = [td_tag
                       for td_tag in tr_tag
                       if td_tag.text != '\n'
                       and 'colspan' not in td_tag.attrs
                       ]
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
            departure_minutes = [
                list(
                    map(
                        # Сэкономим немножко времени, добавим час
                        # отправления из первого столбца к каждому
                        # значению минут.
                        lambda x: td_tags[0].text + ":" + x.strip(),
                        td_tags[i].text.strip().split('\n')
                    )
                )
                for i in range_generator
            ]

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
                    err_msg = ('Table row length doesn\'t match table '
                               f'headers length. Problem with '
                               f'#{table_row_count} row, here it is: '
                               f'{departure_minutes}')
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
        h2_headers = soup.find_all('h2')
        description, first_station, dbl_description, last_station = (
            map(lambda tag: tag.get_text(strip=True), h2_headers))
        route.route_name = route_name
        route.description = description
        route.first_station = first_station
        route.last_station = last_station

        # На странице находятся две таблицы: по одной со временем отправления
        # из каждой конечной точки. Получим эти две таблицы, чтобы было удобно
        # с ними работать, и каждую таблицу передадим в функцию.
        table_first, table_last = soup.find_all('table')
        route.first_st_dep = self.__get_schedule__(table_first)
        route.last_st_dep = self.__get_schedule__(table_last)
        return route
