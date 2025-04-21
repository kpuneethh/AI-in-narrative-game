import json
from openai import OpenAI

client = OpenAI(api_key="***REMOVED***")
import sys
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

DEFAULT_DEBUG_VALUE = True
# Set your OpenAI API key
  # Replace with your actual key

# TODO How the items interact with the story --> (key=item) in text
# TODO game sidebar
# TODO multiple options that can lead to the same story point - losing option leads to another file that forces the user to the next story path while losing health
# TODO add api key to environment and learn how to load it from environment

def story_points_dictionary(json_path: str, debug: bool = DEFAULT_DEBUG_VALUE):
    """returns dictionary of story points"""
    # if debug:
    #     logger.info('Inside story_points_dictionary function')
    #     logger.info(f'json path: {json_path}')
    with open(json_path, 'r') as file:
            # Load the JSON data into a Python dictionary
            data = json.load(file)
    return data

def ask_chatGPT(ai_prompt, user_response, debug: bool = DEFAULT_DEBUG_VALUE):
    """Returns a single word that is used as an option in the current dictionary of story options"""
    if debug:
        logger.info('Inside ask_chatGPT function')
        logger.info(f'assistant content: {ai_prompt}')
    
    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an interactive storytelling assistant helping the user navigate a story. "
                    "The user responds to open-ended prompts, and you have access to a set of hidden options for each decision point in the story. "
                    "Your job is to analyze the user's response, compare it with the hidden options, and select the most similar option based on meaning and intent. "
                    "Once you've chosen the closest option, RESPOND WITH ONLY A SINGLE CHARACTER, which should the NUMBER of that option in the list of choices. "
                    "Respond with the character 'e' if the user's answer is jibberish. Even if the user answer is a little different from the choices, dont return 'e'"
                )
            },
            {"role": "assistant", "content": ai_prompt},
            {"role": "user", "content": user_response}
        ],
        temperature=1.0,
        max_tokens=2
    )

    return response.choices[0].message.content.strip()

def create_prompt(last_input, options_dictionary, debug: bool = DEFAULT_DEBUG_VALUE):
    """Creates prompt for AI using the last input and the current options dictionary"""
    if debug:
        logger.info('Inside create_prompt function')
        logger.info(f'last input: {last_input}')
        logger.info(f'options dictionary: {options_dictionary}')
    if options_dictionary == '':
        return f"Last Input: {last_input}"
    current_question = story_points_dictionary(options_dictionary)["location"]
    # options = list(story_points_dictionary(options_dictionary)["options"].items())
    # formatted_options = "\n".join(f"{key}: {option}" for key, option in options)

    option_lines = [f"{key} : \"{value['text']}\"" for key, value in story_points_dictionary(options_dictionary)["options"].items()]
    formatted_options = "\n".join(option_lines)

    prompt = (
        f"Last Input: {last_input} \n"
        f"Current Question: {current_question} \n"
        f"{formatted_options}"
    )
    return prompt

def is_valid_response(ai_response: str, options_dictionary, num_of_valid_responses: int = None, debug: bool = DEFAULT_DEBUG_VALUE) -> bool:
    """Used to test whether the AI's response is a valid key within the current story dictionary"""
    if debug:
        if ai_response not in story_points_dictionary(options_dictionary)["options"]:
            logging.warning(f"the ai response ({ai_response}) was not valid")
    return ai_response in story_points_dictionary(options_dictionary)["options"]

# def get_new_story_location(ai_response: str, current_location: str, debug: bool = DEFAULT_DEBUG_VALUE) -> str:
#     """Continuation of valid_response. Chooses the next story dictionary to use. Current location is the name of the file. New location coordinates are created 
#     based off of ai_response and current_location"""
#     if debug:
#         logger.info('Inside get_new_story_location function')
#         logger.info(f'ai response: {ai_response}')
#         # logger.info(f'current location: {current_location}')
#     new_location_question = story_points_dictionary(QuestionFlow)[get_question(current_location)][ai_response]
#     if new_location_question in FILE_LOCATIONS.keys():
#         return FILE_LOCATIONS[new_location_question]
#     return ''

def get_question(story_location): #, json_storage_directory
    """"""
    return story_points_dictionary(story_location)["location"]

def is_invalid_user_response(ai_response: str):
    return ai_response == 'e'

def ai_story_generator(user_response: str, ai_prompt: str, dictionary_question: str, item_to_use: str, debug: bool = DEFAULT_DEBUG_VALUE):
    """Uses the short question found in the given question dictionary to generate a longer, well-written passage and question for the story"""
    if debug:
        logger.info('Inside AI story generator function')
        logger.info(f'user content: {dictionary_question}')
    
    content = (
        f'The previous part of the story: {ai_prompt}\n'
        f'The current user response that you must transition to the story: {user_response}\n'
        f'The simplified story that this leads to: {dictionary_question}\n'
        f'Please expand the story taking into account the user input'
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are an interactive storytelling assistant helping the user navigate a story. "
                "The user responds to open-ended prompts."
            )
        },
        {
            "role": "assistant",
            "content": (
                "You must analyze the ai_prompt given to you that shows the previous parts of the story. "
                "Following that, you must read the short question that comes to you, which is a simplified version. Your job is to use that short question and rewrite it into a longer, well-written question/passage for the story, and return it, all while transitioning the user's input to that story so different user inputs can fit in while seeming natural. "
                "Make sure you start out the paragraph by naturally transitioning the users response to the next part of the story instead of something abrupt. It has to be clear to the user that they are being replied to."
                "Make sure not to list or generate any options of what the user can possibly do. "
                "Your response should be UNDER 100 words while conveying the whole idea."
            )
        },
        {"role": "user", "content": content}
    ]

    if item_to_use:
        messages.append({
            "role": "user",
            "content": f"This item helped the user get through this situation, make sure to weave it with the story: {item_to_use}"
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        temperature=1.0,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()


def generate_hint(user_response: str, story_dictionary: dict, item_to_use: str, debug: bool = DEFAULT_DEBUG_VALUE):
    """Returns a hint for invalid responses"""
    if debug:
        logger.info('Inside generate_hints function')
        logger.info(f'assistant content: {story_dictionary}')

    messages = [
        {
            "role": "system",
            "content": (
                "You are an interactive storytelling assistant helping the user navigate a story. The user has just inputted an invalid response that is vastly different from all of the available options and needs hints to come up with a valid response. "
                "You have access to the current question and its corresponding HIDDEN options. "
                "NEVER DIRECTLY REVEAL ANY OF THE HIDDEN OPTIONS. "
                "Since the user inputted an invalid response, your job is return a hint that steers the user in the correct path. "
                "Keep it fluid and dynamic. Talk like the user doesn't know there are any hidden options or choices available. "
                "Respond like the user is really in the situation, and don't call it a story. "
                "Use 2nd person POV only. "
                "Don't call it a 'response'."
            )
        },
        {"role": "assistant", "content": str(story_dictionary)},
        {"role": "user", "content": user_response}
    ]

    if item_to_use:
        messages.append({
            "role": "user",
            "content": f"The user needs this item to get through this situation, let them know that they need it (ignore if blank): {item_to_use}"
        })

    response = client.chat.completions.create(
        model="gpt-4o-mini-2024-07-18",
        messages=messages,
        temperature=1.0,
        max_tokens=100
    )

    return response.choices[0].message.content.strip()
