import os
import google.generativeai as genai
from dotenv import load_dotenv
import yaml
from util import save_game_state, load_game_state
from character import Character
from location import Location

SAFETY_SETTINGS = [
    {
        'category': 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'BLOCK_NONE'
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'BLOCK_NONE'
    }
]

def load_data_from_yaml(filename):
    """Loads data from a YAML file."""
    try:
        with open(filename, 'r') as f:
            return yaml.safe_load(f)  # Use safe_load for security
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML format in '{filename}': {e}")
        return None

def generate_world_setting(aibot, world_description):
    prompt = f"""Generate a more detailed description of a world described as: {world_description}. Include details about the environment, atmosphere, and any notable features."""
    try:
        response = aibot.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                max_output_tokens=200,
                temperature=1.0
            )
        )
        return response.text
    except Exception as e:
        print(f"Error generating world description: {e}")
        return "A mysterious world."

def main():
    load_dotenv()
    genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
    gemini_model = genai.GenerativeModel(model_name=os.environ.get('MODEL_NAME'), safety_settings=SAFETY_SETTINGS)

    # Load game data from YAML
    game_data = load_data_from_yaml("game_data.yaml")
    if game_data is None:
        exit()

    # Load world settings
    world_description = game_data.get("world_description", "A default world.")
    detailed_world_description = generate_world_setting(gemini_model, world_description)
    print("\nWorld Setting:")
    print(detailed_world_description)
    print("-" * 20)

    # Create locations from data
    locations = {}
    for loc_name, loc_data in game_data.get("locations", {}).items():
        exits = {}
        for direction, exit_name in loc_data.get("exits", {}).items():
            exits[direction] = exit_name  # Store names for now, link later
        locations[loc_name] = Location(loc_name, loc_data.get("description", "A default location."), exits)

    # Link locations (after all are created)
    for loc_name, loc in locations.items():
        for direction, exit_name in loc.exits.items():
            if exit_name in locations:
                loc.exits[direction] = locations[exit_name]
            else:
                print(f"Warning: Exit '{exit_name}' from {loc_name} not found.")
                loc.exits[direction] = None # Set to none so the game won't crash

    characters = {}
    for char_name, char_data in game_data.get("characters", {}).items():
        start_location_name = char_data.get("location")
        start_location = locations.get(start_location_name)
        if start_location is None:
            print(f"Error: Starting location '{start_location_name}' for {char_name} not found.")
            exit()
        characters[char_name] = Character(gemini_model, char_name, char_data) # Pass the data dictionary
        characters[char_name].location = start_location

    # Get Player
    player_name = input("Enter your character's name: ")

    if player_name in characters:
        player = characters[player_name]
    else:
        print("Player not found in data file")
        exit()

    # Get Knight
    knight_name = "Knight" # Set the knight name here if you don't want to ask every time
    knight = characters.get(knight_name)

    if knight is None:
        print("Knight not found in the game data.")
        exit()

    # Game loop (mostly same)
    print(f"\nYou find yourself in the {player.location.name}. {player.location.description}")

    while True:
        action = input("What do you do? (move north, talk to knight, quit): ").lower()

        if action == "move north":
            print(player.move("north"))
            print(f"You are now in the {player.location.name}. {player.location.description}")
            print(knight.move("north")) # Knight follows
        elif action == "talk to knight":
            dialogue = knight.generate_dialogue(f"The player is here.")
            print(f"Sir Reginald says: \"{dialogue}\"")
            player.memory.append({"type": "conversation", "with": "knight", "content": dialogue})
            knight.memory.append({"type": "conversation", "with": "player", "content": dialogue})
        elif action == "save":
            save_game_state(player, characters)
        elif action == "load":
            loaded_player = load_game_state(locations, characters)
            if loaded_player:
                player = loaded_player
                print("Game loaded.")
                print(f"You are in the {player.location.name}. {player.location.description}")
            else:
                print("Failed to load game.")
        elif action == "quit":
            break
        else:
            print("Invalid action.")

    print("Game Over")

if __name__ == '__main__':
    main()
