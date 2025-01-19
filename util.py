import yaml

def load_data_from_yaml(filename):
    '''Loads data from a YAML file.'''
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format in '{filename}': {e}")
        return None

def save_game_state(player, characters, filename="save_game.yaml"):
    '''Saves the current game state to a YAML file.'''

    game_state = {
        'player': {
            'name': player.name,
            'location': player.location,
            'memory': player.memory
        },
        'characters': {}
    }

    # Save data for all characters (important for persistent NPC states)
    for char_name, char in characters.items():
        game_state['characters'][char_name] = {
            'name': char.name,
            'location': char.location,
            'memory': char.memory
        }

    try:
        with open(filename, 'w') as f:
            yaml.dump(game_state, f, default_flow_style=False) # default_flow_style=False for better readability
        print(f'Game saved to {filename}')
    except Exception as e:
        print(f'Error saving game: {e}')

def load_game_state(locations, characters, filename='save_game.yaml'):
    '''Loads the game state from a YAML file.'''
    try:
        with open(filename, 'r') as f:
            game_state = yaml.safe_load(f)

        player_data = game_state.get('player')
        if player_data:
            player_name = player_data.get('name')
            if player_name in characters:
                player = characters[player_name]
                player.location = locations.get(player_data.get('location'))
                player.memory = player_data.get('memory', [])
            else:
                print('Player not found in game data')
                return None
        else:
            print('No player data in save file.')
            return None

        for char_name, char_data in game_state.get('characters', {}).items():
            if char_name in characters:
                char = characters[char_name]
                char.location = locations.get(char_data.get('location'))
                char.memory = char_data.get('memory', [])
            else:
                print(f'Character {char_name} from save file not found in game data.')

        return player  # Return the loaded player object
    except FileNotFoundError:
        print(f"Save file '{filename}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f'Error loading game state from YAML: {e}')
        return None
    except Exception as e:
        print(f'Error loading game: {e}')
        return None
