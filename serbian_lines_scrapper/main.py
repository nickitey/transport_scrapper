import urllib.parse

import requests
from bs4 import BeautifulSoup as bs


class MyBSException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class BelgradTrasnportCrawler(requests.Session):
    def __init__(self, host, headers=None):
        super().__init__()
        self.max_redirects = 5
        self.timeout = 5.0
        self.locale_change_url = "https://www.bgprevoz.rs/locale/change"
        self.headers = headers
        self.host = host

    def make_request(self, http_method, path, parse_json=False, **kwargs):
        if path.startswith("http"):
            url = path
        else:
            url = urllib.parse.urljoin(self.host, path)
        try:
            response = self.request(http_method, url, **kwargs, timeout=self.timeout)
            response.raise_for_status()
            if parse_json:
                return response.json()
            else:
                return response
        except requests.JSONDecodeError as err:
            raise MyBSException(f"Incoming JSON is invalid from char {err.pos}")
        except requests.TooManyRedirects:
            raise MyBSException(f"Too much redirects. Allowed: {self.max_redirects}.")
        except requests.HTTPError as err:
            raise MyBSException(f"HTTPError is occured, and it is {err}")
        except requests.Timeout:
            raise MyBSException(
                f"Timeout error. Request is executed over \
                {self.timeout} seconds."
            )
        except requests.ConnectionError:
            raise MyBSException("Connection is lost, try again later.")
        except requests.RequestException as err:
            raise MyBSException(err)

    def get_csrf_token(self):
        soup = self.get_bs_object(path="/")
        # Предполагаем, что разработчик сайта спрятал где-то в начале мету
        # с токеном
        token_holder = soup.find(True, {"name": "csrf-token"})
        if token_holder is not None:
            return token_holder.attrs.get("content")
        # Если наше предположение оказалось неверным, то поищем что-нибудь
        # похожее в теле страницы. Во всяком случае, если токена нет,
        # функция вернет None
        token_holder2 = soup.find(True, {"name": "_token"})
        if token_holder2 is not None:
            return token_holder2.attrs.get("value")

    def change_to_latin(self):
        self.cookies.clear()
        form = {"latin": "true", "_token": self.get_csrf_token()}
        url = self.locale_change_url
        return self.make_request("POST", url, data=form)

    def change_to_cyrillic(self):
        self.cookies.clear()
        form = {"cyrilic": "true", "_token": self.get_csrf_token()}
        url = self.locale_change_url
        return self.make_request("POST", url, data=form)

    def get_bs_object(
        self, html=None, path=None, method="GET",
        parser="html.parser", **kwargs
    ):
        if (path is None and html is None
                or path is not None and html is not None):
            raise MyBSException(
                "You should pass either path or html "
                "which will be used to prepare your soup."
            )
        if html:
            return bs(html, parser)
        else:
            full_html = self.make_request(method, path, **kwargs)
            if 200 >= full_html.status_code > 300:
                raise MyBSException(
                    "Something wrong with your request. "
                    f"HTTP status code is {full_html.status_code}."
                )
            return bs(full_html.text, parser)
