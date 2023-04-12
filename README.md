# registration-system-coursework
"we have Allendar at home"
### сторонние сурсы проекта
- [фигма](https://www.figma.com/file/Kt2FDXipEGxZJmpCemKc7s/Registration-system?t=3hfefkVQvIIGJvIm-6)
- [прототип в фигме](https://www.figma.com/proto/Kt2FDXipEGxZJmpCemKc7s/Registration-system?page-id=1%3A2&node-id=6-95&viewport=120%2C127%2C0.14&scaling=scale-down&starting-point-node-id=6%3A95&show-proto-sidebar=1)
### основные справочники, которые пока пригождались
- [вся джанго документация](https://docs.djangoproject.com/en/4.1/),
- особенно [туториал](https://docs.djangoproject.com/en/4.1/intro/) (1 - сетап, 2 - дб, 3 и 4 - веб)
- и [html-темплейты](https://docs.djangoproject.com/en/4.1/ref/templates/language/)
- [html хинты](https://www.w3schools.com/html/default.asp)
- [маркдаун](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax) лол
- [инструкция от фигмы по работе с прототипами со ссылочками на более конкретные инструкции](https://help.figma.com/hc/en-us/articles/360040314193-Guide-to-prototyping-in-Figma)
- [стили вышкинские отсюда таскаются](https://www.hse.ru/info/brandbook)
### как работать с шайтан-машиной
(пока, это я ещё не знаю, что будет, когда добавится бд)

(но полагаю, что копировать рабочее окружение целиком всё же эффективнее, чем пытаться что-то мутить с контейнерами)
- [установка джанго](https://docs.djangoproject.com/en/4.1/intro/install/)
- в командной строке из директории проекта (там, где `manage.py`) `python manage.py runserver` (по идее, должно сработать, но я никогда не запускала чисто скачанные проекты, только создавала новые)
- открыть в браузере ссылку, которую выдаст сервер (http://127.0.0.1:8000/register/), и можно играть
- для отображения большинства изменений достаточно перезагрузить страницу, ошибки падают либо прямо там (очень информативно), либо в командной строке. в начале рабочего дня сервер можно просто поднять и забыть, сломать его будет очень сложно
- основные нужные файлы лежат в `regsys` - `views.py`, `urls.py`, `templates`
- я не знаю, как толком настроить среду исполнения такого проекта в пайчарме. поэтому, чтобы не отвлекаться на его вопросы и ненужные усложнения, пока пишу просто в нотепаде++ лол
