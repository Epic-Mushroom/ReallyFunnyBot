FOLLOWING_CHARACTERS = ['', ' ', '.', '?', '!', '"', "'"]
PRECEDING_CHARACTERS = [' ', '.', ':', '"', "'"]
ENDING_CHARACTERS = ['.', '?', '!', ':', 'bruh']

def strip_punctuation(text: str) -> str:
    found_ending_index = find_substring_index(text, ENDING_CHARACTERS)

    if found_ending_index > -1:
        text = text[:found_ending_index]

    return text.strip()


def file_lines_to_list(file_path) -> list:
    with open(file_path, 'r') as file:
        lines = []

        for line in file:
            to_add = strip_punctuation(line.strip().lower())

            if to_add:
                lines.append(strip_punctuation(line.strip().lower()))

    return lines

def has_any_substring(text: str, words: list[str]) -> bool:
    """Returns False if none of the elements in words are in text, returns True otherwise"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return True

    return False

def find_any_substring(text: str, words: list[str]) -> str | None:
    """Returns the first occurrence in text of an element in words, returns None if none of the
        elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return w

    return None

def find_substring_index(text: str, words: list[str]) -> int:
    """Returns the index of the first occurrence in text of an element in words, returns -1 if none of the
    elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return text.find(w)

    return -1

def has_any_word(text: str, words: list[str]) -> bool:
    """Same thing as has_any_substring except it checks to see if the word is 'isolated' (meaning no Scunthorpe problem)"""
    return index_after_any_word(text, words) > -1

def index_after_any_word(text: str, words: list[str]) -> int:
    """Finds the index immediately after an isolated word is found. If the word isn't found, returns -1"""

    # found_word_index = find_word_index(text, words)
    # index = found_word_index
    # found_word = find_any_substring(text, words)
    #
    # # probably the worst code i have ever written in my entire life what the fuck is this dudeee
    # if index == -1:
    #     return -1
    # else:
    #     check_beginning = (index - 1 != -1) and (text[index - 1] in PRECEDING_CHARACTERS)
    #     check_end = False
    #
    #     if index - 1 == -1:
    #         check_beginning = True
    #
    #     if check_beginning:
    #         try:
    #             check_end = text[index + len(found_word)] in FOLLOWING_CHARACTERS
    #         except IndexError:
    #             check_end = True
    #
    #     if check_end:
    #         return index + len(found_word)
    #     else:
    #         return -1

    for word in words:
        word = word.lower()
        begin_index = text.find(word)

        if begin_index == -1:
            continue

        end_index = begin_index + len(word) - 1

        if (end_index + 1) < len(text) and not text[end_index + 1] in FOLLOWING_CHARACTERS:
            continue

        if (begin_index - 1) >= 0 and not text[begin_index - 1] in PRECEDING_CHARACTERS:
            continue

        return end_index + 1

    return -1

def pluralize(count, word):
    """
    "word" parameter must be singular
    """
    return f'{count} {word}{'s' if count != 1 else ''}'

def seconds_to_descriptive_time(seconds, decimalize = False) -> str:
    if seconds >= 3600:
        hours = seconds // 3600
        time_left = seconds - hours * 3600
        return f'{pluralize(int(hours), 'hour')}{', ' if time_left >= 60 else ' and '}{seconds_to_descriptive_time(time_left, decimalize=decimalize)}'
    elif seconds >= 60:
        minutes = seconds // 60
        time_left = seconds - minutes * 60
        return f'{pluralize(int(minutes), 'minute')}{f' and {seconds_to_descriptive_time(time_left, decimalize=decimalize)}' if time_left > 0 else ''}'
    else:
        return f'{seconds:,.1f} seconds' if decimalize else f'{seconds:,.0f} seconds'

def hours_since(current_time: int, considered_time: int) -> int:
    seconds_since = int(current_time - considered_time)
    return seconds_since // 3600

def days_and_hours_since(current_time: int, considered_time: int) -> tuple:
    hours = hours_since(current_time, considered_time)
    days = hours // 24
    hours = hours - days * 24

    return days, hours

if __name__ == '__main__':
    words_to_look_for = ['a', 'bb', 'hello', 'world']
    test_strings = [
        "aaaaaaaaaa",
        "bb b",
        " bb",
        " bb ",
        " bb. ",
        ""
        """
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
                         lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        lasdjfkalsdjfaklsdjfladksfjalkdfjakldsfjakdsfadsfadsf
        \"\"\"
        kladsjfkladsklasdjfklasdjflkadsjflkasdflkasdfjlakdsjflsdkfjalksdfjasdlkfjadklsfjasdf
        """
    ]
    expected_results = [
        False,
        True,
        True,
        True,
        True,
        False,
        False
    ]

    import time
    start_time = time.time()

    for i in range(len(test_strings)):
        try:
            assert has_any_word(test_strings[i], words_to_look_for) == expected_results[i]

        except AssertionError:
            print(f"Error found in test string: {test_strings[i]}")

    assert has_any_word(" blob", [""])

    time.sleep(0.2)
    print(f"Elapsed time: {time.time() - start_time - 0.2}")
    # lmao ts ain't even accurate cuz of floating point precision oops