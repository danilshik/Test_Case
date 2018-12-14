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

ff_driver = "../install/chromedriver.exe"  #Путь до драйвера

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



#Метод определяющий разницу двух многомерных списков
def different_list(list1, list2):
    #list2 > list1
    # diff=[x for x in list1 if x not in [y for y in list2]]
    diff = [x for x in list1 if x[0] not in [y[0] for y in list2]]
    return diff

class Test_Case(unittest.TestCase):
    def setUp(self):
        self.ff = ff_driver
        self.chrome_option = webdriver.ChromeOptions()
        self.chrome_option.add_argument("headless")  #Режим headless
        self.prefs = {
            "profile.managed_default_content_settings.images": 2}  # Настройка, которая отключает загрузку изображений
        self.chrome_option.add_experimental_option("prefs", self.prefs)
        self.driver = webdriver.Chrome(executable_path=self.ff, options=self.chrome_option)
        self.driver.get(url_main)

    # Функция отправки запроса к базе данных
    def query_database(self, sql_query, data, type):
        types = ("insert", "select")
        if type in types:
            try:
                conn = MySQLConnection(user=db_user, password=db_password, host=db_host, database=db_bd)
                conn.autocommit = True
                cursor = conn.cursor()
                try:
                    cursor.execute(sql_query, data)
                    if (type == "insert"):
                        # Возврат идентификатора добавленной строки
                        return cursor.lastrowid
                    elif (type == "select"):
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

    #Парсинг страницы
    def parse_page(self, driver):
        rows = []
        try:
            table = self.driver.find_element_by_id("tbl")
        except NoSuchElementException:
            print("Элемент не найден. Конец программы")
            exit(3)
        # Нахождение записей в таблице на сайте
        tr_list = table.find_elements_by_css_selector('tbody > tr')
        if (len(tr_list) == 0):
            print("Элементы tr не найдены. Конец программы")
            exit(4)
        for tr in tr_list:
            td_list = tr.find_elements_by_css_selector('td')
            if (len(td_list) != 4):
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
        return rows

    # Функция добавления новых товаров на сайт
    def add_new_purchase_site(self, driver, cound_add):
        add_list = []
        for count in range(cound_add):
            try:
                # Кнопка добавление новой записи на сайте
                a_id_open = driver.find_element_by_id("open")
                a_id_open.click()
            except NoSuchElementException:
                print("Элемент не найден. Конец программы")
                exit(7)
            try:
                div_class_new = WebDriverWait(driver, time_waiting_item).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, "#new")))
            except TimeoutException:
                log.info(
                    "Элемент div с id = new не найден. Увеличьте время ожидание появления элемента в переменной time_waiting_item или проверьте разметку. Конец программы")
                exit(8)
            try:
                input_id_name = div_class_new.find_element_by_id("name")
            except NoSuchElementException:
                log.info("Элемент input с id = name не найден. Конец программы")
                exit(9)

            # Вводим случайную строку в поле с длинной строки = 5
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
            try:
                input_id_add = div_class_new.find_element_by_id("add").click()
            except NoSuchElementException:
                log.info("Элемент input с id = add не найден. Конец программы")
                exit(12)
            add_list.append([name, count, price])
            # Очистка Input-ов
            input_id_name.clear()
            input_id_count.clear()
            input_id_price.clear()

        return add_list

    def test_main(self):
        driver = self.driver
        rows_table = self.parse_page(driver)

        # Добавление в базу данных
        for row in rows_table:
            sql_query = "INSERT INTO purchase(name, count, price) VALUES (%s, %s, %s)"
            self.query_database(sql_query, row, "insert")

        list_add_in_table_site = self.add_new_purchase_site(driver, random.randint(3, 10))

        # Получаем записи из БД
        sql_query = "SELECT name, count, price FROM purchase"
        set_in_database = self.query_database(sql_query, None, "select")

        log.info("------------------------Повторный парсинг страницы-----------")
        list_purchase_in_table_site = self.parse_page(driver)
        # print("Добавленный список на сайте:", list_add_in_table_site)
        # print("Список на сайте:", list_purchase_in_table_site)
        # print("Список из базы данных:",set_in_database)
        print("Отсутствуют в базе данных:", different_list(list_purchase_in_table_site, list_add_in_table_site))
        print("Имеются и в базе данных и на сайте", different_list(list_add_in_table_site, list(set_in_database)))

    def test_add_purchase_site(self):
        driver = self.driver
        count_add = random.randint(2, 10)
        #Добавляем N--количество на сайт
        rows_add_purchase_site = self.add_new_purchase_site(driver, count_add)
        # Получаем данные, размещенные на сайте после добавления
        rows_table_site = self.parse_page(driver)
        #Определяем количество добавленных:
        different = len(different_list(rows_table_site, rows_add_purchase_site))

        assert different == 4

    # тест на проверку названий столбцов в верхнем регистре (неудачно)
    def test_check_column_name_table(self):
        driver = self.driver
        try:
            table = driver.find_element_by_id("tbl")
        except NoSuchElementException:
            print("Элемент не найден. Конец программы")
            exit(3)
        # Нахождение названия столбцов
        trs_list_column  = table.find_elements_by_css_selector('thead > tr')
        for tr in trs_list_column:
            #Проверка на соотвествие названий столбцов в верхнем регистре
            assert tr.text.strip().isupper() == True

    # тест на проверку правильность названия в 3 столбце таблицы (неудачно)
    def test_correctness_name_third_column_table(self):
        driver = self.driver
        try:
            table = driver.find_element_by_id("tbl")
        except NoSuchElementException:
            print("Элемент не найден. Конец программы")
            exit(3)
        # Нахождение названия столбцов
        trs_list_column  = table.find_elements_by_css_selector('thead > tr > th')
        assert trs_list_column[2].text.find("стоимость") != -1






    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    start = time.time()
    unittest.main()
    log.info("Время работы: %s", time.time() - start)