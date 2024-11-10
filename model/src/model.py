import pika
import pickle
import numpy as np
import json

# Читаем файл с сериализованной моделью
with open('myfile.pkl', 'rb') as pkl_file:
    regressor = pickle.load(pkl_file)
    
# Создаём функцию callback для обработки данных из очереди
def callback(channel, method, properties, body):
    # считанное сообщение десериализуем и делим словарь на id и значение признаков
    message = json.loads(body)
    message_id = message['id']
    features = np.array(message['value'])
    
    # логируем факт получения данных
    with open('./logs/model_log.txt', 'a', newline='') as file:
        file.write(f'Получен вектор признаков {np.around(features, 5)} с ID {message_id}\n')
    
    # делаем предсказание
    pred = regressor.predict(features.reshape(1, -1))
    
    # Формируем сообщение с предсказанием
    prediction_message = {"id": message_id, "body": pred[0]}
    
    # Отправляем предсказание
    channel.basic_publish(exchange="", routing_key="y_pred", body=json.dumps(prediction_message))
    
    # логируем факт отправления предсказания
    with open('./logs/model_log.txt', 'a', newline='') as file:
        file.write(f'Предсказание {pred[0]} с ID {message_id} отправлено в очередь y_pred\n')
        
def send_features_and_responses():
    while True:
        try:
        # Создаём подключение по адресу RabbitMQ:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()
 
        # Объявляем очередь features
        channel.queue_declare(queue='features')
        # Объявляем очередь y_pred
        channel.queue_declare(queue='y_pred')
             
        # Публикуем сообщение в очередь y_pred
        #channel.basic_publish(exchange='',
                        #routing_key='y_pred',
                        #body=json.dumps({'id': message_id, 'value': pred[0]}))
        
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

if __name__ == "__main__":
    # Загружаем модель при запуске скрипта
    regressor = load_model()
    send_features_and_responses()
