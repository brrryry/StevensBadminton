import os
import json

from flask import Flask, request, render_template

from flaskr.utils import *

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='dev', 
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db
    db.init_app(app)
    
    from . import events
    app.register_blueprint(events.bp)

    with app.app_context():
        #print(json.dumps(getEventData('https://brackethq.com/b/zrsnb/'), indent=4))
        pass

    @app.route('/')
    def home():
        return render_template("index.html")
    
    @app.route('/shuttlecock')
    def shuttlecock():
        return 'Why are you here???????'

    @app.route('/leaderboard')
    def getLeaderboard():
        leaderboard = getLeaderboardByBP()
        if 'sortBy' in request.args and request.args['sortBy'] == 'elo':
            leaderboard = getLeaderboardByELO()
        return render_template("leaderboard.html", leaderboard=leaderboard)

    @app.route('/profile/<int:id>')
    def profile(id):

        targetPlayer = getPlayerbyID(id)
        if targetPlayer == None:
            return render_template("error.html", error="Invalid Player ID.")
        else:
            matchhistory1 = getMatchHistory1(id)
            matchhistory2 = getMatchHistory2(id)
            return render_template("profile.html", player=targetPlayer, matchhistory1=matchhistory1, matchhistory2 = matchhistory2)

    return app