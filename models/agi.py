import random
import os

# Типа наши укрупнённые группы
translate_agg_to_group = {
    'Одежда и акссесуары': ['flowers', 'jawelery', 'clothes'],
    'Образование': ['education'],
    'Здоровье': ['medicine', 'eaptek'],
    'Еда и сервисы': ['food', 'service', 'pets', 'others'],
    'Дом и маркетплейсы': ['home', 'marketplace'],
    'Поездки и путешествия': ['travel', 'transport', 'car']
}

all_group = [path.name for path in os.scandir('offers/')]


class AGIModel:
    def __init__(self,
                 all_group: list[str],
                 select_group: list[str]):

        self.unselect_group = [elem for elem in all_group
                               if elem not in set(select_group)]
        self.unselect_dict_group = {elem: 1 / len(self.unselect_group) for elem in self.unselect_group}

        self.select_group = select_group
        self.select_dict_group = {elem: 1 / len(select_group) for elem in select_group}

        self.main_counter_elem = {key: count for key, count in zip(all_group,
                                   [len(list(os.scandir('offers/' + path + '/')))
                                    for path in all_group])}
        
        self.user_counter_elem = {key: 0 for key in all_group}

        tmp_dict = {}
        for key in all_group:
            base = []
            for elem in os.scandir('offers/' + key + '/'):
                base.append(elem.name)
            tmp_dict[key] = set(base)

        self.data = tmp_dict

    def update(self,
               user_item_group: str,
               action: int):
        
        # Проверяем на наличие в списке элементов
        if self.main_counter_elem[user_item_group] <= self.user_counter_elem[user_item_group]:
            zero_weight = True
        else:
            zero_weight = False

        # Функция для валидации весов
        def weight_calc(weight):
            if zero_weight:
                return 0
            
            if weight >= 0.9:
                return 0.9
            elif weight <= 0.05:
                return 0.05
            else:
                return weight

        # Преобразуем значения для работы через мат.операции
        if action == 0:
            action = -1

        # Выполняем пересчёт весов
        if user_item_group in self.select_dict_group:
            self.select_dict_group[user_item_group] = weight_calc(self.select_dict_group[user_item_group] + 0.1*action)

        elif user_item_group in self.unselect_dict_group:
            if action > 0:
                self.select_dict_group[user_item_group] = weight_calc(0.1*action)
                del self.unselect_dict_group[user_item_group]

        else:
            raise Exception

    def next_element(self):
        # Выбираем одну из групп (однорукий бандит)
        agg_group = random.choices([self.unselect_dict_group,
                                    self.select_dict_group],
                                   weights=[0.3, 0.7])[0]

        # Выбирай подгруппу, основываясь на весах
        output_group = random.choices(list(agg_group.keys()),
                                      weights=list(agg_group.values()))[0]
        
        #   File "C:\Users\Goldian\AppData\Local\Programs\Python\Python311\Lib\random.py", line 373, in choice
    # raise IndexError('Cannot choose from an empty sequence')
        # Выбираем элемент из этой подгруппы
        flag = False
        for _ in range(5):
            try:
                output_group = random.choices(list(agg_group.keys()),
                                        weights=list(agg_group.values()))[0]
                output_elem = random.choice(list(self.data[output_group]))
            except IndexError:
                flag = True
                continue
            else:
                flag = False
                break
        
        if flag:
            return None, None


        # Пополняем количество просмотренных элементов, удаляем уже просмотренные
        self.user_counter_elem[output_group] += 1
        self.data[output_group].remove(output_elem)
        print(output_elem)
        return output_elem, output_group


model = AGIModel(all_group=['car', 'clothes', 'flowers'],
                 select_group=['clothes'])
qq = model.next_element()
model.update(qq[1], 2)
qq = model.next_element()
