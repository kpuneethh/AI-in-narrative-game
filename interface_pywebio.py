import json
import openai
import sys
import logging
import os

# PyWebIO
from pywebio.input import input, select
from pywebio.output import put_text, put_markdown, put_image
from pywebio.session import set_env
from pywebio import start_server

DEFAULT_DEBUG_VALUE = True

from functions import(
    story_points_dictionary, ask_chatGPT, create_prompt, is_valid_response,
    get_question, is_invalid_user_response, ai_story_generator, generate_hint, recite_inventory
)

from player import Player

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

# Dynamically create a FILE_LOCATIONS dict to store questions and their file locations on any pc
FILE_LOCATIONS = {}
target_folder = "AI-in-narrative-game"
json_subfolder = "plot json"
start_dir = os.path.expanduser("~")

for root, dirs, files in os.walk(start_dir):
    if os.path.basename(root) == target_folder:
        potential_json_folder = os.path.join(root, json_subfolder)
        if os.path.isdir(potential_json_folder):
            for filename in os.listdir(potential_json_folder):
                if filename.endswith(".json"):
                    full_path = os.path.join(potential_json_folder, filename)
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            location_value = data["location"]  # updated key
                            #print(f"{full_path}: {location_value}")
                            FILE_LOCATIONS[location_value] = f"{full_path}"
                    except Exception as e:
                        print(f"Error reading {full_path}: {e}")


def game():

    player = Player()
    player.health = 100
    put_markdown("**SELECT DIFFICULTY** \n Type **1** for EASY, **2** for MEDIUM, **3** for HARD")
    select = int(input())
    while select < 1 or select > 3:
        put_markdown("Not a valid difficuly! Type **1** for EASY, *2* for MEDIUM, **3** for HARD")
        select = int(input())
    health_to_lose = 0
    if select == 1:
        put_text("Selected Difficulty: EASY")
        health_to_lose = 40
    elif select == 2:
        put_text("Selected Difficulty: MEDIUM")
        health_to_lose = 70
    else:
        put_text("Selected Difficulty: HARD")
        health_to_lose = 100


    PREVIOUS_STORY_POSITION = ''
    CURRENT_STORY_POSITION = FILE_LOCATIONS["Question1_0"]
    LAST_INPUT = ''

    put_markdown("# Dangerous Facility")
    # put_image(open(Question1pic, 'rb').read())
    put_text(story_points_dictionary(CURRENT_STORY_POSITION)["Question"])

    ALIVE = True

    while ALIVE:
        item_found = story_points_dictionary(CURRENT_STORY_POSITION)["item_pickup"]
        if item_found in player.inventory:
            player.inventory[item_found] += 1
            put_markdown(f"You just picked up an item: *{item_found}*")

        put_text(f"Your Health: {player.health}")
        inventory_str = ""
        for item in player.inventory.keys():
            if player.inventory[item] >= 1:
                inventory_str += f"Amount of {item}: {player.inventory[item]} \n"
        put_text(f"Your Inventory: {recite_inventory(inventory_str)}")
        user_input = input()
        put_markdown("**Your Response:** " + str(user_input))
        response = ask_chatGPT(create_prompt(LAST_INPUT, CURRENT_STORY_POSITION), user_input)            
        if is_invalid_user_response(response):
            put_markdown("*Invalid response* \n")
            put_markdown(generate_hint(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION),""))

        elif is_valid_response(response, CURRENT_STORY_POSITION) :
            # LOSING SITUATION --> Either the damage is avoided/reduced with an item or the player loses the most health that they can 

            if "stone" in user_input:
                player.inventory["stone"] -= 1

            if story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["type"] == "losing": # TO CHANGE
                has_item = False
                needed_item = ""
                losing_health = health_to_lose

                needed_item = story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["item_needed"]
                if needed_item: # TO CHANGE -> 'if item:' can be done to check if an item is needed. if it's left blank '', then no item is needed for that point in the story
                    if player.inventory[needed_item] > 0:
                        has_item = True
                        put_markdown(f"*{needed_item} used*")
                        player.inventory[needed_item] -= 1
                        losing_health = 0
                    if has_item == False:
                        put_markdown(f"You could've avoided that with the item *{needed_item}*!")
                        player.lose_health(health_to_lose)
                else:
                    player.lose_health(health_to_lose)

                if player.health <= 0: 
                    ALIVE = False
                    put_text(ai_story_generator(user_input, "This seems to no longer matter, transition the story such that the user meets their end now, and don't ask what they'll do next. ", 
                                                story_points_dictionary(FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["next_location"]])["Question"], ""))
                    put_markdown("**-- Game Over --**")
                    break
                else: 
                    put_text(ai_story_generator(user_input, "The user inputted a losing option here, but instead of transitioning it to end," \
                                                " transition it bluntly with them taking damage but still remaining alive, and end the sentence by saying that THEY DECIDE NOT TO TAKE" \
                                                " the course of action they just took to go down this path in the story. No questions or anything more, just end it like that.", 
                                                story_points_dictionary(FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["next_location"]])["Question"], needed_item))
                    put_markdown(f"{losing_health} Health Lost!")

                    CURRENT_STORY_POSITION = FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["next_location"]]
                    CURRENT_STORY_POSITION = FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"]["1"]["next_location"]]

                    put_text(ai_story_generator('', create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], needed_item))
                    LAST_INPUT = user_input
                    PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION

            # SITUATION WHERE NOT LOSING BUT AN ITEM IS NEEDED

            if "stone" in user_input:
                player.inventory["stone"] -= 1

            elif story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["item_needed"]: # TO CHANGE -> 'if item:' can be done to check if an item is needed. if it's left blank '', then no item is needed for that point in the story
                has_item = False
                needed_item = story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["item_needed"]
                if player.inventory[needed_item] > 0:
                        has_item = True
                        put_markdown(f"*{needed_item} used*")
                        player.inventory[needed_item] -= 1
                if has_item == False:
                    put_markdown(f"*You're going to a {needed_item} to do that!*")
                    put_markdown(generate_hint(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), needed_item))
                else:
                    CURRENT_STORY_POSITION = FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["next_location"]]
                    put_text(ai_story_generator(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], needed_item))
                    LAST_INPUT = user_input
                    PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION

            # NOT LOSING AND NO ITEM NEEDED
            else:

                if "stone" in user_input:
                    player.inventory["stone"] -= 1
                
                CURRENT_STORY_POSITION = FILE_LOCATIONS[story_points_dictionary(CURRENT_STORY_POSITION)["options"][response]["next_location"]]
                if CURRENT_STORY_POSITION == FILE_LOCATIONS["WON"]:
                    put_text(ai_story_generator(user_input, "The user has reached the end of the game and won. Transition it here as such ", 
                                                story_points_dictionary(FILE_LOCATIONS["WON"]["Question"], "")))
                    put_markdown("**-- Game Won --**")
                    break
                put_text(ai_story_generator(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], ""))
                LAST_INPUT = user_input
                PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION
                

if __name__ == "__main__":
    start_server(game, port=0, debug=True)