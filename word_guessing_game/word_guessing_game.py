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
        print('\nCongratulations! You guessed the correct word : ' + word)
        break

if attempts == 0 and '_' in guessedWord:
    print('\nYou have run out of attempts! The word was : ' + word)

