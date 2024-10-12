# import math
# from typing import Dict, List
# import sys
# import autogen
# import os
# from dotenv import load_dotenv

# load_dotenv()


# def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
#     # Read the restaurant data file and extract reviews for the specified restaurant.
#     restaurant_reviews = {}
#     with open('restaurant-data.txt', 'r') as file:
#         for line in file:
#             name, review = line.split('. ', 1)
#             name = name.strip()
#             review = review.strip()
#             if name not in restaurant_reviews:
#                 restaurant_reviews[name] = []
#             restaurant_reviews[name].append(review)

#     # Return reviews for the specified restaurant
#     return {restaurant_name: restaurant_reviews.get(restaurant_name, [])}


# def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
#     N = len(food_scores)
#     score_sum = 0.0

#     for i in range(N):
#         score_sum += math.sqrt(food_scores[i]**2 * customer_service_scores[i])

#     overall_score = (score_sum / (N * math.sqrt(125))) * 10
#     return {restaurant_name: round(overall_score, 3)}


# def main(user_query: str):
#     entrypoint_agent_system_message = """
#         You are an entrypoint agent responsible for overseeing and coordinating conversations between other agents.
#         Your task is to manage queries related to restaurant reviews. First, analyze the user's query and extract the
#         relevant restaurant name. Then, interact with the data fetch agent to retrieve the appropriate reviews for that
#         restaurant. Once you have the reviews, pass them on for further processing and summarization.
#     """

#     # LLM config for the entrypoint agent
# llm_config = {"config_list": [
#     {"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

#     # The main entrypoint/supervisor agent
# entrypoint_agent = autogen.ConversableAgent(
#     "entrypoint_agent", system_message=entrypoint_agent_system_message, llm_config=llm_config)

#     # Messages for the data fetch agent, review analysis agent, and scoring agent
#     fetch_message = """
#         Expert in finding data and extracting features. Good at determining relevant data to fetch. using function fetch_restaurant_data.
#         Notice, the name of the restaurant might be a little different from the real one. For example, sometimes it use ' ' rather than '-' to concate the words, etc. So be little tolerant for the input name.
#         For example, "Chick-fil-A" could be "Chick fil A" or "Chick_fil_A".
#         In this case, you should try every single possible name to fetch the reviews.
#     """

#     review_message = """
#         You are a review analysis agent responsible for analyzing customer reviews of restaurants.
#         Each review contains descriptions of both the food and the customer service, and your task
#         is to extract two separate scores: one for the food and one for the customer service.

#         You will assign a score to each aspect based on the following adjectives present in the review:

#         1. **Score 1/5** has one of these adjectives: awful, horrible, disgusting.
#         2. **Score 2/5** has one of these adjectives: bad, unpleasant, offensive.
#         3. **Score 3/5** has one of these adjectives: average, uninspiring, forgettable.
#         4. **Score 4/5** has one of these adjectives: good, enjoyable, satisfying.
#         5. **Score 5/5** has one of these adjectives: awesome, incredible, amazing.

#         Each review will contain exactly two adjectives: one describing the food and one describing the
#         customer service. You will assign the food score based on the adjective describing food and the
#         customer service score based on the adjective describing service.

#         Your output should be structured as two lists of integers:
#         - One list contains the **food scores** for all reviews.
#         - One list contains the **customer service scores** for all reviews.
#     """

#     score_message = """
#        You are a scoring agent responsible for calculating a restaurant's overall score based on two sets of
#        scores: the food scores and the customer service scores.

#         You will receive:
#         1. The name of the restaurant as a string.
#         2. A list of integers representing the **food scores**.
#         3. A list of integers representing the **customer service scores**.

#         Your task is to:
#         1. Calculate the overall score for the restaurant by applying a specific formula.
#         2. The formula is as follows:
#         - For each review, multiply the food score by the customer service score, then take the square root of the result.
#         - Sum up all the results.
#         - Divide the total sum by \( N \times \sqrt{125} \), where \( N \) is the number of reviews.
#         - Multiply the result by 10 to get the overall score.
#         3. Return the overall score rounded to three decimal places, along with the restaurant's name.
#     """

#     # Agents for data fetching, review analysis, and scoring
#     datafetch_agent = autogen.ConversableAgent(
#         name="data_fetch_agent",
#         llm_config=llm_config,
#         system_message=fetch_message
#     )

#     review_agent = autogen.ConversableAgent(
#         name="review_analysis_agent",
#         llm_config=llm_config,
#         system_message=review_message
#     )

#     scoring_agent = autogen.ConversableAgent(
#         name="scoring_agent",
#         llm_config=llm_config,
#         system_message=score_message
#     )

#     # Register the functions for each agent
#     entrypoint_agent.register_for_llm(
#         name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
#     entrypoint_agent.register_for_execution(
#         name="fetch_restaurant_data")(fetch_restaurant_data)

#     datafetch_agent.register_for_llm(
#         name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
#     datafetch_agent.register_for_execution(
#         name="fetch_restaurant_data")(fetch_restaurant_data)

#     entrypoint_agent.register_for_llm(
#         name="calculate_overall_score", description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
#     entrypoint_agent.register_for_execution(
#         name="calculate_overall_score")(calculate_overall_score)

#     scoring_agent.register_for_llm(name="calculate_overall_score",
#                                    description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
#     scoring_agent.register_for_execution(
#         name="calculate_overall_score")(calculate_overall_score)

#     # Start the conversation
#     task1 = f"""
#         Take the input, {user_query}, and return it in the format "Dict[str, List[str]]"
#         where str is the restaurant's name and List[str] contains every avalible review of
#         the restaurant. The true name of the restaurant might be a little different from the
#         input name. For example, sometimes it use ' ' rather than '-' to concate the words, etc.
#         So be little tolerant for the input name.
#     """

#     task2 = f"""
#         Convert the restaurant reviews to scores.

#         Extract the food_score and customer_service_score based on every reviews(List[str]) of the restaurant. Do it sentence by sentence, the length of the list food_score and customer_service_score are equal to the number of comments.
#         Make sure food_score and customer_service_score have same length.
#     """

#     task2 = """
#         Please analyze the reviews fetched in the previous task. Extract the `food_score` and
#         `customer_service_score` for each review based on your scoring criteria, and return two lists:

#         1. A list of `food_scores`.
#         2. A list of `customer_service_scores`.

#         Make sure to process all the reviews and return the scores in the following format:

#         `[(food_score1, customer_service_score1), (food_score2, customer_service_score2), ...]`
#     """

#     task3 = r"""
#     Calculate the overall score based on the food_score and customer_service_score. Using 'calculate_overall_score' function and "food_scores", "customer_service_scores" as args.
#     For example, if you recieve a json package:
#     {"restaurant_name": "Chick-fil-A", "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]}
#     You can use
#     "restaurant_name": "Chick-fil-A"
#     "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] and
#     "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
#     as args
#     Return in r'\d*\.\d{3}' format.
#     """

#     prefix1 = entrypoint_agent.initiate_chat(
#         datafetch_agent,
#         message=task1,
#         max_turns=4,
#         summary_method="last_msg",
#     )

#     prefix2 = entrypoint_agent.initiate_chat(
#         review_agent,
#         message=f"{prefix1}\n\nNew task: {task2}",
#         max_turns=2,
#         summary_method="last_msg",
#     )

#     entrypoint_agent.initiate_chat(
#         scoring_agent,
#         message=f"{prefix2}\n\nNew task: {task3}",
#         max_turns=3,  # 1
#         summary_method="last_msg",
#     )


# # DO NOT modify this code below.
# if __name__ == "__main__":
#     assert len(
#         sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
#     main(sys.argv[1])


from typing import Dict, List
from autogen import ConversableAgent
import autogen
import sys
import math
import os
from dotenv import load_dotenv
import pdb

load_dotenv()


# def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
#     # This function takes in a restaurant name and returns the reviews for that restaurant.
#     # The output should be a dictionary with the key being the restaurant name and the value being a list of reviews for that restaurant.
#     # The "data fetch agent" should have access to this function signature, and it should be able to suggest this as a function call.
#     # Example:
#     # > fetch_restaurant_data("Applebee's")
#     # {"Applebee's": ["The food at Applebee's was average, with nothing particularly standing out.", ...]}
#     file_path = 'restaurant-data.txt'
#     try:
#         with open(file_path, 'r') as file:
#             content = file.read()

#         # pdb.set_trace()
#         reviews = content.split('\n')

#         comments = []

#         for review in reviews:
#             if review.lower().startswith(restaurant_name.lower() + '.'):
#                 comments.append(review[len(restaurant_name) + 1:].strip())

#         return [restaurant_name, comments]

#     except FileNotFoundError:
#         return f"Error: The file {file_path} was not found."
#     except Exception as e:
#         return f"An error occurred: {str(e)}"

# Combination
def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # Read the restaurant data file and extract reviews for the specified restaurant.
    restaurant_reviews = {}
    with open('restaurant-data.txt', 'r') as file:
        for line in file:
            name, review = line.split('. ', 1)
            name = name.strip()
            review = review.strip()
            if name not in restaurant_reviews:
                restaurant_reviews[name] = []
            restaurant_reviews[name].append(review)

    # Return reviews for the specified restaurant
    return {restaurant_name: restaurant_reviews.get(restaurant_name, [])}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # This function takes in a restaurant name, a list of food scores from 1-5, and a list of customer service scores from 1-5
    # The output should be a score between 0 and 10, which is computed as the following:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # The above formula is a geometric mean of the scores, which penalizes food quality more than customer service.
    # Example:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.04}
    # NOTE: be sure to round the score to 2 decimal places.
    N = len(food_scores)
    sum_score = 0
    for i in range(N):
        sum_score += math.sqrt(food_scores[i] ** 2 *
                               customer_service_scores[i]) * 1 / (N * math.sqrt(125)) * 10
    return {restaurant_name: sum_score}


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string.
    # For example, you could use this function to return a prompt for the data fetch agent
    # to use to fetch reviews for a specific restaurant.

    pass

# TODO: feel free to write as many additional functions as you'd like.

# def finding_score(restaurant_review: Dict[str, List[str]]) -> int:
#     scoring_dict = {
#         1 : ["awful", "horrible", "disgusting"],
#         2 : ["bad", "unpleasant", "offensive"],
#         3 : ["average", "uninspiring", "forgettable"],
#         4 : ["good", "enjoyable", "satisfying"],
#         5 : ["awesome", "incredible", "amazing"]
#     }

#     for i in range(1, 6):


# Do not modify the signature of the "main" function.
def main(user_query: str):
    entrypoint_agent_system_message = ""  # TODO
    # example LLM config for the entrypoint agent
    llm_config = {"config_list": [
        {"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    # the main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent("entrypoint_agent",
                                        system_message=entrypoint_agent_system_message,
                                        llm_config=llm_config)

    # TODO
    # Create more agents here.

    fetch_message = """
    Expert in finding data and extracting features. Good at determining relevant data to fetch. using function fetch_restaurant_data.
    Notice, the name of the restaurant might be a little different from the real one. For example, sometimes it use ' ' rather than '-' to concate the words, etc. So be little tolerant for the input name.
    For example, "Chick-fil-A" could be "Chick fil A" or "Chick_fil_A".
    In this case, you should try every single possible name to fetch the reviews.
    """

    datafetch_agent = autogen.ConversableAgent(
        name="Data_fetch_agent",
        llm_config=llm_config,
        system_message=fetch_message
    )

    review_agent = autogen.ConversableAgent(
        name="Review_analysis_agent",
        llm_config=llm_config,
        system_message="Good at analyzing unstructured text restaurant reviews.(Extracting the food_score and the customer_service_score) The food_score and customer_service_score share a common rating system: Score 1 corresponds to one of these adjectives: awful, horrible, or disgusting. Score 2 corresponds to one of these adjectives: bad, unpleasant, or offensive. Score 3 corresponds to one of these adjectives: average, uninspiring, or forgettable. Score 4 corresponds to one of these adjectives: good, enjoyable, or satisfying. Score 5 corresponds to one of these adjectives: awesome, incredible, or amazing. Please output the result with reasoning."
    )

    score_messgae = """
    Expert in scoring the overall score of the restaurant based on the food_score and customer_service_score, using function calculate_overall_score. If it recieve or output the message in the format like : {restaurant_name: score}, summarize the output and end the conversation
    For example, if you recieve a json package:
    {"restaurant_name": "Chick-fil-A", "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]}
    You can use 
    "restaurant_name": "Chick-fil-A"
    "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] and 
    "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
    as args
    Return in r'\d*\.\d{3}' format.
    """

    scoring_agent = autogen.ConversableAgent(
        name="Scoring_agent",
        llm_config=llm_config,
        system_message=score_messgae
    )

    entrypoint_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    datafetch_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    datafetch_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    # datafetch_agent.register_for_llm(name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    # datafetch_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # review_agent.register_for_llm(name="finding_score", description="Finding restaurants's food_scores and customer_service_scores in the relevant reviews")(finding_score)
    # review_agent.register_for_execution(name="finding_score")(finding_score)

    entrypoint_agent.register_for_llm(
        name="calculate_overall_score", description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
    entrypoint_agent.register_for_execution(
        name="calculate_overall_score")(calculate_overall_score)

    scoring_agent.register_for_llm(name="calculate_overall_score",
                                   description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
    scoring_agent.register_for_execution(
        name="calculate_overall_score")(calculate_overall_score)

    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.
    task1 = f"""
    {user_query} and return "Dict[str, List[str]]" format(the former is the restaurant's name and the latter is the relavent reviews). Notice, the name of the restaurant might be a little different from the real one. For example, sometimes it use ' ' rather than '-' to concate the words, etc. So be little tolerant for the input name.
    """

    prefix1 = entrypoint_agent.initiate_chat(
        datafetch_agent,
        message=task1,
        max_turns=4,
        summary_method="last_msg",
    )

    task2 = f"""
    Extract the food_score and customer_service_score based on every reviews(List[str]) of the restaurant. Do it sentence by sentence, the length of the list food_score and customer_service_score are equal to the number of comments.
    Make sure food_score and customer_service_score have same length.
    """

    combined_message1 = f"{prefix1}\n\nNew task: {task2}"

    prefix2 = entrypoint_agent.initiate_chat(
        review_agent,
        message=combined_message1,
        max_turns=2,
        summary_method="last_msg",
    )

    task3 = r"""
    Calculate the overall score based on the food_score and customer_service_score. Using 'calculate_overall_score' function and "food_scores", "customer_service_scores" as args.
    For example, if you recieve a json package:
    {"restaurant_name": "Chick-fil-A", "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5], "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]}
    You can use 
    "restaurant_name": "Chick-fil-A"
    "food_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5] and 
    "customer_service_scores": [5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5]
    as args
    Return in r'\d*\.\d{3}' format.
    """

    combined_message2 = f"{prefix2}\n\nNew task: {task3}"

    result = entrypoint_agent.initiate_chat(
        scoring_agent,
        message=combined_message2,
        max_turns=3,
        summary_method="last_msg",
    )

    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(
        sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
