chislo = int(input("Введите оценку от 1 до 10 "))

if chislo <= 10 and chislo >= 9:
    print("Отлично!")
elif chislo == 8 or chislo == 7:
    print("Хорошо")
elif chislo < 7 and chislo > 5:
    print("Удовлетворительно")
elif chislo <= 5 and chislo >=1:
    print("Неудовлетворительно")
else:
    print("Ваша оценка некорректна, за пределами диапазона от 1 до 10!!!")