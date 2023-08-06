import random

def generate(length=8):
    "Generate a random password."
    alpha = 'abcdefghkmnopqrstuvwxyz'
    digits = '0123456789'
    alphabet = alpha + digits
    size = len(alphabet)
    password = ''
    for ii in range(length):
        randindex = random.randint(0, size-1)
        char = alphabet[randindex]
        password += char
    return password

