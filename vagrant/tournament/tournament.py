#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    DB = connect()
    cursor = DB.cursor()
    query = "DELETE FROM matches"
    cursor.execute(query)
    DB.commit()
    DB.close()



def deletePlayers():
    """Remove all the player records from the database."""
    DB = connect()
    cursor = DB.cursor()
    query = "DELETE FROM players"
    cursor.execute(query)
    DB.commit()
    DB.close()


def countPlayers():
    """Returns the number of players currently registered."""
    DB = connect()
    cursor = DB.cursor()
    query = "SELECT count(*) as number FROM players"
    cursor.execute(query)
    result = cursor.fetchall()[0][0]
    DB.close()

    return result


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    DB = connect()
    cursor = DB.cursor()
    query = "INSERT INTO players (name) VALUES (%s)"
    cursor.execute(query, (name,))
    DB.commit()
    DB.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """


    # matches:
    #  host | guest | winner
    # ------+-------+-------
    #     3 |     4 |      3


    #  id | wins
    # ----+-----
    #   4 |   0
    #   3 |   1

    winQ = """
        SELECT players.id, count(matches.winner) AS wins
        FROM players LEFT JOIN matches ON players.id = matches.winner
        GROUP BY players.id
        ORDER BY wins DESC;
    """

    #  id | num
    # ----+-----
    #   4 |   1
    #   3 |   1

    numQ = """
        SELECT players.id, count(match_players) AS num
        FROM players LEFT JOIN match_players ON players.id = host OR players.id = guest
        GROUP BY players.id;
    """

    #  id |       name       | wins | num
    # ----+------------------+------+-----
    #   4 | Randy Schwartz   |    0 |   1
    #   3 | Melpomene Murray |    1 |   1

    query = """
        SELECT players.id, players.name, wins, num
        FROM players, (
                SELECT players.id, count(matches.winner) AS wins
                FROM players LEFT JOIN matches ON players.id = matches.winner
                GROUP BY players.id
            ) AS winsQ, (
                SELECT players.id, count(match_players) AS num
                FROM players LEFT JOIN match_players ON players.id = host OR players.id = guest
                GROUP BY players.id
            ) AS numsQ
        WHERE players.id = winsQ.id and players.id = numsQ.id
        ORDER BY wins DESC;
    """

    DB = connect()
    cursor = DB.cursor()
    cursor.execute(query)
    # Get all results
    rows = cursor.fetchall()
    DB.close()

    return rows


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    DB = connect()
    cursor = DB.cursor()
    query = "INSERT INTO matches (host, guest, winner) VALUES (%s, %s, %s)"
    cursor.execute(query, (winner, loser, winner))
    DB.commit()
    DB.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    standings = playerStandings()
    pairings = list()

    i = 0
    while i < len(standings) - 1:
        tmp = (standings[i][0], standings[i][1],
            standings[i + 1][0], standings[i + 1][1])

        pairings.append(tmp)
        i += 2

    # print pairings
    return pairings
