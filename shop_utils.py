from fish_utils import *
from pathlib import Path

SHOP_PATH = Path("values", "shop.json")

class AlreadyOwned(Exception):
    pass

class UserIsBroke(Exception):
    pass

class RequirementError(Exception):
    pass

def shop_database() -> dict:
    with open(SHOP_PATH, 'r') as file:
        shop_dict = json.load(file)
        return shop_dict

def update_shop_file(json_object: list | dict):
    with open(SHOP_PATH, 'w') as file:
        json.dump(json_object, file, indent=4)
        file.truncate()

class ShopItem:
    """
    self will have attribute "special" if it is a consumable. it will be of type "list" and contains the name id of the special
        in the first slot and the count in the second
    self will have attribute requirements if it is an upgrade. it will be a non-empty list of strs with the names of other shop items needed
        to buy it
    """
    VALID_TYPES = ['upgrade', 'consumable', 'misc']

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
        if self.item_type == 'upgrade':
            type_str = "Permanent Upgrade"
        elif self.item_type == 'consumable':
            type_str = "Consumable"

        show_money_price = self.money_price > 0
        show_item_price = len(self.item_price) > 0
        show_prereqs = len(self.requirements) > 0

        result = f'({type_str})\n{self.name}\n*{self.description}*\nCosts:\n'

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

    def sell_to(self, username):
        def can_sell_to(profile: dict) -> bool:
            effective_cost = self.money_price

            if profile is None:
                return False

            for stack in self.item_price:
                effective_cost += stack.count * stack.item.value

                if not any(stack_dict['item']['name'] == stack.item.name and stack_dict['count'] >= stack.count for stack_dict in profile['items']):
                    print(f'Can\'t afford paying: {stack.item.name}')
                    return False

            return effective_cost <= profile['value']

        list_of_profiles = fishing_database()
        user_profile = next((profile for profile in list_of_profiles if profile['username'] == username), None)

        if self.item_type == 'upgrade':
            if not self.name in user_profile['upgrades']:
                if not can_sell_to(user_profile):
                    raise UserIsBroke
            else:
                raise AlreadyOwned

            for req in self.requirements:
                if not req in user_profile['upgrades']:
                    raise RequirementError

            user_profile['upgrades'].append(self.name)

        elif self.item_type == 'consumable':
            if can_sell_to(user_profile):
                add_special(username, self.special[0], count=self.special[1])
            else:
                raise UserIsBroke

        elif self.item_type == 'misc':
            raise ValueError

        update_fish_database(username, fish=get_fish_from_name('Credit'), count=0 - self.money_price, bypass_fish_cd=True)
        for stack in self.item_price:
            update_fish_database(username, fish=get_fish_from_name(stack.item.name), count=0 - stack.count, bypass_fish_cd=True)

        update_fish_file(list_of_profiles)

if __name__ == '__main__':
    # TESTING
    shop = shop_database()

    for item in shop:
        item_obj = ShopItem(**item)
        print(item_obj)

        print("buy this item? (y/n)")
        user_input = input()

        if user_input == 'y':
            try:
                item_obj.sell_to('epicmushroom.')
                print("success")
            except AlreadyOwned:
                print("you can't buy more of that!")
            except UserIsBroke:
                print("you are too broke to buy that!")
            except RequirementError:
                print("you do not have the prerequisite upgrades to buy that!")