# Telebridge

![demonstration](https://github.com/cyborg-ubyvtsya/telegram-mastodon-bridge/blob/main/img/demo.gif)

Telegram/Mastodon bot for forwarding messages.

## Usage

- Create a telegram bot
- - Recieve telegram's access token
- Create a mastodon bot
- - Give it the rights to write statuses
- - Save mastodon's access token
- Subscribe your telegram bot to channel(s) you need
- Install dependencies `pip install -r requirements.txt`
- Edit main.py's `mastodon_visibility = "direct"` variable
- Launch main.py
- - Give it telegram token
- - Then mastodon one
- Bot will start forwarding posts

### Limitations

- Only reposts plain text, images, and videos
- Image galleries are published as separate posts

# Телеміст

Телеграм/Мастодон бот, який дописи з тг в мастодон.

## Використання

- Створіть бота в Телеграм
- - Отримайте токен доступу
- Створіть бота в Мастодон
- - Дайте йому доступ до створення дописів
- - Збережіть токен доступу
- Підпишіть бота на потрібні канали в телеграмі
- Встановіть залежності `pip install -r requirements.txt`
- Відкрийте main.py і змініть видимість постів в `mastodon_visibility = "direct"`
- Запустіть скрипт
- - Дайте йому токен телеграму
- - Дайте йому токен мастодону
- Бот почне постити нові дописи з каналу на який він підписаний

### Обмеження

- Підтримуються лише текст, світлини, та відео
- Галереї публікуються в окремих дописах
