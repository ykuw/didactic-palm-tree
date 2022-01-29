import random
import string

numbers_of_characters = int(input("Enter the number of characters for the pin: "))

id = "".join(random.SystemRandom().choice(string.digits) for _ in range(numbers_of_characters))

print(id)
