import time
import logging
import random
import string
from mysql.connector import MySQLConnection
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.common.exceptions import *
import re
import unittest

db_bd = "test"
db_user = "root"
db_password = ""
db_host = "localhost"

log = logging.getLogger(__name__)
format = '%(asctime)s %(levelname)s:%(message)s'
logging.basicConfig(format=format, level=logging.INFO)

url_main = "http://tereshkova.test.kavichki.com/"
time_waiting_item = 5  #Время ожидание появления элемента


#Функция генерации случайной строки, только ASCII
def random_string(size, type):
    types = ("name", "count", "price")
    if type in types:
        if(type == "name"):
            chars = string.ascii_lowercase
        else:
            chars = string.digits
        return ''.join(random.choice(chars) for _ in range(size))
    else:
        log.info("Вы не правильно указали тип генерируемой строки для. Должно быть name, count или price. Конец программы.")
        exit(8)



#Функция отправки запроса к базе данных
def query_database(sql_query, data, type):
    types = ("insert", "select")
    if type in types:
        try:
            conn = MySQLConnection(user=db_user, password=db_password, host=db_host, database=db_bd)
            conn.autocommit = True
            cursor = conn.cursor()
            try:
                cursor.execute(sql_query, data)
                if(type == "insert"):
                    # Возврат идентификатора добавленной строки
                    return cursor.lastrowid
                elif(type == "select"):
                    # Возврат кортеж значения запроса
                    rows = cursor.fetchall()
                    return rows
            except Exception as e:
                log.info("Ошибка запроса: %s. Конец программы", e)
                exit(6)
            finally:
                cursor.close()
                conn.close()
        except Exception as e:
            log.info("Ошибка подключения к базе данных: %s. Конец программы", e)
            exit(6)

    else:
        log.info("Вы не правильно указали тип SQL - запроса. Должно быть select или insert. Конец программы.")
        exit(5)


#Инициализация driver
def init_driver():
    ff = "../install/chromedriver.exe"
    chrome_option = webdriver.ChromeOptions()
    # chrome_option.add_argument("headless")  #Режим headless
    prefs = {"profile.managed_default_content_settings.images": 2}  #Настройка, которая отключает загрузку изображений
    chrome_option.add_experimental_option("prefs", prefs)
    try:
        return webdriver.Chrome(executable_path=ff, options=chrome_option)
    except SessionNotCreatedException:
        print("Ошибка инициализации браузера. Скорее всего у вас не установлен браузер. Пожалуйста обратитесь к разработчику парсера")

#Парсинг товаров на сайте
def parse(driver):
    rows = []
    try:
        table = driver.find_element_by_id("tbl")
    except NoSuchElementException:
        print("Элемент не найден. Конец программы")
        exit(3)
    #Нахождение записей в таблице на сайте
    tr_list = table.find_elements_by_css_selector('tbody > tr')
    if(len(tr_list) == 0):
        print("Элементы tr не найдены. Конец программы")
        exit(4)
    for tr in tr_list:
        td_list = tr.find_elements_by_css_selector('td')
        if(len(td_list) != 4):
            print("Количество элементов td не соответствует 4. Возможно поменялась разметка. Конец программы")
            exit(5)
        name = td_list[0].text.strip()
        count = td_list[1].text.strip()
        price = td_list[2].text.strip()
        temp = []
        temp.append(name)
        temp.append(count)
        temp.append(price)
        log.info("Товар: %s, количество: %s, цена: %s", name, count, price)

        rows.append(temp)
    print(rows)
    return rows

#Функция добавления новых товаров на сайте
def add_new_purchase_site(driver, cound_add):
    add_list = []
    for count in range(cound_add):
        try:
            #Кнопка добавление новой записи на сайте
            a_id_open = driver.find_element_by_id("open")
            a_id_open.click()
        except NoSuchElementException:
            print("Элемент не найден. Конец программы")
            exit(7)
        try:
            div_class_new = WebDriverWait(driver, time_waiting_item).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#new")))
        except TimeoutException:
            log.info("Элемент div с id = new не найден. Увеличьте время ожидание появления элемента в переменной time_waiting_item или проверьте разметку. Конец программы")
            exit(8)
        try:
            input_id_name = div_class_new.find_element_by_id("name")
        except NoSuchElementException:
            log.info("Элемент input с id = name не найден. Конец программы")
            exit(9)

        #Вводим случайную строку в поле с длинной строки = 5
        name = random_string(5, "name")
        input_id_name.send_keys(name)

        try:
            input_id_count = div_class_new.find_element_by_id("count")
        except NoSuchElementException:
            log.info("Элемент input с id = count не найден. Конец программы")
            exit(10)
        # Вводим случайную строку в поле с длинной строки = 2
        count = random_string(2, "count")
        input_id_count.send_keys(count)

        try:
            input_id_price = div_class_new.find_element_by_id("price")
        except NoSuchElementException:
            log.info("Элемент input с id = price не найден. Конец программы")
            exit(11)
        # Вводим случайную строку в поле с длинной строки = 2
        price = random_string(2, "price")
        input_id_price.send_keys(price)
        time.sleep(5)
        try:
            input_id_add = div_class_new.find_element_by_id("add").click()
        except NoSuchElementException:
            log.info("Элемент input с id = add не найден. Конец программы")
            exit(12)
        add_list.append([name, count, price])
        #Очистка Input-ов
        input_id_name.clear()
        input_id_count.clear()
        input_id_price.clear()

    return add_list

#Метод определяющий разница двух многомерных списков
def different_list(list1, list2):
    #list2 > list1
    # diff=[x for x in list1 if x not in [y for y in list2]]
    diff = [x for x in list1 if x[0] not in [y[0] for y in list2]]
    return diff

def main(url):
    # Проверка на некорретность ссылок
    text_search = re.search("^http", url)
    if (text_search == None):
        log.info("Ссылка %s некорректна. Конец программы", url)
        exit(1)

    log.info("Запуск браузера")
    driver = init_driver()

    log.info("Переход на %s", url)
    try:
        driver.get(url)
    except Exception as e:
        print("Ошибка перехода. Конец программы", e)  # Не отслеживается
        exit(2)

    #Получаем список с сайта
    rows_table = parse(driver)

    # Добавление в базу данных
    for row in rows_table:
        sql_query = "INSERT INTO purchase(name, count, price) VALUES (%s, %s, %s)"
        query_database(sql_query, row, "insert")

    list_add_in_table_site = add_new_purchase_site(driver, 4)

    #Получаем записи из БД
    sql_query = "SELECT name, count, price FROM purchase"
    set_in_database = query_database(sql_query, None, "select")

    log.info("------------------------Повторный парсинг страницы-----------")
    list_purchase_in_table_site = parse(driver)
    print(list_add_in_table_site)
    print(list_purchase_in_table_site)
    print(set_in_database)
    print("Отсутствуют в базе данных:", different_list(list_purchase_in_table_site, list_add_in_table_site))
    print("Имеются и в базе данных и на сайте", different_list(list_add_in_table_site, list(set_in_database)))
    time.sleep(1000)
    driver.close()

if __name__ == '__main__':
    start = time.time()
    unittest.main()
    main(url_main)
    log.info("Время работы: %s", time.time() - start)
