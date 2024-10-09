import math
from typing import Dict, List
from autogen import ConversableAgent
import sys
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


def analyze_reviews(reviews: List[str]) -> List[Dict[str, int]]:
    scores = []

    # Keyword mappings
    food_keywords = {
        "awful": 1, "horrible": 1, "disgusting": 1,
        "bad": 2, "unpleasant": 2, "offensive": 2,
        "average": 3, "uninspiring": 3, "forgettable": 3,
        "good": 4, "enjoyable": 4, "satisfying": 4,
        "awesome": 5, "incredible": 5, "amazing": 5
    }

    service_keywords = {
        "awful": 1, "horrible": 1, "disgusting": 1,
        "bad": 2, "unpleasant": 2, "offensive": 2,
        "average": 3, "uninspiring": 3, "forgettable": 3,
        "good": 4, "enjoyable": 4, "satisfying": 4,
        "awesome": 5, "incredible": 5, "amazing": 5
    }

    # Analyze each review for food and service quality scores
    for review in reviews:
        food_score, service_score = None, None

        for word in review.split():
            word = word.lower().strip('.,')
            if word in food_keywords and food_score is None:
                food_score = food_keywords[word]
            elif word in service_keywords and service_score is None:
                service_score = service_keywords[word]

            # Break early if both scores are found
            if food_score and service_score:
                break

        # If both scores were found, append them to the results
        if food_score and service_score:
            scores.append({"food_score": food_score,
                          "service_score": service_score})

    return scores


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    N = len(food_scores)
    score_sum = 0.0

    for i in range(N):
        score_sum += math.sqrt(food_scores[i]**2 * customer_service_scores[i])

    overall_score = (score_sum / (N * math.sqrt(125))) * 10
    return {restaurant_name: round(overall_score, 3)}


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    prompt = f"""
    The user is asking about the restaurant "{restaurant_query}".
    Your task is to find the reviews for this restaurant from the available dataset.
    Please fetch all reviews for the restaurant named "{restaurant_query}".
    """
    return prompt

# TODO: feel free to write as many additional functions as you'd like.

# Do not modify the signature of the "main" function.


def main(user_query: str):
    entrypoint_agent_system_message = """
        You are an entrypoint agent responsible for overseeing and coordinating conversations between other agents. 
        Your task is to manage queries related to restaurant reviews. First, analyze the user's query and extract the 
        relevant restaurant name. Then, interact with the data fetch agent to retrieve the appropriate reviews for that 
        restaurant. Once you have the reviews, pass them on for further processing and summarization.
        """

    # Example LLM config for the entrypoint agent
    llm_config = {"config_list": [
        {"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}

    # The main entrypoint/supervisor agent
    entrypoint_agent = ConversableAgent(
        "entrypoint_agent", system_message=entrypoint_agent_system_message, llm_config=llm_config)

    # Agents for the different tasks
    fetch_message = """
    You are responsible for fetching reviews for the requested restaurant. 
    Please find all reviews associated with the restaurant mentioned in the user query.
    """

    review_message = """
    Your task is to analyze the reviews and extract two scores for each review:
    - Food score based on the keywords: awesome, good, average, bad, etc.
    - Customer service score based on keywords: amazing, horrible, unpleasant, etc.
    """

    score_message = """
    Your task is to calculate the overall score based on the food and customer service 
    scores, and provide this score. Once done, no further actions are required.
    """

    datafetch_agent = ConversableAgent(
        name="Data_fetch_agent",
        llm_config=llm_config,
        system_message=fetch_message
    )

    review_agent = ConversableAgent(
        name="Review_analysis_agent",
        llm_config=llm_config,
        system_message=review_message
    )

    scoring_agent = ConversableAgent(
        name="Scoring_agent",
        llm_config=llm_config,
        system_message=score_message
    )

    entrypoint_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    datafetch_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    datafetch_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    review_agent.register_for_llm(
        name="finding_score", description="Finding restaurants's food_scores and customer_service_scores in the relevant reviews")(analyze_reviews)
    review_agent.register_for_execution(name="finding_score")(analyze_reviews)

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
    task1 = f"Fetch reviews for {user_query}."
    task2 = f"Analyze the fetched reviews and extract food_score and customer_service_score."
    task3 = f"Calculate overall score using the extracted scores."

    prefix1 = entrypoint_agent.initiate_chat(
        datafetch_agent,
        message=task1,
        max_turns=4,
        summary_method="last_msg",
    )

    combined_message1 = f"{prefix1}\n\nNew task: {task2}"

    prefix2 = entrypoint_agent.initiate_chat(
        review_agent,
        message=combined_message1,
        max_turns=2,
        summary_method="last_msg",
    )

    combined_message2 = f"{prefix2}\n\nNew task: {task3}"

    result = entrypoint_agent.initiate_chat(
        scoring_agent,
        message=combined_message2,
        max_turns=1,
        summary_method="last_msg",
    )


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(
        sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
