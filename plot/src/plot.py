import time
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

# Создаём бесконечный цикл
while True:
    try:
        # считываем таблицу
        df = pd.read_csv('./logs/metric_log.csv')
        # строим гистограмму ошибок        
        sns_plot  = sns.histplot(df['absolute_error'], kde=True, color="orange", bins=30)
        
        # сохраняем график в файл
        plt.savefig('./logs/error_distribution.png')
        plt.close()
        print('Файл успешно сохранен')

        time.sleep(60) # добавляем паузу        
    except:
        print('Не удалось считать таблицу metric_log.csv')