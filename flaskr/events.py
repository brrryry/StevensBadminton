import functools
import json
from flaskr.db import get_db
from flask import jsonify

from flaskr.utils import *

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

bp = Blueprint('event', __name__, url_prefix='/events')


@bp.route('/record', methods=('GET', 'POST'))
def create():
    db = get_db()

    if request.method == 'POST':

        error = None

        if request.form['submit_button'] == 'Submit URL':
            
            url = request.form['Tournament URL']

            tournaments = db.execute(
                f'SELECT * FROM events WHERE url = "{url}"'
            ).fetchall()
            if len(tournaments) > 0: error = "Error: Tournament has already been recorded."

            tournamentData = getTournamentData(url)

            if "error" in tournamentData: 
                if tournamentData["error"] == "Try League Night?":
                    tournamentData = getLeagueData(url)
                    if "error" in tournamentData: error = "Error: " + tournamentData["error"]
                else: error = "Error: " + tournamentData["error"]
            
            if error is not None:
                flash(error)
                return render_template('events/record.html')
            else:
                if 'Tournament' in tournamentData["title"]:
                    tournamentTitle = tournamentData["title"]
                    tournamentURL = url

                    db.execute(
                        'INSERT INTO events (url, title, participants, teamsize, rankings) VALUES (?, ?, ?, ?, ?)', (tournamentURL, tournamentTitle, ", ".join(tournamentData["participants"]), tournamentData["teamsize"], 
                            ",".join([" & ".join(team) for team in tournamentData["rankings"]] ))
                    )

                    db.commit()

                    #loop through each match
                    winnersbracket = tournamentData['winners']
                    for round in winnersbracket:
                        for game in winnersbracket[round]:
                            recordMatch({
                                "title": f'{tournamentTitle} Winners Bracket ({round.capitalize()})',
                                "tournament": 1,
                                "winner": game['winner'],
                                "loser": game['loser']
                            })
                    
                    losersbracket = tournamentData['losers']
                    for round in losersbracket:
                        for game in losersbracket[round]:
                            recordMatch({
                                "title": f'{tournamentTitle} Losers Bracket ({round.capitalize()})',
                                "tournament": 1,
                                "winner": game['winner'],
                                "loser": game['loser']
                            })

                    #Record rankings
                    if tournamentData["tournament"] > 0: recordRankings(tournamentData["rankings"], tournamentData["tournament"])

                    flash("Tournament Input Successful!")
                    return render_template('events/record.html')
                else:
                    leagueTitle = tournamentData["title"]
                    leagueURL = url

                    db.execute(
                        'INSERT INTO events (url, title, participants, teamsize) VALUES (?, ?, ?, ?)', (leagueURL, leagueTitle, ", ".join(tournamentData["participants"]), tournamentData["teamsize"])
                    )

                    db.commit()

                    for group in tournamentData["groups"].keys():
                        for game in tournamentData["groups"][group]:
                            recordMatch({
                                "title": f'{leagueTitle} ({group})',
                                "tournament": 0,
                                "winner": game['winner'],
                                "loser": game['loser']
                            })
                    flash("League Night Input Successful!")
                    return render_template('events/record.html')

    else:
        return render_template('events/record.html')

@bp.route('/view')
def viewTournaments():
    db = get_db()
    tournaments = db.execute(
        f'SELECT * FROM events'
    ).fetchall()
    return render_template('events/view.html', tournaments=tournaments)



