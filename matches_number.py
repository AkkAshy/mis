def smallest_number(matches):

    if matches < 2:
        return "Неволхможно составить число (минимум 2 спички нужны для цифры '1')"

   
    remaining = matches - 2

    num_eights = remaining // 7


    number = '1' + '8' * num_eights

    return number

if __name__ == "__main__":
    matches = 8
    result = smallest_number(matches)
    print(f"Для {matches} спичек самое маленькое число: {result}")