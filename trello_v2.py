import requests
import sys
###################################################
#  ПЕРЕД ЗАПУСКОМ ПРОГРАММЫ ВВЕДИ СВОИ ДАННЫЕ     #
#  key  token board_id                            #
#  строки 12, 13, 19                              #
###################################################


# Данные авторизации в API Trello  
auth_params = {
    'key': "",
    'token': "",}

# Адрес, на котором расположен API Trello, # Именно туда мы будем отправлять HTTP запросы.
base_url = "https://api.trello.com/1/{}"

#ID доски
board_id = ""
board_long_id = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()['id']
print(board_long_id)

def read():
    # Получим данные всех колонок на доске:      
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Теперь выведем название каждой колонки и всех заданий, которые к ней относятся:      
    for column in column_data:
        #print(column['name'], column)
        # Получим данные всех задач в колонке и перечислим все названия      
        task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        print(column['name'], " | в колонке {} задач".format(len(task_data)))
        if not task_data:
            print('\t' + 'Нет задач!')
            continue
        for task in task_data:
            print('\t' + task['name'])

def create(name, column_name): # _name_ имя создаваймой карточки(задачи), _column_name_ имя колонки(lists) в которой разместить задачу
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    # Переберём данные обо всех колонках, пока не найдём ту колонку, которая нам нужна
    for column in column_data:
        if column['name'] == column_name:
         # Создадим задачу с именем _name_ в найденной колонке
            requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})
            break

def move(name, column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()

    tasks_id_l = [] # Список задач с искомым иминем
    t_counter = 1 # Счетчик задач для выбора нужной задачи
        # Среди всех колонок нужно найти задачи с заданым именем и записать их id в tasks_id_l
    for column in column_data:
        column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
        for task in column_tasks:
            if task['name'] == name:
                tasks_id_l.append(task['id'])
    print("Найдено {} задач с именем {}".format(len(tasks_id_l),name))

    
    for task_id in tasks_id_l:
        f_task = requests.get(base_url.format('cards') + '/' + task_id, params=auth_params).json()
        list_of_f_task = requests.get(base_url.format('lists') + '/' + f_task['idList'], params=auth_params).json()
        print("{}) задача {} с ID: {} в колонке {}".format(t_counter, name, f_task['id'], list_of_f_task['name']))
        t_counter += 1
    
    if len(tasks_id_l) > 1:
        # Запрашиваем задачу с которой работать и поверяем допустимость выбора
        task_num = int(input("Выбирите задачу с которой хотите работать (1 - {}): ".format(len(tasks_id_l))))
        while task_num > len(tasks_id_l) or task_num < 1:
            task_num = int(input("Некорректный выбор. Выбирите в диапазоне 1 - {}: ".format(len(tasks_id_l))))
        # Теперь, когда у нас есть выбор пользователя получим id задачи, которую мы хотим переместить
        moving_task_id = tasks_id_l[task_num-1]
        print("Ваш выбор {}, это задача с ID: {}".format(task_num, moving_task_id))
    elif len(tasks_id_l) == 0:
        print("Задача не найдена")
    else:
        moving_task_id = tasks_id_l[0]

    # Переберём данные обо всех колонках, пока не найдём ту, в которую мы будем перемещать задачу
    for column in column_data:
        if column['name'] == column_name:
            # И выполним запрос к API для перемещения задачи в нужную колонку
            requests.put(base_url.format('cards') + '/' + moving_task_id + '/idList', data={'value': column['id'], **auth_params})
            print("Задача {} перемещена в колонку {}".format(moving_task_id, column['id']))
            break

def listadd(column_name):
    # Получим данные всех колонок на доске
    column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
    column_name_check = 0
    for column in column_data:
            if column['name'] == column_name:
                column_name_check = 1
    if column_name_check == 1:
        print('колонка {} есть на доске'.format(column_name))
    else:
        response = requests.post(base_url.format('lists'), params={'name': column_name, 'idBoard': board_long_id, **auth_params})
        print('колонка {} создана'.format(column_name))
        print(response.text)

if __name__ == "__main__":
    if len(sys.argv) <= 2:
        read()
    elif sys.argv[1] == 'create':
        create(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'move':
        move(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'listadd':
        listadd(sys.argv[2])