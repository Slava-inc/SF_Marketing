import sys
# Для считывания PDF
import PyPDF2
# Для анализа структуры PDF и извлечения текста
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure
# Для извлечения текста из таблиц в PDF
import pdfplumber
# Для извлечения изображений из PDF
from PIL import Image
from pdf2image import convert_from_path
# Для выполнения OCR, чтобы извлекать тексты из изображений
import pytesseract
# Для удаления дополнительно созданных файлов
import os
# Добавляем пути к исполняемым файлам tesseract.exe в переменные окружения

if sys.platform == 'win32':
    sep = ';'
else:
    sep = ':'

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
os.environ['PATH'] += sep + r'C:\Users\Rossvik\PycharmProjects\SFMarketing\bin'

class GetTextOCR:
    def __init__(self, kind_content: str = 'Весь контент страницы'):
        self.kind_content = kind_content

    # Создаём функцию для извлечения текста
    @staticmethod
    def text_extraction(element):
        # Извлекаем текст из вложенного текстового элемента
        line_text = element.get_text()

        # Находим форматы текста
        # Инициализируем список со всеми форматами, встречающимися в строке текста
        line_formats = []
        for text_line in element:
            if isinstance(text_line, LTTextContainer):
                # Итеративно обходим каждый символ в строке текста
                for character in text_line:
                    if isinstance(character, LTChar):
                        # Добавляем к символу название шрифта
                        line_formats.append(character.fontname)
                        # Добавляем к символу размер шрифта
                        line_formats.append(character.size)
        # Находим уникальные размеры и названия шрифтов в строке
        format_per_line = list(set(line_formats))
        # Возвращаем кортеж с текстом в каждой строке вместе с его форматом
        return line_text, format_per_line

    # Создаём функцию для вырезания элементов изображений из PDF
    @staticmethod
    def crop_image(element, page_obj):
        # Получаем координаты для вырезания изображения из PDF
        [image_left, image_top, image_right, image_bottom] = [element.x0,element.y0,element.x1,element.y1]
        # Обрезаем страницу по координатам (left, bottom, right, top)
        page_obj.mediabox.lower_left = (image_left, image_bottom)
        page_obj.mediabox.upper_right = (image_right, image_top)
        # Сохраняем обрезанную страницу в новый PDF
        cropped_pdf_writer = PyPDF2.PdfWriter()
        cropped_pdf_writer.add_page(page_obj)
        # Сохраняем обрезанный PDF в новый файл
        with open('cropped_image.pdf', 'wb') as cropped_pdf_file:
            cropped_pdf_writer.write(cropped_pdf_file)

    # Создаём функцию для преобразования PDF в изображения
    @staticmethod
    def convert_to_images(input_file,):
        images = convert_from_path(input_file)
        image = images[0]
        output_file = "PDF_image.png"
        image.save(output_file, "PNG")

    # Создаём функцию для считывания текста из изображений
    @staticmethod
    def image_to_text(image_path):
        # Считываем изображение
        img = Image.open(image_path)
        # Извлекаем текст из изображения
        text = pytesseract.image_to_string(img)
        return text

    # Извлечение таблиц из страницы
    @staticmethod
    def extract_table(pdf_path, page_num, table_num):
        # Открываем файл pdf
        pdf = pdfplumber.open(pdf_path)
        # Находим исследуемую страницу
        table_page = pdf.pages[page_num]
        # Извлекаем соответствующую таблицу
        table = table_page.extract_tables()[table_num]
        return table

    # Преобразуем таблицу в соответствующий формат
    @staticmethod
    def table_converter(table):
        table_string = ''
        # Итеративно обходим каждую строку в таблице
        for row_num in range(len(table)):
            row = table[row_num]
            # Удаляем разрыв строки из текста с переносом
            cleaned_row = [item.replace('\n', ' ') if item is not None and '\n' in item else 'None' if item is None else item for item in row]
            # Преобразуем таблицу в строку
            table_string+=('|'+'|'.join(cleaned_row)+'|'+'\n')
        # Удаляем последний разрыв строки
        table_string = table_string[:-1]
        return table_string

    # Функция замены символов в строке
    @staticmethod
    def change_char(text: str, char: str, new_char: str) -> str:
        return new_char.join(text.split(char))

    # Анализируем файл PDF и вытаскиваем текст из разных форматов в список
    def processing_pdf(self, path_pdf: str):
        # Находим путь к PDF
        pdf_path = path_pdf
        # создаём объект файла PDF
        pdf_file_obj = open(pdf_path, 'rb')
        # создаём объект считывателя PDF
        pdf_reader = PyPDF2.PdfReader(pdf_file_obj)
        # Создаём словарь для извлечения текста из каждого изображения
        text_per_page = {}
        # Извлекаем страницы из PDF
        for page_num, page in enumerate(extract_pages(pdf_path)):
            # Инициализируем переменные, необходимые для извлечения текста со страницы
            page_obj = pdf_reader.pages[page_num]
            page_text = []
            line_format = []
            text_from_images = []
            text_from_tables = []
            page_content = []
            # Инициализируем количество исследованных таблиц
            table_num = 0
            first_element = True
            table_extraction_flag = False
            # Открываем файл pdf
            pdf = pdfplumber.open(pdf_path)
            # Находим исследуемую страницу
            page_tables = pdf.pages[page_num]
            # Находим количество таблиц на странице
            tables = page_tables.find_tables()
            # Находим все элементы
            page_elements = [(element.y1, element) for element in page._objs]
            # Сортируем все элементы по порядку нахождения на странице
            page_elements.sort(key=lambda a: a[0], reverse=True)
            # Находим элементы, составляющие страницу
            for i, component in enumerate(page_elements):
                # Извлекаем положение верхнего края элемента в PDF
                pos = component[0]
                # Извлекаем элемент структуры страницы
                element = component[1]

                # Проверяем, является ли элемент текстовым
                if isinstance(element, LTTextContainer):
                    # Проверяем, находится ли текст в таблице
                    if not table_extraction_flag:
                        # Используем функцию извлечения текста и формата для каждого текстового элемента
                        (line_text, format_per_line) = self.text_extraction(element)
                        # Добавляем текст каждой строки к тексту страницы
                        page_text.append(line_text)
                        # Добавляем формат каждой строки, содержащей текст
                        line_format.append(format_per_line)
                        page_content.append(line_text)
                    else:
                        # Пропускаем текст, находящийся в таблице
                        pass

                # Проверяем элементы на наличие изображений
                if isinstance(element, LTFigure):
                    # Вырезаем изображение из PDF
                    self.crop_image(element, page_obj)
                    # Преобразуем обрезанный pdf в изображение
                    self.convert_to_images('cropped_image.pdf')
                    # Извлекаем текст из изображения
                    image_text = self.image_to_text('PDF_image.png')
                    text_from_images.append(image_text)
                    page_content.append(image_text)
                    # Добавляем условное обозначение в списки текста и формата
                    page_text.append('image')
                    line_format.append('image')

                # Проверяем элементы на наличие таблиц
                if isinstance(element, LTRect):
                    # Если первый прямоугольный элемент
                    if first_element == True and (table_num + 1) <= len(tables):
                        # Находим ограничивающий прямоугольник таблицы
                        lower_side = page.bbox[3] - tables[table_num].bbox[3]
                        upper_side = element.y1
                        # Извлекаем информацию из таблицы
                        table = self.extract_table(pdf_path, page_num, table_num)
                        # Преобразуем информацию таблицы в формат структурированной строки
                        table_string = self.table_converter(table)
                        # Добавляем строку таблицы в список
                        text_from_tables.append(table_string)
                        page_content.append(table_string)
                        # Устанавливаем флаг True, чтобы избежать повторения содержимого
                        table_extraction_flag = True
                        # Преобразуем в другой элемент
                        first_element = False
                        # Добавляем условное обозначение в списки текста и формата
                        page_text.append('table')
                        line_format.append('table')
                    else:
                        lower_side = 0
                        upper_side = 0
                    # Проверяем, извлекли ли мы уже таблицы из этой страницы
                    if element.y0 >= lower_side and element.y1 <= upper_side:
                        pass
                    elif not isinstance(page_elements[i + 1][1], LTRect):
                        table_extraction_flag = False
                        first_element = True
                        table_num += 1

            # Создаём ключ для словаря
            dct_key = 'Page_' + str(page_num)
            # Добавляем список списков как значение ключа страницы
            text_per_page[dct_key] = {'Текст страницы': page_text, 'Форматы текста': line_format,
                                      'Текст из изображения': text_from_images, 'Текст из таблицы': text_from_tables,
                                      'Весь контент страницы': page_content}

        # Закрываем объект файла pdf
        pdf_file_obj.close()

        # Удаляем созданные дополнительные файлы
        os.remove('cropped_image.pdf')
        os.remove('PDF_image.png')
        # Удаляем содержимое страницы
        return text_per_page['Page_0'][self.kind_content]

    # Находим нужный текст в платежке банка Тинькофф и записываем в словарь
    def outlay_dict_tinkoff(self, result: list) -> dict:
        dict_text_pdf = {}
        i = 1
        for item in result:
            if i == 2:
                dict_text_pdf['Наименование банка'] = self.change_char(item, '\n', ' ').split(' ХУТОРСКАЯ')[0]
            elif i == 3:
                dict_text_pdf['Номер и дата п/п:'] = self.change_char(item, '\n', ' ').split('Исх. № ')[1]
            elif i == 4:
                dict_text_pdf['Плательщик:'] = self.change_char(item, '\n', ' ').split('которой является ')[1]
            elif i == 4:
                dict_text_pdf['Дата и время операции:'] = self.change_char(item, '\n', ' ')
            elif i == 11:
                dict_text_pdf['Сумма в валюте операции:'] = self.change_char(item, '\n', ' ')
            elif i == 12:
                dict_text_pdf['Информация о получателе средств:'] = self.change_char(item, '\n', ' ')
            i += 1
        return dict_text_pdf

    # Находим нужный текст в приходе банка Тинькофф и записываем в словарь
    def receipt_dict_tinkoff(self, result: list) -> dict:
        dict_text_pdf = {}
        i = 1
        for item in result:
            if i == 2:
                dict_text_pdf['Номер и дата п/п:'] = self.change_char(item, '\n', ' ')
            elif i == 4:
                dict_text_pdf['Сумма:'] = self.change_char(item, '\n', ' ').split(' i')[0]
            i += 1
        return dict_text_pdf

    # Определяем какой документ пришел из банка Тинькофф и записываем текст словарь
    def get_tinkoff(self, result: list):
        if 'АО «ТБАНК»' in result[1]:
            dict_tinkoff = self.outlay_dict_tinkoff(result)
        else:
            dict_tinkoff = self.receipt_dict_tinkoff(result)
        return dict_tinkoff

    def get_text_file(self, path_file: str):
        if path_file.split('.')[-1] == 'pdf':
            result = self.processing_pdf(path_file)
        elif path_file.split('.')[-1] == 'jpg':
            result = ' '.join(self.image_to_text(path_file).split())
        else:
            result = None
        return result

my_ocr = GetTextOCR()
dict_text = my_ocr.get_text_file('operation_statement_04.10.2024 (3).pdf')
dict_tinkoff = my_ocr.get_tinkoff(dict_text)
# for key, item in dict_text.items():
#     print(f'{key} {item}')
print(dict_tinkoff)
