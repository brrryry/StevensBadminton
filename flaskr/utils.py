import sqlite3
import click
import requests
import validators
from bs4 import BeautifulSoup
import sys
from functools import reduce

from flaskr.db import get_db

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options



"""
JSON Object (getTournamentData)
{
    "winners": {
        "round-16": {
            [
                {
                    "winner": {
                        "name": "Eric G",
                        "score": [11]
                    },
                    "loser": {
                        "name": "Risa",
                        "score": [3]
                    },
                },
                ...
            ],
        },
    },
    "losers": {
    
    }
}

"""
def getLeagueData(url):
    leagueData = {}
    leagueData["tournament"] = 0
    teamSize = 1

    if not validators.url(url): return {"error": "Invalid URL"}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)',
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    #Get Tournament HTML
    with Chrome(options=options) as browser:
        browser.get(url)
        html = browser.page_source

    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("h2", {"class": "bracket-title"})
    if title == None: return {"error": "Invalid URL"}

    title = title.getText()
    leagueData["title"] = title

    #Getting Participants
    participants = []
    participantDivs = soup.find_all("div", {"class": "participant"})
    for participantDiv in participantDivs:
        participant = participantDiv.find("input").get('value')
        participants.append(participant)
    leagueData["participants"] = participants
    
    leagueData["groups"] = {}

    groups = soup.find_all("div", {"class": "group"})
    for group in groups:
        groupTitle = group.get('id').upper()
        groupData = []

        games = group.find_all("div", {"class": "game-completed"})

        for game in games:

            loser = game.find("div", {"class": "slot-loser"})

            loserScore = loser.find("div", {"class": "slot-score-val"})
            if(loserScore.find_all("set")): loserScore = [int(set.getText()) for set in loserScore.find_all("set")]
            else: loserScore = [int(loserScore.getText())]

            loserName = loser.find("div", {"class": "slot-name"}).getText().split(" & ")
            if len(loserName) > 1: teamSize = 2

            winner = game.find("div", {"class": "slot-winner"})

            winnerScore = winner.find("div", {"class": "slot-score-val"})
            if(winnerScore.find_all("set")): winnerScore = [int(set.getText()) for set in winnerScore.find_all("set")]
            else: winnerScore = [int(winnerScore.getText())]

            winnerName = winner.find("div", {"class": "slot-name"}).getText().split(" & ")

            groupData.append({
                "winner": {
                    "name": winnerName,
                    "score": winnerScore
                },
                "loser": {
                    "name": loserName,
                    "score": loserScore
                }
            })
        leagueData["groups"][groupTitle] = groupData

    leagueData["teamsize"] = teamSize

    return leagueData

    

def getTournamentData(url):
    tournamentData = {}
    tournament_value = 0
    teamSize = 1

    if not validators.url(url): return {"error": "Invalid URL"}

    headers = {
        'User-Agent': 'Mozilla/5.0 (Platform; Security; OS-or-CPU; Localization; rv:1.4) Gecko/20030624 Netscape/7.1 (ax)',
    }

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")

    #Get Tournament HTML
    with Chrome(options=options) as browser:
        browser.get(url)
        html = browser.page_source

    soup = BeautifulSoup(html, "html.parser")

    #Get Tournament Title
    title = soup.find("h2", {"class": "bracket-title"})
    if title == None: return {"error": "Invalid URL"}

    title = title.getText()
    tournamentData["title"] = title

    if "Tournament" in title:
        if "Mini" in title: tournament_value += 1
        elif "Major" in title: tournament_value += 2
    else: return {"error": "Try League Night?"}
    tournamentData["tournament"] = tournament_value

    #Getting Participants
    participants = []
    participantDivs = soup.find_all("div", {"class": "participant"})
    for participantDiv in participantDivs:
        participant = participantDiv.find("input").get('value')
        participants.append(participant)
    tournamentData["participants"] = participants

    tournamentData["winners"] = {}    
    tournamentData["losers"] = {}
    #Getting Winners Bracket
    winnersbracket = soup.find("div", {"class": "winners"})
    winnersrounds = winnersbracket.find_all("div", {"class": "round"})
    for round in winnersrounds:
        roundName = round.get('class')[1]
        if 'round-advance' in round.get('class'): roundName += "A"
        if 'round-finals' in round.get('class'): roundName = "Finals"

        roundData = []
        games = round.find_all("div", {"class": "game-completed"})
        for game in games:

            loser = game.find("div", {"class": "slot-loser"})

            loserScore = loser.find("div", {"class": "slot-score-val"})
            if(loserScore.find_all("set")): loserScore = [int(set.getText()) for set in loserScore.find_all("set")]
            else: loserScore = [int(loserScore.getText())]

            loserName = loser.find("div", {"class": "slot-name"}).getText().split(" & ")
            if len(loserName) > 1: teamSize = 2

            winner = game.find("div", {"class": "slot-winner"})

            winnerScore = winner.find("div", {"class": "slot-score-val"})
            if(winnerScore.find_all("set")): winnerScore = [int(set.getText()) for set in winnerScore.find_all("set")]
            else: winnerScore = [int(winnerScore.getText())]

            winnerName = winner.find("div", {"class": "slot-name"}).getText().split(" & ")

            roundData.append({
                "winner": {
                    "name": winnerName,
                    "score": winnerScore
                },
                "loser": {
                    "name": loserName,
                    "score": loserScore
                }
            })

        tournamentData["winners"][roundName] = roundData

    #Getting Losers Bracket
    losersbracket = soup.find("div", {"class": "losers"})
    losersrounds = losersbracket.find_all("div", {"class": "round"})
    for round in losersrounds:
        roundName = round.get('class')[1]
        if 'round-advance' in round.get('class'): roundName += "A"

        roundData = []
        games = round.find_all("div", {"class": "game-completed"})
        for game in games:

            loser = game.find("div", {"class": "slot-loser"})

            loserScore = loser.find("div", {"class": "slot-score-val"})
            if(loserScore.find_all("set")): loserScore = [set.getText() for set in loserScore.find_all("set")]
            else: loserScore = [loserScore.getText()]

            loserName = loser.find("div", {"class": "slot-name"}).getText().split(" & ")

            winner = game.find("div", {"class": "slot-winner"})

            winnerScore = winner.find("div", {"class": "slot-score-val"})
            if(winnerScore.find_all("set")): winnerScore = [set.getText() for set in winnerScore.find_all("set")]
            else: winnerScore = [winnerScore.getText()]

            winnerName = winner.find("div", {"class": "slot-name"}).getText().split(" & ")

            roundData.append({
                "winner": {
                    "name": winnerName,
                    "score": winnerScore
                },
                "loser": {
                    "name": loserName,
                    "score": loserScore
                }
            })

        tournamentData["losers"][roundName] = roundData

    #Getting Final Rankings
    rankings = []
    for round in tournamentData["losers"]:
        for game in tournamentData["losers"][round]:
            rankings.append(game['loser']['name'])
    rankings.append(tournamentData["winners"]["Finals"][-1]["loser"]["name"])
    rankings.append(tournamentData["winners"]["Finals"][-1]["winner"]["name"])
    tournamentData["rankings"] = rankings[::-1]

    tournamentData["teamsize"] = teamSize

    return tournamentData


#oldElos will be a value of two ELOS [winner, loser], returns the points gained/lost
def calculateELO(winnerELO, loserELO):
    k_score = 32
    return round(k_score * 1/(1 + pow(10, (winnerELO - loserELO) / 400)), 3)


def createPlayer(name):
    db = get_db()
    db.execute(f'INSERT INTO players (name, picture, bp, elo) VALUES (?, ?, ?, ?)', (name, "", 0, 800))
    db.commit()

def getPlayerByName(name):
    db = get_db()
    player = db.execute(
        f'SELECT * FROM players WHERE name="{name}"'
    ).fetchone()
    if player == None: 
        createPlayer(name)
        player = getPlayerByName(name)
    return dict(zip(player.keys(), player))

def getPlayerbyID(id):
    player = get_db().execute(
        f'SELECT * FROM players WHERE id="{id}"'
    ).fetchone()
    if player == None: return None
    else: return dict(zip(player.keys(), player))
    

def recordRankings(rankings, tournamentValue):
    db = get_db()
    pointValues = [2000] + [1200] + [720] + [360] + [180 for i in range(2)] + [90 for i in range(2)] + [50 for i in range(4)] + [30 for i in range(4)] #places 1-15
    pointValues = [value / (3 - tournamentValue) for value in pointValues]

    for i in range(min(len(pointValues), len(rankings))):
        #update each bp
        points = pointValues[i]
        team = rankings[i]
        for player in team:
            db.execute(f'UPDATE players SET bp = bp + {points} WHERE name = "{player}"')

    db.commit()
    return 1



"""
matchData format:

{
    "title": '01/30/23 Mini Tournament Winners Round-16',
    "tournament": 1,
    "winner": {
        "name": "Eric G",
        "score": [11]
    },
    "loser": {
        "name": "Risa",
        "score": [3]
    }
}
"""
def recordMatch(matchData):
    db = get_db()
    matchTitle = matchData["title"]
    winningTeam = matchData["winner"]
    losingTeam = matchData["loser"]

    for winner in winningTeam["name"]:
        winnername = getPlayerByName(winner)
        if winnername == None:
            db.execute(f'INSERT INTO players (name, picture, bp, elo) VALUES (?, ?, ?, ?)', (winner, "", 0, 800))
            db.commit()
    for loser in losingTeam["name"]:
        losername = getPlayerByName(loser)
        if losername == None:
            db.execute(f'INSERT INTO players (name, picture, bp, elo) VALUES (?, ?, ?, ?)', (loser, "", 0, 800))
            db.commit()

    winnerELO = sum([getPlayerByName(x)["elo"] for x in winningTeam["name"]]) / len(winningTeam["name"])
    loserELO = sum([getPlayerByName(x)["elo"] for x in winningTeam["name"]]) / len(losingTeam["name"])

    eloChange = calculateELO(winnerELO, loserELO)
    
    db = get_db()

    for winner in winningTeam["name"]:
        db.execute(f'UPDATE players SET elo = elo + {eloChange} WHERE name = "{winner}"')
    for loser in losingTeam["name"]:
        db.execute(f'UPDATE players SET elo = elo - {eloChange} WHERE name = "{loser}"')

    if len(winningTeam["name"]) == 1:
        db.execute(f'INSERT INTO matches1 (title, winner, loser, winnerscore, loserscore, tournament) VALUES (?, ?, ?, ?, ?, ?)', 
                   (matchTitle, 
                    winningTeam["name"][0], 
                    losingTeam["name"][0], 
                    " ".join([str(x) for x in winningTeam["score"]]),
                    " ".join([str(x) for x in losingTeam["score"]]),
                    matchData["tournament"])
        )
    elif len(winningTeam["name"]) == 2:
        db.execute(f'INSERT INTO matches2 (title, winner1, winner2, loser1, loser2, winnerscore, loserscore, tournament) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', 
                   (matchTitle, 
                    winningTeam["name"][0], 
                    winningTeam["name"][1],
                    losingTeam["name"][0], 
                    losingTeam["name"][1],
                    " ".join([str(x) for x in winningTeam["score"]]),
                    " ".join([str(x) for x in losingTeam["score"]]),
                    matchData["tournament"])
        )
    db.commit()

    return 1

def getMatchHistory1(id):
    db = get_db()
    name = getPlayerbyID(id)["name"]
    matches = db.execute(
        f'SELECT * FROM matches1 WHERE winner="{name}" OR loser="{name}"'
    ).fetchall()
    
    matches = [dict(zip(match.keys(), match)) for match in matches]
    for match in matches:
        match["winner"] = {
            "name": match["winner"],
            "score": match["winnerscore"]
        }
        match["loser"] = {
            "name": match["loser"],
            "score": match["loserscore"]
        }

    return matches

def getMatchHistory2(id):
    db = get_db()
    name = getPlayerbyID(id)["name"]
    matches = db.execute(
        f'SELECT * FROM matches2 WHERE winner1="{name}" OR winner2="{name}" OR loser1="{name}" OR loser2="{name}"'
    ).fetchall()
    
    matches = [dict(zip(match.keys(), match)) for match in matches]
    for match in matches:
        match["winner"] = {
            "name": " & ".join([match["winner1"], match["winner2"]]),
            "score": match["winnerscore"]
        }
        match["loser"] = {
            "name": " & ".join([match["loser1"], match["loser2"]]),
            "score": match["loserscore"]
        }

    return matches

def getLeaderboardByBP():
    db = get_db()
    leaderboard = db.execute(
        "SELECT * FROM players ORDER BY bp DESC"
    ).fetchall()
    return leaderboard

def getLeaderboardByELO():
    db = get_db()
    leaderboard = db.execute(
        "SELECT * FROM players ORDER BY elo DESC"
    ).fetchall()
    return leaderboard


