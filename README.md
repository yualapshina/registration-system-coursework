# registration-system-coursework
"we have Allendar at home"
### сторонние сурсы проекта
- [фигма дизайна интерфейса](https://www.figma.com/file/Kt2FDXipEGxZJmpCemKc7s/Registration-system?t=3hfefkVQvIIGJvIm-6)
- [фигджем базы данных](https://www.figma.com/file/cpJIurC4qGIu2jrA6UtA9I/Registration-System%3A-ER-Diagram?t=dPPlxvHcQsi7tSL4-6)
### основные справочники, которые пока пригождались
- [вся джанго документация](https://docs.djangoproject.com/en/4.1/),
- особенно [туториал](https://docs.djangoproject.com/en/4.1/intro/) (1 - сетап, 2 - дб, 3 и 4 - веб)
- и [html-темплейты](https://docs.djangoproject.com/en/4.1/ref/templates/language/)
- [html хинты](https://www.w3schools.com/html/default.asp)
- [маркдаун](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) лол
### как работать с шайтан-машиной
(для версии рабочего коммита от 11 апреля, потому что я пока не понимаю, насколько бд портативна, и стоит ли возня с ней того)
- [установка джанго](https://docs.djangoproject.com/en/4.1/intro/install/)
- в командной строке из директории проекта (там, где `manage.py`) `python manage.py runserver` (по идее, должно сработать, но я никогда не запускала чисто скачанные проекты, только создавала новые)
- открыть в браузере ссылку, которую выдаст сервер (http://127.0.0.1:8000/register/), и можно играть
- для отображения большинства изменений достаточно перезагрузить страницу, ошибки падают либо прямо там (очень информативно), либо в командной строке. в начале рабочего дня сервер можно просто поднять и забыть, сломать его будет очень сложно
- основные нужные файлы лежат в `regsys` - `views.py`, `urls.py`, `templates`
- я не знаю, как толком настроить среду исполнения такого проекта в пайчарме. поэтому, чтобы не отвлекаться на его вопросы и ненужные усложнения, пока пишу просто в нотепаде++ лол
