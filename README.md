# registration-system-coursework
Данный проект - прототип системы для регистрации на мероприятия, разрабатываемый в рамках курсовой/практики/диплома для ИМиКН НИУ ВШЭ. 
### Содержание репозитория
- Весь исходный код проекта, сосредоточенный в основном в папке *regsys*
- Пояснительные записки, отчёты и презентации для защиты в папке *documents*
### Ссылки на дополнительные ресурсы
- [Дизайн интерфейса](https://www.figma.com/file/Kt2FDXipEGxZJmpCemKc7s/Registration-system?t=3hfefkVQvIIGJvIm-6)
- [Интерактивный прототип дизайна](https://www.figma.com/proto/Kt2FDXipEGxZJmpCemKc7s/Registration-system?page-id=1%3A2&node-id=6-95&viewport=120%2C127%2C0.14&scaling=scale-down&starting-point-node-id=6%3A95&show-proto-sidebar=1)
- [Архитектура базы данных](https://www.figma.com/file/cpJIurC4qGIu2jrA6UtA9I/Registration-System%3A-ER-Diagram?type=whiteboard&t=XQAnZ1MlXFPwVaEB-6)
### release notes
штуки, которым нужны дизайны:
- системные сообщения: [есть вот здесь](https://docs.djangoproject.com/en/4.2/ref/contrib/messages/#message-tags)
- навбары: цыганские фокусы блин. я понятия не имею почему, но ссылки просто-напросто не работали вне parent (а по логике им место ниже сообщений). поставь их адекватно как-нибудь.
- статусы записей: [которые вот эти штуки](https://docs.djangoproject.com/en/4.2/ref/models/fields/#field-choices-enum-types)
- лейблы событий (механика та же, что и сверху)
- фильтрбар
- НОВОЕ: html textarea в обратной связи
запуск:
- миграции как всегда
- добавился гитигнор, так что если пропадут мелкие автогенерируемые файлы, то так и надо
- безопасность паролей обеспечивается тем, что они хранятся в отдельном неотслеживаемом файлике, так что чтобы оно работало, пиши мне и я скину его отдельно