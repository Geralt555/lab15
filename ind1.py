#!/usr/bin/env python3
# -*- config: utf-8 -*-

# Вариант 13. Использовать словарь, содержащий следующие ключи: фамилия, имя; номер телефона;
# дата рождения. Написать программу, выполняющую следующие
# действия: ввод с клавиатуры данных в список, состоящий из словарей заданной структуры;
# записи должны быть упорядочены по трем первым цифрам номера телефона; вывод на
# экран информации о человеке, чья фамилия введена с клавиатуры; если такого нет, выдать
# на дисплей соответствующее сообщение.

# Изучить возможности модуля logging. Добавить для предыдущего задания вывод в файлы лога
# даты и времени выполнения пользовательской команды с точностью до миллисекунды.

# Выполнить индивидуальное задание 2 лабораторной работы 14, добавив аннтотации типов.
# Выполнить проверку программы с помощью утилиты mypy.

from dataclasses import dataclass, field
import logging
import sys
from typing import List
import xml.etree.ElementTree as ET


class IllegalYearError(Exception):

    def __init__(self, year, message="Illegal year (ДД.ММ.ГГГГ)"):
        self.year = year
        self.message = message
        super(IllegalYearError, self).__init__(message)

    def __str__(self):
        return f"{self.year} -> {self.message}"


class UnknownCommandError(Exception):

    def __init__(self, command, message="Unknown command"):
        self.command = command
        self.message = message
        super(UnknownCommandError, self).__init__(message)

    def __str__(self):
        return f"{self.command} -> {self.message}"


@dataclass(frozen=True)
class People:
    surname: str
    name: str
    number: int
    year: int


@dataclass
class Staff:
    peoples: List[People] = field(default_factory=lambda: [])

    def add(self, surname, name, number, year) -> None:

        if "." not in number:
            raise IllegalYearError(year)

        self.peoples.append(
            People(
                surname=surname,
                name=name,
                number=number,
                year=year
            )
        )

        self.peoples.sort(key=lambda peoples: people.number)

    def __str__(self):
        table = []
        line = '+-{}-+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 20,
            '-' * 20,
            '-' * 20,
            '-' * 15
        )
        table.append(line)
        table.append(
            '| {:^4} | {:^20} | {:^20} | {:^20} | {:^15} |'.format(
                "№",
                "Фамилия ",
                "Имя",
                "Номер телефона",
                "Дата рождения"
            )
        )
        table.append(line)

        for idx, People in enumerate(self.peoples, 1):
            table.append(
                '| {:>4} | {:<20} | {:<20} | {:<20} | {:>15} |'.format(
                    idx,
                    people.surname,
                    people.name,
                    people.number,
                    people.year
                )
            )

        table.append(line)

        return '\n'.join(table)

    def select(self, surname) -> List[People]:
        parts = command.split(' ', maxsplit=2)
        sur = (parts[1])
        result = []

        for people in self.peoples:
            if people.surname == surname:
                result.append(people)

        return result

    def load(self, filename):
        with open(filename, 'r', encoding='utf8') as fin:
            xml = fin.read()
        parser = ET.XMLParser(encoding="utf8")
        tree = ET.fromstring(xml, parser=parser)
        self.peoples = []

        for people_element in tree:
            surname, name, number, year = None, None, None, None

            for element in people_element:
                if element.tag == 'surname':
                    surname = element.text
                elif element.tag == 'name':
                    name = element.text
                elif element.tag == 'number':
                    number = element.text
                elif element.tag == 'year':
                    year = element.text

                if surname is not None and name is not None \
                        and number is not None and year is not None:
                    self.peoples.append(
                        People(
                            surname=surname,
                            name=name,
                            number=int(number),
                            year=int(year)
                        )
                    )

    def save(self, filename):
        root = ET.Element('peoples')
        for people in self.peoples:
            people_element = ET.Element('peoples')

            surname_element = ET.SubElement(people_element, 'surname')
            surname_element.text = people.surname

            name_element = ET.SubElement(people_element, 'name')
            name_element.text = people.name

            number_element = ET.SubElement(people_element, 'number')
            number_element.text = str(people.number)

            year_element = ET.SubElement(people_element, 'year')
            year_element.text = str(people.year)

            root.append(people_element)

        tree = ET.ElementTree(root)
        with open(filename, 'wb') as fout:
            tree.write(fout, encoding='utf8', xml_declaration=True)


if __name__ == '__main__':

    logging.basicConfig(
        filename='peoples.log',
        level=logging.INFO,
        format='%(asctime)s %(levelname)s:%(message)s'
    )

    staff = Staff()
    while True:
        try:
            command = input(">>> ").lower()
            if command == 'exit':
                break


            elif command == 'add':
                surname = input("Фамилия ")
                name = input("Имя ")
                number = int(input("Номер телефона "))
                year = input("Дата рождения в формате: дд.мм.гггг ")

                staff.add(surname, name, number, year)
                logging.info(
                    f"Добавлена фамилия: {surname}, "
                    f"Добавлено имя {name}, "
                    f"Добавлен номер телефона {number}, "
                    f"Добавлена дата рождения {year}. "
                )


            elif command == 'list':
                print(staff)
                logging.info("Отображен список людей.")

            elif command.startswith('select '):
                parts = command.split(' ', maxsplit=2)
                selected = staff.select(parts[1])

                if selected:
                    for c, people in enumerate(selected, 1):
                        print(
                            ('Фамилия:', people.surname),
                            ('Имя:', people.name),
                            ('Номер телефона:', people.number),
                            ('Дата рождения:', people.year)
                        )
                    logging.info(
                        f"Найден человек с фамилией {People.surname}"
                    )

                else:
                    print("Таких фамилий нет!")
                    logging.warning(
                        f"Человек с фамилией {People.surname} не найден."
                    )

            elif command.startswith('load '):
                parts = command.split(' ', maxsplit=1)
                staff.load(parts[1])
                logging.info(f"Загружены данные из файла {parts[1]}.")

            elif command.startswith('save '):
                parts = command.split(' ', maxsplit=1)
                staff.save(parts[1])
                logging.info(f"Сохранены данные в файл {parts[1]}.")

            elif command == 'help':

                print("Список команд:\n")
                print("add - добавить человека;")
                print("list - вывести список людей;")
                print("select <фамилия> - запросить информацию по фамилии;")
                print("help - отобразить справку;")
                print("load <имя файла> - загрузить данные из файла;")
                print("save <имя файла> - сохранить данные в файл;")
                print("exit - завершить работу с программой.")
            else:
                raise UnknownCommandError(command)

        except Exception as exc:
            logging.error(f"Ошибка: {exc}")
            print(exc, file=sys.stderr)
