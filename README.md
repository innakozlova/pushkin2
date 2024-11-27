<b>Простейшее интернет приложение на Flask + БД "Визитка сайта Экскурсионного бюро в городе Пушкин"</b>


На сайте представлены страницы с информацией "О нас", описанием услуг для целевой аудитории,
страница с контактами и формой заявки, через которую посетители могут заказать экскурсию. 
В случае отправки заявки на почту администратора сайта приходит уведомление. 

Предусмотрена возможность регистрации и авторизации пользователей. Зарегистрированные пользователи могут 
оставлять и удалять свои отзывы через форму, а также загружать изображение для отправки.

К приложению подключена база данных SQLite, в которой учитываются зарегистрированные пользователи и их отзывы. 

Отдельно выделена роль администратора, который может мониторить активность пользователей, удалять комментарии через
панель администратора.

Для повышения функционала сайта внедрен API погоды.
