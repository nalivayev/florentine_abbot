[![en](https://img.shields.io/badge/lang-en-red.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.md)
[![ru](https://img.shields.io/badge/lang-ru-yellow.svg)](https://github.com/nalivayev/florentine_abbot/blob/master/README.ru.md)

Набор утилит предназначен для автоматизации процесса сканирования с использованием [VueScan](https://www.hamrick.com) от Ed Hamrick 

Включает:

calculate_dpi.py - утилита для расчета оптимального режима сканирования на основе исходных данных о фотографии

run_workflow.py - утилита выполняющая имитацию рабочего процесса для VueScan на основе заранее сохраненных настроек программы

В настройках используются шаблоны

Формат шаблона:

`{<n>[:l[:a[:p]]]}`.

Где:

n - имя значения  
l - общая длина  
a - выравнивание  
p - символ-заполнитель  

Пример формата шаблона:

`{digitization_year:8:>:0}`.

Список шаблонов, которые могут быть использованы в *.ini файлах:

user_name - имя пользователя операционной системы
digitization_year - год оцифровки, извлеченный из EXIF  
digitization_month - месяц оцифровки, извлеченный из EXIF  
digitization_day - день оцифровки, извлеченный из EXIF  
digitization_hour - час оцифровки, извлеченный из EXIF  
digitization_minute - минута оцифровки, извлеченная из EXIF  
digitization_second - секунда оцифровки, извлеченная из EXIF
