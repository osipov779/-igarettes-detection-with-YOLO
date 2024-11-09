import time
import pika
import json
import numpy as np
from sklearn.datasets import load_diabetes
from datetime import datetime  # Импортируем datetime для генерации timestamp

np.random.seed(42)

# Пишем функции

def load_data():
    return load_diabetes(return_X_y=True)

def generate_message(X, y):
    # Формируем случайный индекс строки
    random_row = np.random.randint(0, X.shape[0] - 1)
    # Генерируем уникальный идентификатор на основе текущего времени в формате timestamp
    message_id = datetime.timestamp(datetime.now())
    # Выводим сообщение с уникальным идентификатором, вектором признаков и ответом
    message_y_true = {"ID": message_id, "body": json.dumps(y[random_row])}
    message_features = {"ID": message_id, "body": json.dumps(list(X[random_row]))}

    return message_id, message_y_true, message_features


def publish_messages(channel, message_id, message_y_true, message_features):
    # Публикуем сообщение в очередь y_true
    channel.basic_publish(
        exchange="", routing_key="y_true", body=message_y_true
    )
    print(f"Сообщение с правильным ответом отправлено в очередь (id: {message_id})")

    # Публикуем сообщение в очередь features
    channel.basic_publish(
        exchange="", routing_key="features", body=message_features
    )
    print(f"Сообщение с вектором признаков отправлено в очередь (id: {message_id})")

def send_features_and_responses():
    # Загружаем датасет о диабете
    X, y = load_data()
    
    while True:
        try:
        # Подключение к серверу на локальном хосте
        connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
        channel = connection.channel()

        # Создаём очередь y_true
        channel.queue_declare(queue='y_true')
        # Создаём очередь features
        channel.queue_declare(queue='features')
        
        # Генерируем сообщения
        message_id, message_y_true, message_features = generate_message(X, y)

        # Публикуем сообщения
        publish_messages(channel, message_id, message_y_true, message_features)

        # Закрываем подключение
        connection.close()

        # Добавляем задержку в 10 секунд
        time.sleep(10)
        except:
        print('Не удалось подключиться к очереди')

if __name__ == '__main__':
    send_features_and_responses()  # Запуск функции
