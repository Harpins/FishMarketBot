# FishMarketBot 🐟

Telegram‑бот‑магазин с интеграцией Strapi 5.36.0.
Позволяет просматривать каталог, добавлять товары в корзину, изменять корзину и оформлять заказ.

## Установка и запуск

1. Склонировать репозиторий

```bash
git clone https://github.com/Harpins/FishMarketBot.git
cd FishMarketBot
```

2. Создать виртуальное окружение и установить зависимости
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Создать файл .env содержащий следующие переменные:

STRAPITOKEN - full-access token, можно получить в админке Strapi, см. п. 4.4

TG_BOT_TOKEN - токен бота-магазина, можно получить у BotFather

ERROR_BOT_TOKEN - TG токен отдельного бота для логгирования ошибок, также получается у BotFather

ERROR_CHAT_ID - ID чата с ботом-сборщиком ошибок

4. Установка и запуск Strapi (локально)

[Документация к Strapi](https://github.com/strapi/documentation)

4.1 Убедитесь, что установлены:

- Node.js (версия 18 или 20 — рекомендуется для Strapi 5.x);

- npm (обычно идёт в комплекте с Node.js).

[Как установить](https://www.geeksforgeeks.org/node-js/how-to-download-and-install-node-js-and-npm/)

Проверка:
```bash
node --version
npm --version
```
4.2 Создание проекта Strapi (быстрый старт с SQLite)


- Создать проект my-strapi-project
```bash
npx create-strapi-app@5.36.0 my-strapi-project --quickstart
```
Важный нюанс - Strapi не устанавливается глобально, он устанавливается отдельно в каждый созданный командой проект

- перейдите в директорию проекта и запустите Strapi в режиме разработки

```bash
cd my-strapi-project
npm run develop
```
- Дождитесь завершения развертывания Strapi — после этого в терминале отобразится ссылка для доступа к административной панели

По умолчанию Strapi запускается на порту 1337

- Зарегистрируйтесь и зайдите в свой аккаунт в админке Strapi.

4.3 Создайте модели со следующими полями:

Product - Заполните тестовыми/реальными данными для отображения каталога товаров
name: short-text
price: decimal
mass_g: decimal
description: rich-text
image: media (single)
cartproduct: one-to-one relation with cartproduct

customer
tg_id: short-text
email: short-text
cart: one-to-one relation with cart

cart
customer: one-to-one relation with customer
cartproducts: one-to-many relation with cartproduct

cartproduct
cart: relation many-to-one with cart
product: relation one-to-one with Product
quantity: integer or decimal

4.4 В настройках админки получите [full-access Strapi токен](https://docs.strapi.io/cms/features/api-tokens) и запишите в переменную окружения STRAPITOKEN

5. Запустить бота как модуль (обязательно, иначе может не видеть зависимости)
```bash
python -m main
```
