import pika
import json
import csv

# Создаём глобальный словарь для хранения меток и предсказаний
data_store = {}

# Имя файла для записи метрик
csv_file = "logs/metric_log.csv"

# Функция для записи метрик в CSV
def write_to_csv(message_id, y_true, y_pred):
    # Вычисляем абсолютную ошибку
    abs_error = abs(y_true - y_pred)

    # Проверяем, существует ли файл
    file_exists = os.path.isfile(csv_file)

    # Открываем файл в режиме добавления
    with open(csv_file, "a", newline="") as csvfile:
        fieldnames = ["message_id", "y_true", "y_pred", "absolute_error"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Записываем заголовки, если файл новый
        if not file_exists:
            writer.writeheader()

        # Записываем данные
        writer.writerow(
            {
                "message_id": message_id,
                "y_true": y_true,
                "y_pred": y_pred,
                "absolute_error": abs_error,
            }
        )

# Создаём функцию callback для обработки данных из очереди
def callback(ch, method, properties, body):
    message = json.loads(body)
    message_id = message["id"]
    value = message["body"]

    # Сохраняем значение в соответствующий ключ
    if method.routing_key == "y_true":
        data_store[message_id]["true"] = value
    else:  # y_pred
        data_store[message_id]["pred"] = value

    # Если для данного id получены оба значения, записываем их в CSV
    if "true" in data_store[message_id] and "pred" in data_store[message_id]:
        y_true = data_store[message_id]["true"]
        y_pred = data_store[message_id]["pred"]

        # Записываем метрики в CSV
        write_to_csv(message_id, y_true, y_pred)
        print(
            f"Записаны метрики для сообщения {message_id}: true={y_true}, pred={y_pred}, "
            f"error={abs(y_true - y_pred)}"
        )

        # Удаляем обработанные значения из словаря
        del data_store[message_id]

def send_features_and_responses():
    while True:
        try:
        # Создаём подключение к серверу на локальном хосте
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
   
        # Объявляем очередь y_true
        channel.queue_declare(queue='y_true')
        # Объявляем очередь y_pred
        channel.queue_declare(queue='y_pred')
 
        # Извлекаем сообщение из очереди y_pred
        channel.basic_consume(
            queue='y_pred',
            on_message_callback=callback_y_pred,
            auto_ack=True
        ) 
    
        # Извлекаем сообщение из очереди y_true
        channel.basic_consume(
            queue='y_true',
            on_message_callback=callback_y_true,
            auto_ack=True
        )

        # Запускаем режим ожидания прихода сообщений
        print('...Ожидание сообщений, для выхода нажмите CTRL+C')
        channel.start_consuming()
    except:
        print('Не удалось подключиться к очереди')

if __name__ == "__main__":
   send_features_and_responses()
