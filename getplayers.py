import requests
import pandas as pd

# Step 1: Fetch player data from the Sleeper API
players_url = 'https://api.sleeper.app/v1/players/nfl'
players_response = requests.get(players_url)

if players_response.status_code == 200:
    players_data = players_response.json()
    if not players_data:
        print("No player data found.")
        exit()
else:
    print(f"Error fetching player data: {players_response.status_code}")
    exit()

# Step 2: Convert the player data (a dictionary) into a DataFrame
# The response is a dictionary where each key is a player_id and the value is another dictionary with player info
player_info_list = []

for player_id, player_info in players_data.items():
    # Add the player_id as a field in the player_info dictionary
    player_info['player_id'] = player_id
    player_info_list.append(player_info)

# Convert the list of player information dictionaries into a DataFrame
df = pd.DataFrame(player_info_list)
# Step 3: Write the DataFrame to a CSV file
df.to_csv('nfl_players.csv', index=False)

print("Player data has been written to nfl_players.csv")
