import random


def crypt_char(char):
    map = '@./=#$%&:,;_-|0123456789abcd3fghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
    i = 0
    for ch in map:
        if ch == char:
            return map[len(map) - 1 - i]
        i+=1
    return char

def encrypt(text):
    i = 0
    cryptText = ''
    for char in text:
        rnd = random.randrange(1,9,1)
        cryptText += crypt_char(char) + crypt_char(str(rnd))
        i+=1
    return cryptText

def decrypt(text):
    i = 0
    decryptText = ''
    while i < len(text):
        decryptText += crypt_char(text[i])
        i+=2
    return decryptText


proxy = encrypt('181.225.253.17:3435')
print(proxy)