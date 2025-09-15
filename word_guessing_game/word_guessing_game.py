import random

genZ_word_bank = ['rizz', 'ohio', 'skibidi', 'pookie', 'sigma']

word = random.choice(genZ_word_bank)

guessedWord = ['_'] * len(word)

attempts = 10

while attempts > 0:
    print('Current Word: ' + ' '.join(guessedWord))

    guess = input('Guess a letter : ').lower()

    if guess in word:
        for i in range(len(word)):
            if word[i] == guess:
                guessedWord[i] = guess
        print("Great Guess")
    else:
        attempts = attempts - 1
        print("Wrong Guess! Attepts left: " + str(attempts))

        if '_' not in guessedWord:
            print('\n Congratulations! You guessed the correct word' + word)
            break

