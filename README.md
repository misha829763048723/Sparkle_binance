# Sparkle_binance
Binance P2P orders bot

Бот запускается на vps-сервере и предназначен для пользования несколькими людьми.

Пользователь добавляет свои cookie от аккаунта binance и proxy через дискорд-бота.
Дискорд-бот редактирует tasks.json в котором указаны все данные.

*Суть программы*

Бот постоянно с помощью асинхронных запросов мониторит предложения на покупку USDT на binance,

Как только появляется предложение ниже рынка, а разница больше числа, указанного одним (несколькими) пользователями, бот отправляет реквесты на покупку криптовалюты.

Результат приходит в дискорд, с помощью вебхуков

Благодаря шустрому API Бинанса и vps серверу, находящемуся близко к серверам бинанса, весь процесс заключения сделки занимает 0.2-0.4 секунды
