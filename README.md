Микросервисная архитектура для анализа медицинских данных
-
Проект реализует микросервисную архитектуру для анализа медицинских данных с использованием брокера сообщений RabbitMQ. Система состоит из четырех независимых сервисов, которые работают совместно для генерации предсказаний, расчета метрик и визуализации распределения ошибок.

Структура проекта
-
microservice_architecture
    └─features
        └─src
            └─features.py
    └─model
        └─src
            └─model.py
            └─myfile.pkl
    └─metric
        └─src
            └─metric.py


├── docker-compose.yaml
├── features/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── features.py
├── logs/
│   ├── error_distribution.png
│   └── metric_log.csv
├── metric/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       └── metric.py
├── model/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── src/
│       ├── model.py
│       └── myfile.pkl
└── plot/
    ├── Dockerfile
    ├── requirements.txt
    └── src/
        └── plot.py
Описание сервисов
-
Features Service (features/src/features.py):

Загружает датасет о диабете
Генерирует случайные выборки
Отправляет векторы признаков и истинные значения в очереди RabbitMQ
Добавляет уникальные ID сообщений на основе временных меток
Работает в бесконечном цикле с интервалом 10 секунд

Model Service (model/src/model.py):

Загружает предварительно обученную модель из myfile.pkl
Слушает очередь с признаками
Делает предсказания
Отправляет предсказания в очередь предсказаний
Сохраняет ID сообщений для отслеживания

Metric Service (metric/src/metric.py):

Слушает очереди с истинными значениями и предсказаниями
Сопоставляет пары по ID сообщений
Вычисляет абсолютные ошибки
Записывает результаты в logs/metric_log.csv

Plot Service (plot/src/plot.py):

Отслеживает metric_log.csv
Создает гистограммы распределения ошибок
Добавляет статистическую информацию (среднее, медиана)
Сохраняет графики в logs/error_distribution.png
Обновляется каждые 10 секунд

Требования
-
Docker
Docker Compose

Запуск
-
Клонируйте репозиторий:

git clone <url-репозитория>
cd <название-директории>
Запустите сервисы с помощью Docker Compose:

docker-compose up -d

Мониторинг
-
RabbitMQ Management UI: http://localhost:15672 (guest/guest)
Метрики: logs/metric_log.csv
Визуализация распределения ошибок: logs/error_distribution.png
Логи сервисов: docker logs <имя-контейнера>
Docker Compose конфигурация

Сервисы:
-

rabbitmq: Брокер сообщений
Порты: 5672 (AMQP), 15672 (Management UI)
features: Генерация данных
model: Предсказания
metric: Расчет метрик
plot: Визуализация
Все сервисы настроены на автоматический перезапуск и имеют необходимые зависимости.

Формат сообщений
Сообщения отправляются в формате JSON:

{
    "id": 1699541234.567,
    "body": [значение]
}
где:

id: Unix timestamp как идентификатор сообщения
body: Вектор признаков или значение предсказания
Остановка сервисов
docker-compose down
Структура файлов
docker-compose.yaml: Конфигурация Docker Compose
*/Dockerfile: Инструкции сборки контейнеров
*/requirements.txt: Зависимости Python
*/src/*.py: Исходный код сервисов
logs/: Директория для файлов с результатами
metric_log.csv: Метрики и ошибки
error_distribution.png: Визуализация распределения ошибок
