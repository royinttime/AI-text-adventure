import os
# TODO: switch to Google's new library(from google import genai)
import google.generativeai as genai
from dotenv import load_dotenv
from util import load_data_from_yaml, save_game_state, load_game_state
from character import Character
from location import Location
from setting import GEIMINI_SAFETY_SETTINGS

GAME_SETTING_FILENAME = 'game_setting.yaml'

def handle_player_action(player, characters, locations, action):
    '''Handles player actions and their effects on the game world.'''
    action_parts = action.split(" ", 1)
    verb = action_parts[0].lower()
    if len(action_parts) > 1:
        object_name = action_parts[1].lower()
    else:
        object_name = None

    if verb == 'move':
        if object_name in locations:
            print(player.move(object_name))
            print(f'You are now in the {player.location}. {locations[player.location].description}')
            # Move following characters
            # TODO: Build party system
            for char_name, char in characters.items():
                if char != player and char.location == player.location:
                    char.location = player.location
        else:
            print(f'{destination} does not exist.')
    elif verb == 'interact':
        if object_name:
            handle_character_interaction(player, characters, object_name)
        else:
            print('Who do you want to interact with?')
    elif verb == 'look':
        print(locations[player.location].description)
        print('\nThe characters in this location:')
        for ch_name, ch_data in characters.items():
            if ch_data.location == player.location:
                print(ch_name)

    elif verb == 'save':
        save_game_state(player, characters)
    elif verb == 'load':
        loaded_player = load_game_state(locations, characters)
        if loaded_player:
            player = loaded_player
            print('Game loaded.')
            print(f'You are in the {player.location}. {locations[player.location].description}')
        else:
            print('Failed to load game.')
    else:
        print('Invalid action.')

def handle_character_interaction(player, characters, target_name):
    '''Handles detailed interactions with a specific character.'''

    char_name = target_name.title()
    if player.name == char_name:
        print('Can not interact with yourself')
        return

    target_char = characters.get(char_name)
    if not target_char or target_char.location != player.location:
        print(f'{char_name} is not here.')
        return

    while True:
        interaction = input(f"What do you do with {char_name}? (Type 'back' to return): ")
        if interaction.lower() == 'back':
            break

        try:
            target_char.interact_with(player, interaction)
        except Exception as e:
            print(f'Error generating response: {e}')
    target_char.end_ineraction()

def main():
    load_dotenv()
    # TODO: Create AI agent class and have a config decide what part use which agent
    genai.configure(api_key=os.environ.get('GOOGLE_API_KEY'))
    gemini_model = genai.GenerativeModel(model_name=os.environ.get('MODEL_NAME'), safety_settings=GEIMINI_SAFETY_SETTINGS)

    # Laod game setting from a YAML file
    # TODO: extend this flow. might leave the setting to YAML file.
    #       info to pure text file for RAG pipeline
    game_data = load_data_from_yaml(GAME_SETTING_FILENAME)
    if game_data is None:
        exit()

    # Create objects to store the info from game setting file
    locations = {}
    for loc_name, loc_data in game_data.get('locations', {}).items():
        locations[loc_name] = Location(loc_name, loc_data)
    characters = {}
    for char_name, char_data in game_data.get('characters', {}).items():
        characters[char_name] = Character(char_name, char_data)

    narrator = Narrator(gemini_model)

    # Generate stating world description
    world_description = game_data.get('world_description', 'A default world.')
    detailed_world_description = narrator.generate_world_setting(world_description)
    print('\nWorld Setting:')
    print(detailed_world_description)
    print('-' * 20)

    player_name = input("Enter your character's name: ")
    if player_name in characters:
        player = characters[player_name]
    else:
        print('Player not found in the game setting file')
        exit()

    print(f'\nYou find yourself in the {player.location}. {locations[player.location].description}')

    while True:
        user_input = input('What do you do? (e.g., interact, move, look, save, load, quit): ')

        # TODO: use AI to guess which kind of action user want to do. so we don't need to input keyword.
        if user_input.lower() == 'quit':
            break

        handle_player_action(player, characters, locations, user_input)

    print('\nThanks for playing')

if __name__ == '__main__':
    main()
