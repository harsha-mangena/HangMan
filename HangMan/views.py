from django.http import HttpResponse
from django.shortcuts import render
import string, logging, requests
#configuration value
NUMGUESSES = 6

def newGame(request):
    logger = logging.getLogger('django')
    wins = 0
    games = 0
    if request.method == 'GET':
        # save current number of wins and games played for state
        if 'wins' in request.session.keys():
            wins = request.session['wins']
        if 'games' in request.session.keys():
            games = request.session['games']
        # if win best 2 out of 3 send to final win
        if games >= 2 and wins > 1:
            request.session['wins'] = 0
            request.session['games'] = 0
            return render(request, "finalWin.html")
        # if lose best 2 out of 3 send to final lose
        elif (games == 3 and wins <= 1) or (games == 2 and wins == 0):
            request.session['wins'] = 0
            request.session['games'] = 0
            return render(request, "finalLose.html")
        # else continue the games
        request.session.flush()
        request.session['wins'] = wins
        request.session['games'] = games
        # send list of letters to make buttons
        alph = list(string.ascii_lowercase)
        request.session['alph'] = alph
        # store answer from random word api
        answer = requests.get("https://random-word-api.herokuapp.com/word").text
        answer = answer[2:len(answer) - 2]
        # answer = 'test'
        # logger.info(answer[2:len(answer) - 2])
        request.session['answer'] = answer
        # store record of guessed answers
        request.session['guessed'] = []
        # store record of number of incorrect guesses made
        request.session['guessNum'] = 0
        # store record of current guess
        request.session['cur_guess'] = ''
        # store record of number correct guesses
        request.session['correct'] = 0
        # store record of previous guess
        request.session['prev_guess'] = ''
        # store game status
        request.session['status'] = 1
        return render(request, "mainPage.html")
    else:
        return buttonPress(request)


def buttonPress(request):
    logger = logging.getLogger('django')
    # get the guessed letter from the request
    cur_guess = request.POST['letter']
    # put guessed letter into guessed list
    guessed = request.session['guessed']
    guessed.append(cur_guess)
    request.session['guessed'] = guessed
    # get the answer from the request
    answer = request.session['answer']
    # get the previous guess from the request
    prev = request.session['prev_guess']
    # prevents guess incrementing due to refreshing the browser
    if cur_guess != prev:
        # increment correct counter
        if cur_guess in answer:
            request.session['correct'] += 1
        request.session['guessNum'] += 1
    request.session['prev_guess'] = cur_guess
    if (request.session['guessNum'] - request.session['correct']) == NUMGUESSES and request.session['correct'] != len(answer):
        request.session['games'] += 1
        return render(request, "lose.html")
    elif request.session['correct'] == len(set(answer)):
        request.session['games'] += 1
        request.session['wins'] += 1
        return render(request, "win.html")
    else:
        return render(request, "mainPage.html")