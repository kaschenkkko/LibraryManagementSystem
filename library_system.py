import os
import sys
from math import ceil
from typing import List, Optional, Tuple, Union

import pandas as pd
from colorama import Fore, init
from simple_term_menu import TerminalMenu
from terminaltables import SingleTable

init(autoreset=True)  # colorama


class LibraryManagementSystem:
    """В классе реализованы 12 методов:

    - main_menu: Главное меню, со всем функционалом.
    - list_books: Постраничный вывод книг.
    - add_book: Добавление новой книги.
    - delete_book: Удаление книги по ID.
    - search_book_menu: Меню для поиска книг.
    - search_book: Поиск книги по указанному столбцу.
    - update_book_status: Изменение статуса книги по ID.
    - _checking_for_valid_page: Проверяет валидность текущей страницы.
    - _get_input: Получение пользовательского ввода с проверкой.
    - _format_book_table: Получение данных в виде таблицы.
    - _show_menu: Отображение меню с доступными действиями.
    - _exit_application: Выход из приложения.
    """
    COLUMNS_NAME: List[str] = ['ID', 'Title', 'Author', 'Year', 'Status']

    def __init__(self, file_library, page_size):
        self.file_library: str = file_library
        self.page_size: int = page_size

    def main_menu(self) -> None:
        """Главное меню, со всем функционалом."""
        os.system('cls||clear')

        selected_index: int = self._show_menu(
            [
                'Вывести список книг.',
                'Добавить книгу.',
                'Удалить книгу.',
                'Поиск книги.',
                'Изменение статуса книги.',
                'Выйти из приложения.'
            ],
            '«Library Management App»'
        )

        menu_options = {
            0: self.list_books,
            1: self.add_book,
            2: self.delete_book,
            3: self.search_book_menu,
            4: self.update_book_status,
            5: self._exit_application,
        }
        action = menu_options.get(selected_index)
        if action:
            action()

    def list_books(self, current_page: int = 1) -> None:
        """Постраничный вывод книг.

        Args:
            - current_page (int) : Номер текущей страницы.
        """
        df: pd.DataFrame = pd.read_csv(self.file_library)
        cnt_rows: int = df.shape[0]
        last_page: int = max(1, ceil(cnt_rows / self.page_size))

        current_page, error_message = self._checking_for_valid_page(current_page, last_page)
        if error_message:
            print(f'{Fore.RED}{error_message}')

        start_idx: int = (current_page - 1) * self.page_size
        end_idx: int = start_idx + self.page_size

        df_on_current_page: pd.DataFrame = df.iloc[start_idx:end_idx]
        df_to_list: List[List] = [self.COLUMNS_NAME] + df_on_current_page.values.tolist()

        table_with_books: str = self._format_book_table(
            data_table=df_to_list,
            title=f'Вы находитесь на странице «{current_page}/{last_page}»'
        )

        print(table_with_books)

        selected_index: int = self._show_menu(
            [
                'Перейти на следующую страницу.',
                'Перейти на предыдущую страницу.',
                'Выход в главное меню.'
            ],
            '«List books»'
        )

        menu_options = {
            0: lambda: (os.system('cls||clear'), self.list_books(current_page + 1)),
            1: lambda: (os.system('cls||clear'), self.list_books(current_page - 1)),
            2: self.main_menu,
        }
        action = menu_options.get(selected_index)
        if action:
            return action()

    def add_book(self) -> None:
        """Добавление новой книги."""
        title: str = self._get_input('Введите название книги')
        author: str = self._get_input('Введите автора книги')
        year: str = self._get_input('Введите год издания книги', is_int=True)

        df: pd.DataFrame = pd.read_csv(self.file_library)
        if not df.empty:
            new_id: int = df['ID'].max() + 1
        else:
            new_id: int = 1

        try:
            new_book: pd.DataFrame = pd.DataFrame([[new_id, title, author, year, 'В наличии']])
            new_book.to_csv(self.file_library, mode='a', header=False, index=False)
        except UnicodeEncodeError:
            print(f'{Fore.RED}Ошибка кодировки.')
            return self.add_book()

        print(f'{Fore.GREEN}Данные добавлены!')

        selected_index: int = self._show_menu(
            ['Добавить ещё одну книгу.', 'Выйти в главное меню.'],
            '«Add book»'
        )

        menu_options = {0: self.add_book, 1: self.main_menu}
        action = menu_options.get(selected_index)
        if action:
            return action()

    def delete_book(self) -> None:
        """Удаление книги по ID."""
        df: pd.DataFrame = pd.read_csv(self.file_library)

        while True:
            book_id: int = self._get_input('Введите ID книги для удаления', is_int=True)
            if book_id in df['ID'].values:
                break
            print(f'{Fore.RED}Книга с ID «{book_id}» не найдена.')

        df = df[df['ID'] != book_id]
        df.to_csv(self.file_library, index=False)

        print(f'{Fore.GREEN}Книга с ID «{book_id}» успешно удалена.')

        selected_index: int = self._show_menu(
            ['Удалить ещё одну книгу.', 'Выйти в главное меню.'],
            '«Delete book»'
        )

        menu_options = {0: self.delete_book, 1: self.main_menu}
        action = menu_options.get(selected_index)
        if action:
            return action()

    def search_book_menu(self):
        """Меню для поиска книг."""
        selected_index: int = self._show_menu(
            [
                'Поиск книги по названию.',
                'Поиск книги по автору.',
                'Поиск книги по году издания.',
                'Выйти в главное меню.'
            ],
            '«Search book menu»'
        )

        menu_options = {
            0: lambda: self.search_book('Title', 'Введите название книги для поиска'),
            1: lambda: self.search_book('Author', 'Введите автора книги для поиска'),
            2: lambda: self.search_book('Year', 'Введите год издания для поиска', True),
            3: self.main_menu
        }
        action = menu_options.get(selected_index)
        if action:
            return action()

    def search_book(self, column: str, prompt: str, is_year: bool = False) -> None:
        """Поиск книги по указанному столбцу.

        Args:
            column (str) : Название столбца для поиска ('Title', 'Author', 'Year').
            prompt (str) : Сообщение, отображаемое пользователю для ввода данных.
        """
        search_value: str = self._get_input(prompt, is_year)

        df: pd.DataFrame = pd.read_csv(self.file_library)
        if column == 'Year':
            df = df[df[column] == int(search_value)]
        else:
            df = df[df[column].str.contains(search_value, case=False, na=False)]

        if df.empty:
            print(f'{Fore.RED}По вашему запросу ничего не найдено.')
        else:
            df_to_list: List[List] = [self.COLUMNS_NAME] + df.values.tolist()
            table = self._format_book_table(
                data_table=df_to_list,
                title='Результаты по вашему запросу.'
            )
            print(f'{table}')

        selected_index: int = self._show_menu(
            ['Найти ещё одну книгу.', 'Выйти в главное меню.'],
            '«Search book»'
        )

        menu_options = {0: self.search_book_menu, 1: self.main_menu}
        action = menu_options.get(selected_index)
        if action:
            return action()

    def update_book_status(self):
        """Изменение статуса книги по ID."""
        df: pd.DataFrame = pd.read_csv(self.file_library)

        while True:
            book_id: int = self._get_input('Введите ID книги для изменения статуса', is_int=True)
            if book_id in df['ID'].values:
                break
            print(f'{Fore.RED}Книга с ID «{book_id}» не найдена.')

        old_status = df.loc[df['ID'] == book_id, 'Status'].values[0]
        new_status = 'В наличии' if old_status == 'Выдана' else 'Выдана'

        df.loc[df['ID'] == book_id, 'Status'] = new_status
        df.to_csv(self.file_library, index=False)

        print(f'{Fore.GREEN}Год издания книги с ID «{book_id}» успешно изменён с '
              f'«{old_status}» на «{new_status}».')

        selected_index: int = self._show_menu(
            ['Изменить статус ещё одной книги.', 'Выйти в главное меню.'],
            '«Update book status»'
        )

        menu_options = {0: self.update_book_status, 1: self.main_menu}
        action = menu_options.get(selected_index)
        if action:
            return action()

    @staticmethod
    def _checking_for_valid_page(current_page: int, last_page: int) -> Tuple[int, Optional[str]]:
        """Проверяет валидность текущей страницы.

        Args:
            - current_page (int) : Номер текущей страницы.
            - last_page (int) : Номер последней страницы.

        Returns:
            - Tuple[int,Optional[str]] : Кортеж с обновлённым номером страницы и
            сообщением об ошибке (если есть).
        """
        if current_page < 1:
            return 1, 'Ошибка: нельзя перейти на страницу меньше 1.'
        elif current_page > last_page:
            return last_page, f'Ошибка: нельзя перейти на страницу больше {last_page}.'
        return current_page, None

    @staticmethod
    def _get_input(prompt: str, is_int: bool = False) -> Union[str, int]:
        """Получение пользовательского ввода с проверкой.

        Args:
            - prompt (str) : Подсказка для функции input.
            - is_year (bool) : Флаг, указывающий, что ввод должен быть числом.

        Returns:
            - str: Возвращает строку с введенным значением.
        """
        while True:
            value = input(f'{prompt}: ').strip()
            if not value:
                print(f'{Fore.RED}Ошибка: Это поле не может быть пустым.')
                continue
            if is_int:
                try:
                    return int(value)
                except ValueError:
                    print(f'{Fore.RED}Ошибка: Это поле должно быть числом.')
                    continue
            return value

    @staticmethod
    def _format_book_table(data_table: List[List], title: str = None) -> str:
        """Получение данных в виде таблицы.

        Args:
            - data_table (List[List]) : Двумерный список, где каждая вложенная
                                        последовательность представляет строку таблицы,
                                        а её элементы — соответствующие столбцы.
            - title (str) : Заголовок таблицы.

        Returns:
            - str: Строка, содержащая таблицу, в формате текста.
        """

        table_instance = SingleTable(data_table, title)
        table_instance.inner_heading_row_border = False
        table_instance.inner_row_border = True
        return table_instance.table

    @staticmethod
    def _show_menu(options: List[str], title: str) -> int:
        """Отображение меню с доступными действиями.

        Args:
            - options (List[str]) : Действия для меню.
            - title (str) : Название для меню.

        Returns:
            - int: Возвращает индекс выбранного действия.
        """
        menu = TerminalMenu(options, title=title)
        return menu.show()

    @staticmethod
    def _exit_application() -> None:
        """Выход из приложения."""
        sys.exit()


file_library: str = 'library_information.csv'
page_size: int = 5


def check_columns_in_csv(file_library: str):
    """Проверяет, что столбцы в CSV файле соответствуют ожидаемым."""
    df = pd.read_csv(file_library)
    csv_columns = list(df.columns)

    if csv_columns == ['ID', 'Title', 'Author', 'Year', 'Status']:
        library = LibraryManagementSystem(file_library, page_size)
        library.main_menu()
    else:
        print('Ошибка: Столбцы в файле не совпадают с ожидаемыми.')


check_columns_in_csv(file_library)
