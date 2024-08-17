filename = "example.txt"

# Текст, который нужно записать
content = "Привет, мир! Это пример записи в файл."

# Создание и открытие файла для записи
with open(filename, "w") as file:
    # Запись текста в файл
    file.write(content)