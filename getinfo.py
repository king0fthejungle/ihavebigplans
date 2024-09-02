import requests
import pandas as pd

# Replace with your specific league ID
league_id = '920762316600217600'

# Step 1: Fetch league members
members_url = f'https://api.sleeper.app/v1/league/{league_id}/users'
members_response = requests.get(members_url)

if members_response.status_code == 200:
    members_data = members_response.json()
    if not members_data:
        print("No members found in the league.")
        exit()
else:
    print(f"Error fetching league members: {members_response.status_code}")
    exit()

# Prepare a list to collect all user information
user_info_list = []

# To track all metadata keys for dynamic column creation
metadata_keys = set()

# Step 2: Get detailed information for each user
for user in members_data:
    user_id = user['user_id']
    username = user['display_name']
    avatar = user['avatar']  # This is the avatar ID (image), which can be used to generate a URL if needed
    is_owner = user.get('is_owner', False)
    is_co_owner = user.get('is_co_owner', False)
    metadata = user.get('metadata', {})

    # Add metadata keys to the set
    metadata_keys.update(metadata.keys())

    # Collecting information into a dictionary
    user_info = {
        'User ID': user_id,
        'Username': username,
        'Avatar': avatar,
        'Is Owner': is_owner,
        'Is Co-Owner': is_co_owner,
    }

    # Add metadata fields to the user_info dictionary
    user_info.update(metadata)
    
    user_info_list.append(user_info)

# Step 3: Create a DataFrame with the collected user information
user_df = pd.DataFrame(user_info_list)

# Step 4: Ensure all metadata keys have corresponding columns in the DataFrame
for key in metadata_keys:
    if key not in user_df.columns:
        user_df[key] = None

# Populate the user DataFrame with metadata values
for i, user in enumerate(members_data):
    metadata = user.get('metadata', {})
    for key in metadata_keys:
        user_df.at[i, key] = metadata.get(key, None)

# Step 5: Fetch roster data for the league
rosters_url = f'https://api.sleeper.app/v1/league/{league_id}/rosters'
rosters_response = requests.get(rosters_url)

if rosters_response.status_code == 200:
    rosters_data = rosters_response.json()
    if not rosters_data:
        print("No rosters found in the league.")
        exit()
else:
    print(f"Error fetching rosters: {rosters_response.status_code}")
    exit()

# Load NFL players data
nfl_players = pd.read_csv('nfl_players.csv')

# Create a mapping from player_id to player details
player_id_to_details = nfl_players.set_index('player_id')[['first_name', 'last_name', 'height', 'weight', 'position']].to_dict('index')

# Initialize a list to hold all rows for DataFrame
data_rows = []

# Process each roster
for roster in rosters_data:
    owner_id = roster['owner_id']
    players = roster.get('players', [])
    settings = roster.get('settings', {})  # Extract settings block if it exists
    
    # Add settings columns if they don't exist in the DataFrame
    if settings:
        for key in settings.keys():
            column_name = f'setting_{key}'
            if column_name not in user_df.columns:
                user_df[column_name] = None
    
    # Create row with player details
    roster_row = {'User ID': owner_id}
    
    for i, player_id in enumerate(players):
        column_name = f'Roster Spot {i + 1}'
        if column_name not in user_df.columns:
            user_df[column_name] = None
        
        # Get player's details
        player_details = player_id_to_details.get(player_id, {})
        first_name = player_details.get('first_name', 'Unknown')
        last_name = player_details.get('last_name', 'Unknown')
        height = player_details.get('height', 'Unknown')
        weight = player_details.get('weight', 'Unknown')
        position = player_details.get('position', 'Unknown')
        
        # Format the player's full details
        full_details = f"{first_name} {last_name} - Height: {height}, Weight: {weight}, Position: {position}"
        
        # Assign player's details to the appropriate user's roster spot
        roster_row[column_name] = full_details
    
    # Add settings to the row
    if settings:
        for key, value in settings.items():
            column_name = f'setting_{key}'
            roster_row[column_name] = value

    # Append the row to the list of rows
    data_rows.append(roster_row)

# Convert list of rows to DataFrame
roster_df = pd.DataFrame(data_rows)

# Merge user_df and roster_df on 'User ID'
final_df = pd.merge(user_df, roster_df, on='User ID', how='left')

# Display the updated DataFrame
print(final_df.columns)

# Save to CSV
final_df.to_csv('ihavebigplans.csv', index=False)
