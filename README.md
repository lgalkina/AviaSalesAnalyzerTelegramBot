# AviaSalesAnalyzerTelegramBot

[Бот-аналитик] (t.me/AviaSalesAnalyzerTelegramBot) цен авиабилетов по данным метапоисковика aviasales.ru.
Предоставляет информацию о ценах на авиабилеты для городов России, используя [API](https://support.travelpayouts.com/hc/ru/articles/203956163-Aviasales-API-%D0%B4%D0%BE%D1%81%D1%82%D1%83%D0%BF%D0%B0-%D0%B)

## Файлы
Файлы исходного кода:

* main.py - основной код обработки запросов к боту
* config.py - файл с натсройка подлючения к Telegram и API, также дополнительные настройки для работы бота
* data_parser.py - основной код для работы с API для извлечения данных об авиабилетах
* dbworker.py - код для работы с SQLite3 (in-memory) для хранения информации о городе отправления пользователя
* exceptions.py - кастомные исключения
* messages.py - сообщения для пользователя

## Команды
Команды для работы с ботом:
* /start - начало работы с ботом, выводит приветственное сообщение с основной информацией о назначении бота
* /info - выводит основную информацию о назначении бота
* /citylist - выводит список городов России, по которым можно получить информацию
* /setsrccity - используется для устновки города отправления для дальнейших запросов, необходимо выполнить команду перед вызовом остальных команд
* /populardestinations - выводит популярные направления из города отправления
* /maxmonthprices - выводит календарь самых высоких цен (top 20) на следующий месяц из города отправления
* /minmonthprices - выводит календарь самых низких цен (top 20) на следующий месяц  из города отправления
* /minpricespermonth - выводит самые низкие цены каждого месяца (следующие 6 месяцев) из города отправления (данные + график), данные за некоторые месяцы могут отсутствовать
* /maxpricespermonth - выводит самые высокие цены каждого месяца (следующие 6 месяцев) из города отправления (данные + график), данные за некоторые месяцы могут отсутствовать


