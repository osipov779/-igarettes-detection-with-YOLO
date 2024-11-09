import pika
import pickle
import numpy as np
import json

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)

try:
    # Создаём подключение по адресу rabbitmq:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
 
    # Объявляем очередь features
    channel.queue_declare(queue='features')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')
 
    # Создаём функцию callback для обработки данных из очереди
    def callback(ch, method, properties, body):
        # считанное сообщение десериализуем и делим словарь на id и значение признаков
        message = json.loads(body)
        message_id = message['id']
        features = np.array(message['value'])
        
        # логируем факт получения данных
        with open('./logs/model_log.txt', 'a', newline='') as file:
            file.write(f'Получен вектор признаков {np.around(features, 5)} с ID {message_id}\n')
        
        # делаем предсказание
        pred = regressor.predict(features.reshape(1, -1))
        
        # Публикуем сообщение в очередь y_pred
        channel.basic_publish(exchange='',
                        routing_key='y_pred',
                        body=json.dumps({'id': message_id, 'value': pred[0]}))
        # логируем факт отправления предсказания
        with open('./logs/model_log.txt', 'a', newline='') as file:
            file.write(f'Предсказание {pred[0]} с ID {message_id} отправлено в очередь y_pred\n')
 
    # Извлекаем сообщение из очереди features
    channel.basic_consume(
        queue='features',
        on_message_callback=callback,
        auto_ack=True
    )
    print('...Ожидание сообщений, для выхода нажмите CTRL+C')
 
    # Запускаем режим ожидания прихода сообщений
    channel.start_consuming()
except:
    print('Не удалось подключиться к очереди')