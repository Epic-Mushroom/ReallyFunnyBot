from pathlib import Path
import json, fish_utils

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
    self will have attribute requirements if it is an upgrade or consumable. it will be a non-empty list of strs
        with the names of other upgrades needed to buy it
    upgrades will NOT have the attribute "special"
    """
    VALID_TYPES = ['upgrade', 'consumable', 'misc']

    def __init__(self, **kwargs):
        for key, value in kwargs.items():

            if key == 'item_price':
                stack_list = []

                for stack_dict in value:
                    temp_stack = fish_utils.Stack(**stack_dict)
                    stack_list.append(temp_stack)

                self.item_price = stack_list

            else:
                setattr(self, key, value)

        self.effective_cost = self.money_price + sum([stk.item.value * stk.count for stk in self.item_price])

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

        result = f'[ID: {self.id}]\n**{self.name}** ({type_str})\n*{self.description}*\nCosts:\n'

        if show_money_price:
            result += f'{self.money_price} moneys\n'
        if show_item_price:
            for stack in self.item_price:
                result += f'{stack.__str__()}\n'

            result += f'*Effective cost: {self.effective_cost} moneys*\n'

        if show_prereqs:
            result += f'\nRequires:\n'
            for req in self.requirements:
                result += f'{req}\n'

        return result

    def sell_to(self, username):
        def can_sell_to(profile: dict) -> bool:
            if profile is None:
                return False

            for stack in self.item_price:
                if not any(stack_dict['item']['name'] == stack.item.name and stack_dict['count'] >= stack.count for stack_dict in profile['items']):
                    print(f'Can\'t afford paying: {stack.item.name}')
                    return False

            return self.effective_cost <= profile['value']

        list_of_profiles = fish_utils.fishing_database()
        user_profile = next((profile for profile in list_of_profiles if profile['username'] == username), None)

        for req in self.requirements:
            if not req in user_profile['upgrades']:
                raise RequirementError

        if self.item_type == 'upgrade':
            if not self.name in user_profile['upgrades']:
                if not can_sell_to(user_profile):
                    raise UserIsBroke
            else:
                raise AlreadyOwned

            user_profile['upgrades'].append(self.name)

        elif self.item_type == 'consumable':
            if can_sell_to(user_profile):
                fish_utils.add_special(username, self.special[0], count=self.special[1])
            else:
                raise UserIsBroke

        elif self.item_type == 'misc':
            raise ValueError

        # writes upgrades to fishing.json
        fish_utils.update_fish_file(list_of_profiles)

        fish_utils.update_fish_database(username, fish=fish_utils.get_fish_from_name('Credit'), count=0 - self.money_price, bypass_fish_cd=True)
        for stack in self.item_price:
            fish_utils.update_fish_database(username, fish=fish_utils.get_fish_from_name(stack.item.name), count=0 - stack.count, bypass_fish_cd=True)
            # print(0 - stack.count, "of item was deleted from inv")

def get_list_of_shop_items() -> list[ShopItem]:
    shop = shop_database()
    shop_items = []

    for item in shop:
        shop_items.append(ShopItem(**item))

    return shop_items

def get_shop_item_from_id(id: int):
    shop_items = get_list_of_shop_items()
    return next((item for item in shop_items if item.id == id), None)

def max_page() -> int:
    shop_items = get_list_of_shop_items()
    return max([shop_item.page for shop_item in shop_items])

def display_shop_page(page=1) -> str:
    shop_items = get_list_of_shop_items()
    result = ''

    for item in shop_items:
        if item.page == page:
            result += f'{str(item)}\n'

    # result += f'Page {page} of {max_page()}'
    result += f'*Type "go shop [page number]" to navigate to a different page*\n'
    result += f'*Type "go buy [item ID]" to buy that item*'
    return result

def get_user_upgrades(username) -> list[str]:
    list_of_profiles = fish_utils.fishing_database()
    user_profile = next((profile for profile in list_of_profiles if profile['username'] == username), None)

    if user_profile is not None:
        return user_profile['upgrades']
    else:
        return []

def test_purchasing_items():
    for item_obj in get_list_of_shop_items():
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

if __name__ == '__main__':
    # TESTING
    print(get_shop_item_from_id(4))