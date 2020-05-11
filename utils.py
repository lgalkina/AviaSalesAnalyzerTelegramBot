from tabulate import tabulate
import matplotlib.pyplot as plt
import io


# Формирование строки дл вывода списка городов
def pretty_print_city_list(cities):
    return ', '.join([e +'\n' if i%3 == 4 else e for i, e in enumerate(list(cities.name))]).replace('\n,', ',\n')


# Формирование строки дл вывода данных о популярных направлениях
def pretty_print_popular_destinations(data):
    return tabulate(data, showindex=False, headers=['Направление', 'Пересадки', 'Цена (руб.)'],
                    tablefmt='pipe', stralign='center')


# Формирование строки дл вывода данных о ценах за месяц
def pretty_print_month_prices(data):
    return tabulate(data, showindex=False, headers=['Дата', 'Пересадки', 'Цена (руб.)', 'Расст.'],
                    tablefmt='pipe', stralign='center')


# Формирование строки дл вывода данных о ценах по месяцам
def pretty_print_prices_per_month(data):
    return tabulate(data.items(), showindex=False, headers=['Месяц', 'Цена (руб.)'],
                    tablefmt='pipe', stralign='center')


def wrap_pre(text):
    return '<pre>' + text + '</pre>'


# отрисовка цен по месяцам, data - dictionary
def build_prices_per_month_bar(data, title):
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.set_title(title)
    ax.set_xlabel('Месяц', fontsize=12)
    ax.set_ylabel('Цена (руб.)', fontsize=12)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.xaxis.set_tick_params(width=0.2)
    ax.yaxis.set_tick_params(width=0.2)
    ax.spines['bottom'].set_linewidth(0.2)
    ax.spines['left'].set_linewidth(0.2)
    plt.bar(range(len(data)), list(data.values()), align='center')
    plt.xticks(range(len(data)), list(data.keys()))
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

