## Описание
Проект для сбора статистических данных:
- текущих
- сборки сети
- отрисовки ценников
- и т.д.  

## Requirements / Требования
- app/requirements.txt


##Installation and run / Установка и запуск проекта
You can install and start the project locally or just start the project in the Docker. But containers are simpler. You have to choose :)
##Run in Docker / Запуск проекта в Docker
- project start: docker-compose up --build -d
- project down: docker-compose down

##Local installation / Локальная установка
#### Local Installation / Локальная установка 
- Open the command line, navigate to the project folder and execute:
- virtualenv *virtualenvname*
- Clone this repository to virtualenv folder
- Linux: source *virtualenvname*/bin/activate (Windows: call *virtualenvname*/Scripts/activate.bat)
- pip install -r app/requirements.txt
- python app/manage.py migrate
- python app/manage.py createsuperuser

#### Runserver / запуск тестового серевера
- python app/manage.py runserver 8000
- open http://127.0.0.1:8000/ in web browser.

## Основные реализованные подсистемы и фичи:
####Общая информация
- текущий мониторинг
- запуск сборки сети со сбором статистических данных
- запуск отрисовки ценников со сбором статистических данных
- объединенный запуск (сборка(и) сети + отрисовка(и) ценников)
- мониторинг доступности стендов
- сравнение конфигурационных файлов Chaos
- получение текущих и средникх значений напряжения
- получение общего количества значений bat_reserved
- отчеты в формате Excel о результатах сборки сети и отрисовки ценников

#### Страница "Устройства"
- Вывод в табличном виде с возможностью экспорта данных в табличном виде
- Вывод текуших статистических данных
- Отображение предупреждений о расхождениях между конфигурационными файлами chaos (текущий и "эталонный")
- Цветовая индикация доступности(недоступности) устройств
- Возможность изменения настроек устройства
#### Страница "Общие отчеты"
- Вывод в табличном виде с возможностью экспорта данных в табличном виде
#### Страница "Сборки сети"
- Вывод результатов(отчетов)  в табличном виде с возможностью экспорта данных в табличном виде
#### Страница "Отрисовки ценников"
- Вывод результатов(отчетов) отрисовки ценников в табличном виде с возможностью экспорта данных в табличном виде
#### Страница "Отрисовки ценников"


