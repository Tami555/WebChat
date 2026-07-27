def pascal_to_snake(string: str) -> str:
    """example: ChatParticipants -> chat_participants"""
    result = [string[0].lower()]
    for char in string[1:]:
        if char.isupper():
            result.extend(["_", char.lower()])
        else:
            result.append(char)
    return "".join(result)


def snake_to_camel(string: str) -> str:
    """example: chat_participants -> ChatParticipants"""
    string_split = string.split("_")
    return "".join(word.capitalize() for word in string_split)
