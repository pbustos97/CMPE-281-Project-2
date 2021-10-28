def line_has_number(line:str):
    for char in line:
        if char.isdigit():
            return True
    return False