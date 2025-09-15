import random

genZ_word_bank = ['rizz', 'ohio', 'skibidi', 'pookie', 'sigma']

word = random.choice(genZ_word_bank)

guessedWord = ['_'] * len(word)

attempts = 10

if attempts > 0:
    print('Current Word: ' + ' '.join(guessedWord))

guess = input('Guess a letter : ').lower()

