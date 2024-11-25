FOLLOWING_CHARACTERS = ['', ' ', '.', '?', '!', '"', "'"]
PRECEDING_CHARACTERS = [' ', '.', ':', '"', "'"]
ENDING_CHARACTERS = ['.', '?', '!', ':', 'bruh']

def strip_punctuation(text: str) -> str:
    found_ending_index = find_word_index(text, ENDING_CHARACTERS)

    if found_ending_index > -1:
        text = text[:found_ending_index]

    return text.strip()

def find_word_bool(text: str, words: list[str]) -> bool:
    """Returns False if none of the elements in words are in text, returns True otherwise"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return True

    return False

def find_isolated_word_bool(text: str, words: list[str]) -> bool:
    """Same thing as find_word_bool except it checks to see if the word is 'isolated' (meaning no Scunthorpe problem)"""
    return find_index_after_word(text, words) > -1

def find_word(text: str, words: list[str]) -> str:
    """Returns the first occurrence in text of an element in words, returns None if none of the
        elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return w

    return None

def find_word_index(text: str, words: list[str]) -> int:
    """Returns the index of the first occurrence in text of an element in words, returns -1 if none of the
    elements in words are in text"""
    text = text.lower()

    for w in words:
        w = w.lower()
        if text.find(w) > -1:
            return text.find(w)

    return -1

def find_index_after_word(text: str, words: list[str]) -> int:
    """Yeah"""

    found_word_index = find_word_index(text, words)
    index = found_word_index
    found_word = find_word(text, words)

    # probably the worst code i have ever written in my entire life what the fuck is this dudeee
    if index == -1:
        return -1
    else:
        check_beginning = (index - 1 != -1) and (text[index - 1] in PRECEDING_CHARACTERS)
        check_end = False

        if index - 1 == -1:
            check_beginning = True

        if check_beginning:
            try:
                check_end = text[index + len(found_word)] in FOLLOWING_CHARACTERS
            except IndexError:
                check_end = True

        if check_end:
            return index + len(found_word)
        else:
            return -1