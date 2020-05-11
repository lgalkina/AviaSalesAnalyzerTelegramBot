import requests
import config
from exceptions import APIRequestException, ParsingException
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import logging


def get_parser():
    return Parser()


def get_first_days_of_next_months(months=6):
    start_year = datetime.datetime.now().year
    start_month = datetime.datetime.now().month
    end_year = (datetime.datetime.now() + relativedelta(months=months-1)).year
    end_month = (datetime.datetime.now() + relativedelta(months=months-1)).month
    return [datetime.date(int(m / 12), m % 12 + 1, 1)
            for m in range(start_year * 12 + start_month - 1, end_year * 12 + end_month)]


class Parser:

    __cities = None

    # Проверка сущестует ли город в списке
    def do_city_exist(self, city_name):
        if self.__cities is None:
            self.get_city_list()
        return not self.__cities[self.__cities.name == city_name].empty

    # Первые дни каждого месяца с текущего в формате YYYY-MM-DD

    # Запрашиваем список городов
    def get_city_list(self):
        if self.__cities is None:
            params = {
                'token': config.access_token,
                'format': 'json'
            }
            response = requests.get(config.base_url + '/data/ru/cities.json', params=params)
            if response.ok:
                data = pd.DataFrame(response.json())
                if not data.empty:
                    self.__cities = data[['name', 'code', 'country_code']]
                    self.__cities = self.__cities[self.__cities.name.notnull() & (self.__cities.country_code == 'RU')]\
                        .sort_values(by='name')
                return self.__cities
            else:
                raise APIRequestException
        else:
            return self.__cities

    # Популярные направления из города
    def get_popular_destinations(self, city_name):
        if self.__cities is None:
            self.get_city_list()
        city = self.__cities[self.__cities.name == city_name]
        if city.empty:
            raise ParsingException(f'Город {city_name} не найден')
        else:
            city_code = city.code.iloc[0]
            params = {
                'origin': city_code,
                'token': config.access_token,
                'format': 'json'
            }
            response = requests.get(config.base_url + '/v1/city-directions', params=params)
            if response.ok:
                data = pd.DataFrame(response.json()['data'])
                if not data.empty:
                    data = data.transpose()[['destination', 'transfers', 'price']]
                    # удаляем города, которые не в России, и заменяем код на название
                    data = data[data.destination.isin(self.__cities.code)]
                    data.destination = data.destination.map(self.__cities.set_index('code').name)
                return data
            else:
                raise APIRequestException

    # Календарь цен на следующий месяц
    # month - первый день месяца, в формате «YYYY-MM-DD». По умолчанию API использует месяц, следующий за текущим.
    def get_month_prices(self, src_city_name, dest_city_name, is_min=False, top=20, month_first_day=None):
        if self.__cities is None:
            self.get_city_list()
        src_city = self.__cities[self.__cities.name == src_city_name]
        if src_city.empty:
            raise ParsingException(f'Город {src_city_name} не найден')
        else:
            dest_city = self.__cities[self.__cities.name == dest_city_name]
            if dest_city.empty:
                raise ParsingException(f'Город {dest_city_name} не найден')
            else:
                src_city_code = src_city.code.iloc[0]
                dest_city_code = dest_city.code.iloc[0]
                params = {
                    'origin': src_city_code,
                    'destination': dest_city_code,
                    'show_to_affiliates': 'false',
                    'month': month_first_day,
                    'token': config.access_token,
                    'format': 'json'
                }
            response = requests.get(config.base_url + '/v2/prices/month-matrix', params=params)
            if response.ok:
                data = pd.DataFrame(response
                                    .json()['data'])
                if not data.empty:
                    data = data[['depart_date', 'number_of_changes', 'value', 'distance', 'actual']]
                    # оставляем только актуальные предложения, сортируем по цене и оставляем только top записей
                    data = data[data.actual == True].sort_values(by='value', ascending=is_min).head(top)
                    data = data.drop(columns=['actual'])
                return data
            else:
                raise APIRequestException

    # Цены по месяцам (следующие 6 месяцев, включая текущий)
    # Если данных нет, исключаем месяц
    def get_prices_per_month(self, src_city_name, dest_city_name, is_min=False):
        prices_per_month = {}
        month_first_days = get_first_days_of_next_months()
        for month_first_day in month_first_days:
            result = self.get_month_prices(src_city_name, dest_city_name, is_min,
                                           1, month_first_day.strftime("%Y-%m-%d"))
            month_name = month_first_day.strftime("%b")
            if not result.empty:
                prices_per_month[month_name] = result.value.iloc[0]
            else:
                logging.warning(f'Данных о минимальной цене за {month_first_day} нет, этот месяц будет пропущен')
        return prices_per_month
