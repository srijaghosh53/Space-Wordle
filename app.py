from flask import Flask, render_template, request, redirect
import random

app = Flask(__name__)

# --------------------------------------------------
# Load ALL valid 5-letter words
# These words can be used as player guesses
# --------------------------------------------------

with open("valid_words.txt", "r") as file:
    valid_words = set(
        word.strip().upper()
        for word in file
        if len(word.strip()) == 5
    )


# --------------------------------------------------
# Load COMMON 5-letter words
# These words will be used as secret words only
# --------------------------------------------------

with open("common_words.txt", "r") as file:
    common_words = [
        word.strip().upper()
        for word in file
        if len(word.strip()) == 5
    ]


# Choose a common word as the secret word
word = random.choice(common_words)

attempts = []
game_over = False
message = ""


@app.route("/", methods=["GET", "POST"])
def index():

    global attempts, game_over, message

    if request.method == "POST" and not game_over:

        # Get the user's guess
        guess = request.form["guess"].upper().strip()

        # Check if guess has exactly 5 letters
        if len(guess) != 5 or not guess.isalpha():

            message = "Please enter a 5-letter word!"

        # Check if the guess is a real word
        elif guess not in valid_words:

            message = "❌ That's not a valid word!"

        else:

            # Start with all letters marked as absent
            result = ["absent"] * 5

            # Keep track of letters that are still available
            # in the secret word
            remaining_letters = list(word)


            # --------------------------------------------------
            # FIRST PASS
            # Check for correct letter + correct position
            # --------------------------------------------------

            for i in range(5):

                if guess[i] == word[i]:

                    result[i] = "correct"

                    # Remove the matched letter so it
                    # cannot be counted again
                    remaining_letters.remove(guess[i])


            # --------------------------------------------------
            # SECOND PASS
            # Check for correct letter + wrong position
            # --------------------------------------------------

            for i in range(5):

                # Skip letters already marked correct
                if result[i] == "correct":
                    continue

                # Check whether the letter exists in the
                # remaining letters of the secret word
                if guess[i] in remaining_letters:

                    result[i] = "present"

                    # Remove it so it cannot be counted twice
                    remaining_letters.remove(guess[i])


            # Save the guess
            attempts.append({
                "guess": guess,
                "result": result
            })


            # --------------------------------------------------
            # Check if player won
            # --------------------------------------------------

            if guess == word:

                message = "🎉 You Won!"
                game_over = True


            # --------------------------------------------------
            # Check if player used all 7 attempts
            # --------------------------------------------------

            elif len(attempts) >= 7:

                message = f"😢 Game Over! The word was {word}."
                game_over = True


            else:

                message = ""


    return render_template(
        "index.html",
        attempts=attempts,
        message=message,
        game_over=game_over
    )


@app.route("/restart")
def restart():

    global word, attempts, game_over, message

    # Choose a NEW common word
    word = random.choice(common_words)

    # Reset the game
    attempts = []
    game_over = False
    message = ""

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True, port=5001)