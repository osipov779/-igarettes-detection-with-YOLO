import pika
import json
import csv

# Создаём глобальный словарь для хранения меток и предсказаний
data_store = {}

try:
    # Создаём подключение к серверу на локальном хосте
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    channel = connection.channel()
   
    # Объявляем очередь y_true
    channel.queue_declare(queue='y_true')
    # Объявляем очередь y_pred
    channel.queue_declare(queue='y_pred')
 
    # Создаём функцию callback_y_true для обработки данных из очереди y_true
    def callback_y_true(ch, method, properties, body):
        # считанное сообщение десериализуем и делим словарь на id и значение
        message = json.loads(body)
        message_id = message['id']
        value = message['value']

        # логируем факт получения
        print(f'Из очереди {method.routing_key} получено значение {value} с ID {message_id}')
        with open('./logs/labels_log.txt', 'a', newline='') as file:
            file.write(f'Из очереди {method.routing_key} получено значение {value} с ID {message_id}\n')    
                
        global data_store
        # добавляем данные в data_store по существующему id
        if data_store['id'] == message_id:
            data_store['y_true'] = value
            absolute_error = abs(data_store['y_pred'] - value)
            data_store['absolute_error'] = absolute_error
            # логируем факт объединения всех данных по текущему id
            with open('./logs/labels_log.txt', 'a', newline='') as file:
                file.write(f'ID {message_id} найден\n')
        else:
            # логируем ошибку
            with open('./logs/labels_log.txt', 'a', newline='') as file:
                file.write(f'Не удалось найти ID {message_id}\n')
        
        # добавляем строку в файл csv
        with open('./logs/metric_log.csv', 'a', newline='') as f:
            csv.writer(f).writerow(data_store.values())       
    
    # Создаём функцию callback_y_pred для обработки данных из очереди y_pred            
    def callback_y_pred(ch, method, properties, body):
        # считанное сообщение десериализуем и делим словарь на id и значение
        message = json.loads(body)
        message_id = message['id']
        value = message['value']

        # логируем факт получения
        print(f'Из очереди {method.routing_key} получено значение {value} с ID {message_id}')
        with open('./logs/labels_log.txt', 'a', newline='') as file:
            file.write(f'Из очереди {method.routing_key} получено значение {value} с ID {message_id}\n')    
                
        global data_store
        # добавляем данные в data_store
        data_store['id'] = message_id
        data_store['y_pred'] = value

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