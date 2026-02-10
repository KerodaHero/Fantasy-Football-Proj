import requests
import mysql.connector
import os
from dotenv import load_dotenv

#Load your password from the .env file
load_dotenv()

def update_player_database():
    #Connect to MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=os.getenv("DB_PASSWORD"),
        database="fantasy_draft_db"
    )
    cursor = db.cursor()

    #Get data from Sleeper API
    print("Fetching player data from Sleeper...")
    response = requests.get("https://api.sleeper.app/v1/players/nfl")
    all_players = response.json()

    #Prepare data for MySQL
    player_list = []
    for p_id, info in all_players.items():
        if info['active'] and info['position']:
            player_list.append((
                info['full_name'],
                info['position'],
                info['team'],
                p_id
            ))

    #Push to MySQL
    sql = """
    INSERT INTO players (name, position, team, player_id_external)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    team = VALUES(team), 
    position = VALUES(position);
    """
    
    cursor.executemany(sql, player_list)
    db.commit()
    print(f"Success! {cursor.rowcount} players updated.")
    
    cursor.close()
    db.close()

if __name__ == "__main__":
    update_player_database()