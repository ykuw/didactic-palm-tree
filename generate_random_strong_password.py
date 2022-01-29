import string
import random

number_of_characters = int(input("Enter the number of characters for the password: "))

pw = "".join(
    random.SystemRandom().choice(
        string.ascii_uppercase
        + string.ascii_lowercase
        + string.digits
        + string.punctuation
    )
    for _ in range(number_of_characters)
)

print(pw)
