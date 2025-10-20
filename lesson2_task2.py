chislo = int(input("Введите оценку от 1 до 10 "))

if chislo <= 10 and chislo >= 9:
    print("Отлично!")
elif chislo == 8 or chislo == 7:
    print("Хорошо")
elif chislo < 7 and chislo > 5:
    print("Удовлетворительно")
else:
    print("Неудовлетворительно")
