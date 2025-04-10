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
    get_new_story_location, get_question, is_invalid_user_response, ai_story_generator, generate_hint
)

from player import Player


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

# Set your OpenAI API key
openai.api_key = "***REMOVED***"  # Replace with your actual key

# FILE_LOCATIONS = {
# "Question1_0    " : r"C:\\Users\punco\OneDrive\Desktop\plot json\story.json",
# "Question1_2_0" : r"C:\\Users\punco\OneDrive\Desktop\plot json\1_2_0.json",
# "Question1_4_0" : r"C:\\Users\punco\OneDrive\Desktop\plot json\1_4_0.json",
# "Question1_2_2_0" : r"C:\\Users\punco\OneDrive\Desktop\plot json\1_2_2_0.json",
# "Question1_2_2_2_0" : r"C:\\Users\punco\OneDrive\Desktop\plot json\1_2_2_2_0.json",
# "Question1_2_2_2_1_0" : r"C:\\Users\punco\OneDrive\Desktop\plot json\1_2_2_2_1_0.json"
# }

# Dynamically create a file_locations dict to store questions and their file locations
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



# Pictures
# Question1pic = 'C:\\Users\punco\OneDrive\Desktop\programming\question1pic.png'
# Question1_2_0pic = 'C:\\Users\punco\OneDrive\Desktop\programming\question1_2_0pic.png'
# Question1_4_0pic = 'C:\\Users\punco\OneDrive\Desktop\programming\question1_4_0pic.jpg'

def game():

    player = Player()
    player.health = 100
    put_markdown("**SELECT DIFFICULTY** \n Type **1** for EASY, **2** for MEDIUM, **3** for HARD")
    select = int(input())
    while select > 3 or select < 1:
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
    CURRENT_STORY_POSITION = Question1
    LAST_INPUT = ''

    put_markdown("# Dangerous Facility")
    put_image(open(Question1pic, 'rb').read())
    put_text(story_points_dictionary(Question1)["Question"])
    ALIVE = True
    
    while ALIVE:
        item_found = story_points_dictionary(CURRENT_STORY_POSITION)["item"]
        if item_found in player.inventory:
            player.inventory[item_found] += 1
            put_markdown(f"You just picked up an item: *{item_found}*")
        
        put_text(f"Your Health: {player.health}")
        put_text(f"Your Inventory: {player.inventory}")
        user_input = input()
        put_markdown("**Your Response:** " + str(user_input))
        response = ask_chatGPT(create_prompt(LAST_INPUT, CURRENT_STORY_POSITION), user_input)
        
        if is_invalid_user_response(response):
            put_markdown("*Invalid response* \n")
            put_markdown(generate_hint(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION)))

        elif is_valid_response(response, CURRENT_STORY_POSITION) :
            # LOSING SITUATION --> Either the damage is avoided/reduced with an item or the player loses the most health that they can 
            if story_points_dictionary(QuestionFlow)[get_question(CURRENT_STORY_POSITION)][response][:5] == "end--": # TO CHANGE
                has_item = False
                needed_item = ""
                losing_health = health_to_lose
                if "(key=" in story_points_dictionary(CURRENT_STORY_POSITION)[response]: # TO CHANGE -> 'if item:' can be done to check if an item is needed. if it's left blank '', then no item is needed for that point in the story
                    for k in player.inventory.keys():
                        if f"key={k}" in story_points_dictionary(CURRENT_STORY_POSITION)[response]: # TO CHANGE 
                            needed_item = k
                            if player.inventory[k] > 0:
                                has_item = True
                                put_markdown(f"*{k} used*")
                                player.inventory[k] -= 1
                    if has_item == False:
                        put_markdown(f"You could've avoided that situation with the item *{needed_item}*!")
                        player.lose_health(health_to_lose)
                        needed_item = ''
                    else: 
                        losing_health = 0

                if player.health <= 0: 
                    ALIVE = False
                    put_text(ai_story_generator(user_input, "This seems to no longer matter, transition the story such that the user meets their end now.", story_points_dictionary(QuestionFlow)[get_question(CURRENT_STORY_POSITION)][response], ''))
                    put_markdown("**-- Game Over --**")
                else: 
                    put_text(ai_story_generator(user_input, "The user inputted a losing option here, but instead of transitioning it to end, transition it bluntly with them taking damage but still remaining alive, and end the sentence by saying that THEY DECIDE NOT TO TAKE the course of action they just took to go down this path in the story. No questions or anything more, just end it like that.", story_points_dictionary(QuestionFlow)[get_question(CURRENT_STORY_POSITION)][response], needed_item))
                    put_markdown(f"{losing_health} Health Lost!")
                    for k, v in story_points_dictionary(CURRENT_STORY_POSITION).items(): # TO CHANGE --> This part's functionality will be replaced with a losing point of a story being forced to another file
                        if "(continues)" in v:
                            response = k
                            break
                    
                    CURRENT_STORY_POSITION = get_new_story_location(response, CURRENT_STORY_POSITION)
                    put_text(ai_story_generator('', create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], needed_item))
                    LAST_INPUT = user_input
                    PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION
            # SITUATION WHERE NOT LOSING BUT AN ITEM IS NEEDED
            elif "(key=" in story_points_dictionary(CURRENT_STORY_POSITION)[response]: # TO CHANGE -> 'if item:' can be done to check if an item is needed. if it's left blank '', then no item is needed for that point in the story
                has_item = False
                needed_item = ''
                for k in player.inventory.keys():
                    if f"(key={k})" in story_points_dictionary(CURRENT_STORY_POSITION)[response]: # TO CHANGE
                        needed_item = k
                        if player.inventory[k] > 0:
                            has_item = True
                            put_markdown(f"*{k} used*")
                            player.inventory[k] -= 1
                if has_item == False:
                    put_markdown(f"*You're going to a {needed_item} to do that!*")
                    put_markdown(generate_hint(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION)), needed_item)
                else:
                    CURRENT_STORY_POSITION = get_new_story_location(response, CURRENT_STORY_POSITION)
                    put_text(ai_story_generator(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], needed_item))
                    LAST_INPUT = user_input
                    PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION
            # NOT LOSING AND NO ITEM NEEDED
            else:
                CURRENT_STORY_POSITION = get_new_story_location(response, CURRENT_STORY_POSITION)
                put_text(ai_story_generator(user_input, create_prompt(LAST_INPUT, PREVIOUS_STORY_POSITION), story_points_dictionary(CURRENT_STORY_POSITION)["Question"], ''))
                LAST_INPUT = user_input
                PREVIOUS_STORY_POSITION = CURRENT_STORY_POSITION

if __name__ == "__main__":
    start_server(game, port=0, debug=True)