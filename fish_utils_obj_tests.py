import fish_utils, random
from fish_utils import get_fish_from_name

if __name__ == '__main__':
    all_profs = fish_utils.AllProfiles()
    my_profile = all_profs.profile_from_name('epicmushroom.')

    my_profile.add_fish(get_fish_from_name('Catfish'), 27)
    print([str(stx) for stx in my_profile.items])
    all_profs.write_data()