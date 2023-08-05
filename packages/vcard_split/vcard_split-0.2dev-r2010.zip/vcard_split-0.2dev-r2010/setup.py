# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
setup(
    name = "vcard_split",
    version = "0.2",
#    packages = find_packages(),
    py_modules = ['vcard_split'],
    install_requires=[
        "vobject>=0.8.1c",
        "argparse",
    ],
    author = "mail@dtatarkin.ru",
    author_email = "mail@dtatarkin.ru",
    description = '\
        Splits one vcard file (*.vcf) to many vcard files\
        with one vcard per file. Useful for import contacts to phones, \
        thats do not support multiple vcard in one file. \
        Supprt unicode cyrillic characters. \
        Консольная программа для разбиения одного большлго файла с контактами в формате VCARD (*.vcf)\
        на несколько файлов содержащих один контакт. Полезна для импорта контактов в телефон,\
        который не поддерживает несколько контактов в одном файле. Поддерживает русские буквы кириллицу в тексте контактов.\
        Работоспособность проверялась на файле с контактами экспортированными из google gmail.com. \
        Установка вариант 1: скачать, распаковать, в папке запустить "python setup.py install". \
        Использование вариант 1: python vcard_split.py [-h] [-l LOG_LEVEL] [-d] filename [filename ...] например "python vcard_split.py contacts.vcf"\
        Установка вариант 2: "easy_install -U vcard_split". \
        Использование вариант 2: vcard_split [-h] [-l LOG_LEVEL] [-d] filename [filename ...] например "vcard_split contacts.vcf"\
    ',
    license = "PSF",
    keywords = "vcard split",
    entry_points = {
        'console_scripts': [
            'vcard_split = vcard_split:main',
        ],
    },    
    classifiers=[
              'Development Status :: 4 - Beta',
              'Environment :: Console',
              'Intended Audience :: End Users/Desktop',
              'Intended Audience :: System Administrators',
              'License :: OSI Approved :: Python Software Foundation License',
              'Operating System :: OS Independent',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2.6',
              'Topic :: Communications :: Email :: Address Book',
              'Topic :: Communications :: Telephony',
              'Topic :: Text Processing',
              ],
)