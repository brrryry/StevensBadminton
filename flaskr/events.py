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
            
            url = request.form['Event URL']

            events = db.execute(
                f'SELECT * FROM events WHERE url = "{url}"'
            ).fetchall()
            if len(events) > 0: error = "Error: Event has already been recorded."

            eventData = getEventData(url)

            if "error" in eventData: error = "Error: " + eventData["error"]

            
            if error is not None:
                flash(error)
                return render_template('events/record.html')
            else:

                eventTitle = eventData["title"]
                eventURL = url

                db.execute(
                    'INSERT INTO events (url, title, participants, teamsize, rankings) VALUES (?, ?, ?, ?, ?)', (eventURL, eventTitle, ", ".join(eventData["participants"]), eventData["teamsize"], 
                        ",".join([" & ".join(team) for team in eventData["rankings"]]))
                )

                db.commit()

                #loop through each match
                for game in eventData["games"]:
                    recordMatch({
                        "title": f'{eventTitle} ({game.partition("_")[0]})',
                        "tournament": eventData["tournament"],
                        "winner": eventData["games"][game]["winner"],
                        "loser": eventData["games"][game]["loser"],
                    })

                #Record rankings
                if len(eventData["rankings"]) > 0: 
                    recordRankings(eventData["rankings"], eventData["tournament"])
                    flash("Tournament Input Successful!")
                else: flash("League Night Input Successful!")

                return render_template('events/record.html')
    else:
        return render_template('events/record.html')

@bp.route('/view')
def viewTournaments():
    db = get_db()
    events = db.execute(
        f'SELECT * FROM events'
    ).fetchall()
    return render_template('events/view.html', events=events)



