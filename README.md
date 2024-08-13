# Тестовое задание: Имеются несколько файлов и несколько конечных точек, в которые необходимо эти файлы доставить (скопировать). 

Исполнитель - 
*   [Клавдия Дунаева](https://www.t.me/klodunaeva)

**Инструменты и стек:**

[Python](https://www.python.org/) 
[requests](https://pypi.org/project/requests/),
[pyocclient](https://github.com/owncloud/pyocclient/tree/master),



**Как запустить проект:**

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/KlavaD/bs4_parser_pep
```


Создать и активировать виртуальное окружение:

```
python3 -m venv env
```

* Если у вас Linux/macOS

    ```
    source env/bin/activate
    ```

* Если у вас windows

    ```
    source env/scripts/activate
    ```

Обновить pip:

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```
Создайте .env файл и заполните своими данными:
```
FTP_HOST=ftp.automiq.ru
FTP_USERNAME=
FTP_PASSWORD=

CLOUD_URL=https://fs.automiq.ru/owncloud/index.php/s/Vfe40mHsvvWKxAZ
CLOUD_PASSWORD=

FOLDER_NAME=/tmp/test-240809/
```
В файле enter_data.py напишите названия файлов для копирования и места назначения.

Для запуска в командной строке введите:

Получить справку о командах: 
```
python main.py -h
```

Запуск в "сухом" режиме: 
```
python main.py -d полный путь до файлов
```
Запуск с перезаписыванием файла, если он уже существует в месте доставки:
```
python main.py -o полный путь до файлов
```
Запуск без перезаписывания файла, если он уже существует в месте доставки:
```
python main.py полный путь до файлов
```
