from fish_utils import *
from pathlib import Path

SHOP_PATH = Path("values", "shop.json")

def shop_database() -> dict:
    with open(SHOP_PATH, 'r') as file:
        shop_dict = json.load(file)
        return shop_dict

def update_shop_file(json_object: list | dict):
    with open(SHOP_PATH, 'w') as file:
        json.dump(json_object, file, indent=4)
        file.truncate()

class ShopItem:
    VALID_TYPES = ['perm_upgrade', 'consumable', 'misc']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():

            if key == 'item_price':
                stack_list = []

                for stack_dict in value:
                    temp_stack = Stack(**stack_dict)
                    stack_list.append(temp_stack)

                self.item_price = stack_list

            else:
                setattr(self, key, value)

    def __str__(self):
        result = ''

        type_str = "Other"
        if self.item_type == 'perm_upgrade':
            type_str = "Permanent Upgrade"
        elif self.item_type == 'consumable':
            type_str = "Consumable"

        show_money_price = self.money_price > 0
        show_item_price = len(self.item_price) > 0
        show_prereqs = len(self.requirements) > 0

        result = f'({type_str})\n{self.name}\nCosts:\n'

        if show_money_price:
            result += f'{self.money_price} moneys\n'
        if show_item_price:
            for stack in self.item_price:
                result += f'{stack.__str__()}\n'

        if show_prereqs:
            result += f'\nRequires:\n'
            for req in self.requirements:
                result += f'{req}\n'

        return result

if __name__ == '__main__':
    # TESTING
    shop = shop_database()

    for item in shop:
        item_obj = ShopItem(**item)
        print(item_obj)