import math
from typing import Dict, List
import sys
import autogen
import os
from dotenv import load_dotenv

load_dotenv()


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
    N = len(food_scores)
    score_sum = 0.0

    for i in range(N):
        score_sum += math.sqrt(food_scores[i]**2 * customer_service_scores[i])

    overall_score = (score_sum / (N * math.sqrt(125))) * 10
    return {restaurant_name: round(overall_score, 3)}


def main(user_query: str):
    entrypoint_agent_system_message = """
        You are an entrypoint agent responsible for overseeing and coordinating conversations between other agents.
        Your task is to manage queries related to restaurant reviews. First, analyze the user's query and extract the
        relevant restaurant name. Then, interact with the data fetch agent to retrieve the appropriate reviews for that
        restaurant. Once you have the reviews, pass them on for further processing and summarization.
    """

    # LLM config for the entrypoint agent
    llm_config = {"config_list": [
        {"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # The main entrypoint/supervisor agent
    entrypoint_agent = autogen.ConversableAgent(
        "entrypoint_agent", system_message=entrypoint_agent_system_message, llm_config=llm_config)

    # Messages for the data fetch agent, review analysis agent, and scoring agent
    fetch_message = """
        Expert in finding data and extracting features. Good at determining relevant data to fetch. using function fetch_restaurant_data.
        Notice, the name of the restaurant might be a little different from the real one. For example, sometimes it use ' ' rather than '-' to concate the words, etc. So be little tolerant for the input name.
        For example, "Chick-fil-A" could be "Chick fil A" or "Chick_fil_A".
        In this case, you should try every single possible name to fetch the reviews.
    """

    review_message = """
        You are a review analysis agent responsible for analyzing customer reviews of restaurants. 
        Each review contains descriptions of both the food and the customer service, and your task 
        is to extract two separate scores: one for the food and one for the customer service.

        You will assign a score to each aspect based on the following adjectives present in the review:

        1. **Score 1/5** has one of these adjectives: awful, horrible, disgusting.
        2. **Score 2/5** has one of these adjectives: bad, unpleasant, offensive.
        3. **Score 3/5** has one of these adjectives: average, uninspiring, forgettable.
        4. **Score 4/5** has one of these adjectives: good, enjoyable, satisfying.
        5. **Score 5/5** has one of these adjectives: awesome, incredible, amazing.

        Each review will contain exactly two adjectives: one describing the food and one describing the 
        customer service. You will assign the food score based on the adjective describing food and the 
        customer service score based on the adjective describing service.

        Your output should be structured as two lists of integers:
        - One list contains the **food scores** for all reviews.
        - One list contains the **customer service scores** for all reviews.
    """

    score_message = """
       You are a scoring agent responsible for calculating a restaurant's overall score based on two sets of 
       scores: the food scores and the customer service scores. 

        You will receive:
        1. The name of the restaurant as a string.
        2. A list of integers representing the **food scores**.
        3. A list of integers representing the **customer service scores**.

        Your task is to:
        1. Calculate the overall score for the restaurant by applying a specific formula.
        2. The formula is as follows:
        - For each review, multiply the food score by the customer service score, then take the square root of the result.
        - Sum up all the results.
        - Divide the total sum by \( N \times \sqrt{125} \), where \( N \) is the number of reviews.
        - Multiply the result by 10 to get the overall score.
        3. Return the overall score rounded to three decimal places, along with the restaurant's name.
    """

    # Agents for data fetching, review analysis, and scoring
    datafetch_agent = autogen.ConversableAgent(
        name="data_fetch_agent",
        llm_config=llm_config,
        system_message=fetch_message
    )

    review_agent = autogen.ConversableAgent(
        name="review_analysis_agent",
        llm_config=llm_config,
        system_message=review_message
    )

    scoring_agent = autogen.ConversableAgent(
        name="scoring_agent",
        llm_config=llm_config,
        system_message=score_message
    )

    # Register the functions for each agent
    entrypoint_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    datafetch_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    datafetch_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    entrypoint_agent.register_for_llm(
        name="calculate_overall_score", description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
    entrypoint_agent.register_for_execution(
        name="calculate_overall_score")(calculate_overall_score)

    scoring_agent.register_for_llm(name="calculate_overall_score",
                                   description="Calculate restaurants's overall scores based on food_scores and customer_service_scores")(calculate_overall_score)
    scoring_agent.register_for_execution(
        name="calculate_overall_score")(calculate_overall_score)

    # Start the conversation
    task1 = f"""
        Take the input, {user_query}, and return it in the format "Dict[str, List[str]]"
        where str is the restaurant's name and List[str] contains every avalible review of
        the restaurant. The true name of the restaurant might be a little different from the
        input name. For example, sometimes it use ' ' rather than '-' to concate the words, etc.
        So be little tolerant for the input name.
    """

    task2 = f"""
        Convert the restaurant reviews to scores.

        Extract the food_score and customer_service_score based on every reviews(List[str]) of the restaurant. Do it sentence by sentence, the length of the list food_score and customer_service_score are equal to the number of comments.
        Make sure food_score and customer_service_score have same length.
    """

    task2 = """
        Please analyze the reviews fetched in the previous task. Extract the `food_score` and
        `customer_service_score` for each review based on your scoring criteria, and return two lists:

        1. A list of `food_scores`.
        2. A list of `customer_service_scores`.

        Make sure to process all the reviews and return the scores in the following format:

        `[(food_score1, customer_service_score1), (food_score2, customer_service_score2), ...]`
    """

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

    prefix1 = entrypoint_agent.initiate_chat(
        datafetch_agent,
        message=task1,
        max_turns=4,
        summary_method="last_msg",
    )

    prefix2 = entrypoint_agent.initiate_chat(
        review_agent,
        message=f"{prefix1}\n\nNew task: {task2}",
        max_turns=2,
        summary_method="last_msg",
    )

    entrypoint_agent.initiate_chat(
        scoring_agent,
        message=f"{prefix2}\n\nNew task: {task3}",
        max_turns=3,  # 1
        summary_method="last_msg",
    )


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(
        sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
