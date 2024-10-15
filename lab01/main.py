from typing import Dict, List
import sys
from autogen import ConversableAgent
import os
from dotenv import load_dotenv
import re

load_dotenv()

# my functions works, change prompts to vitaminds (some of them)


def normalize_name(name: str) -> str:
    # Remove special characters and convert to lowercase
    return re.sub(r'[^a-zA-Z0-9]', '', name).lower()


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    normalized_input_name = normalize_name(restaurant_name)
    restaurant_reviews = {}
    original_names = {}
    with open('restaurant-data.txt', 'r') as file:
        for line in file:
            name, review = line.split('. ', 1)
            name = name.strip()
            review = review.strip()
            normalized_name = normalize_name(name)
            if normalized_name not in restaurant_reviews:
                restaurant_reviews[normalized_name] = []
                original_names[normalized_name] = name
            restaurant_reviews[normalized_name].append(review)

    true_name = original_names.get(normalized_input_name, restaurant_name)
    return {true_name: restaurant_reviews.get(normalized_input_name, [])}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    print(f"Calculating overall score for {restaurant_name}")
    print(f"Food scores: {food_scores}")
    print(f"Customer service scores: {customer_service_scores}")
    N = len(food_scores)
    score_sum = 0.0
    for i in range(N):
        score_sum += (food_scores[i]**2 * customer_service_scores[i]) ** 0.5
    overall_score = (score_sum / (N * 125 ** 0.5)) * 10
    return {restaurant_name: round(overall_score, 3)}


def main(user_query: str):
    entrypoint_agent_system_message = """
        You are an AI assistant that helps users find the overall score of a restaurant based on reviews.
        Your task is to identify the restaurant name from the {user_query} by matching it with one famously known restaurant.
        Then, you will call the function fetch_restaurant_data and calculate_overall_score.
    """

    llm_config = {
        # "functions": [calculate_overall_score],
        "config_list": [
            {"model": "gpt-4o-mini", "api_key": os.environ.get("OPENAI_API_KEY")}]}
    entrypoint_agent = ConversableAgent(
        "entrypoint_agent", system_message=entrypoint_agent_system_message, llm_config=llm_config)

    fetch_message = """
            Expert in finding data and extracting features. Good at determining relevant data to fetch. using function
            fetch_restaurant_data. Notice, the name of the restaurant might be a little different from the real one.
            For example, sometimes it use ' ' rather than '-' to concate the words, etc. So be little tolerant for
            the input name. For example, "Chick-fil-A" could be "Chick fil A" or "Chick_fil_A". In this case, you
            should try every single possible name to fetch the reviews.
        """

    review_message = """
            You are an assistant that analyzes a list of restaurant reviews to extract food and customer service scores.
            Each review corresponds to exactly one food score and one customer service score.
            You must return the same number of scores as there are reviews.
            For each review:
            - Extract the keyword(s) corresponding to the quality of the food.
            - Extract the keyword(s) corresponding to the quality of the customer service.
            - Assign a food score and a customer service score between 1 and 5 based on the keywords.

            Keywords and their corresponding scores:
            - Score 1: awful, horrible, disgusting
            - Score 2: bad, unpleasant, offensive
            - Score 3: average, uninspiring, forgettable
            - Score 4: good, enjoyable, satisfying
            - Score 5: awesome, incredible, amazing

            Ensure the following:
            - Each review has exactly two scores: one food score and one customer service score.
            - The number of food and customer service scores must exactly match the number of reviews.
            - Return a dictionary with two keys: 'food_scores' and 'customer_service_scores', each containing a list of integers.
        """

    score_message = """
        You are a scoring agent responsible for calculating a restaurant's overall score based on two sets of
        scores: the food scores and the customer service scores.
        You will receive:
        1. The name of the restaurant as a string.
        2. A list of integers representing the **food scores**.
        3. A list of integers representing the **customer service scores**.
        Your task is to call the function `calculate_overall_score` with the provided inputs and return the overall score.
        It is important to use that function. If that is not possible, please use the formula provided below.


        1. Calculate the overall score for the restaurant by applying a specific formula.
        2. The formula is as follows:
        - For each review, multiply the food score by the customer service score, then take the square root of the result.
        - Sum up all the results.
        - Divide the total sum by \( N \times \sqrt(125) \), where \( N \) is the number of reviews.
        - Multiply the result by 10 to get the overall score.
        3. Return the overall score rounded to three decimal places, along with the restaurant's name.
        """
    datafetch_agent = ConversableAgent(
        name="data_fetch_agent",
        llm_config=llm_config,
        system_message=fetch_message,
        human_input_mode="NEVER"
    )
    review_agent = ConversableAgent(
        name="review_analysis_agent",
        llm_config=llm_config,
        system_message=review_message,
        human_input_mode="NEVER"
    )
    scoring_agent = ConversableAgent(
        name="scoring_agent",
        llm_config=llm_config,
        system_message=score_message,
        human_input_mode="NEVER"
    )
    # Register the functions for each agent
    print("Registering fetch_restaurant_data function")
    entrypoint_agent.register_for_llm(
        name="fetch_restaurant_data",
        description="Fetches the reviews for a specific restaurant."
    )(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(
        name="fetch_restaurant_data"
    )(fetch_restaurant_data)
    datafetch_agent.register_for_llm(
        name="fetch_restaurant_data",
        description="Fetches the reviews for a specific restaurant."
    )(fetch_restaurant_data)
    datafetch_agent.register_for_execution(
        name="fetch_restaurant_data"
    )(fetch_restaurant_data)
    print("Registering calculate_overall_score function")
    entrypoint_agent.register_for_llm(
        name="calculate_overall_score",
        description="Calculate restaurants's overall scores based on food_scores and customer_service_scores"
    )(calculate_overall_score)
    entrypoint_agent.register_for_execution(
        name="calculate_overall_score"
    )(calculate_overall_score)
    scoring_agent.register_for_llm(
        name="calculate_overall_score",
        description="Calculate restaurants's overall scores based on food_scores and customer_service_scores"
    )(calculate_overall_score)
    scoring_agent.register_for_execution(
        name="calculate_overall_score"
    )(calculate_overall_score)

    # Start the conversation
    fetch_reviews_task = f"""
            Take the input, {user_query}, and return it in the format "Dict[str, List[str]]"
            where str is the restaurant's name and List[str] contains every available review of
            the restaurant. Be tolerant with the input name, as the actual restaurant name might
            use spaces, hyphens, or similar small differences.
        """
    analyze_reviews_task = """
            Analyze the reviews fetched in the previous task. Extract `food_score` and
            `customer_service_score` for each review based on your scoring criteria, and
            return the results in the format:
            `[(food_score1, customer_service_score1), (food_score2, customer_service_score2), ...]`
        """
    calculate_overall_task = """
            Calculate the overall score for the restaurant based on `food_scores` and
            `customer_service_scores`. It is important to use the function 'calculate_overall_score'!
            Example Input:
            {
            "restaurant_name": "Chick-fil-A",
            "food_scores": [5, 5, 5, ...],
            "customer_service_scores": [5, 5, 5, ...]
            }
            Return the overall score in the format: `0.000`.
        """
    fetched_reviews = entrypoint_agent.initiate_chat(
        datafetch_agent,
        message=fetch_reviews_task,
        max_turns=2,
        summary_method="last_msg",
    )
    analyzed_reviews = entrypoint_agent.initiate_chat(
        review_agent,
        message=f"{fetched_reviews}\n\nNew task: {analyze_reviews_task}",
        max_turns=2,
        summary_method="last_msg",
    )
    entrypoint_agent.initiate_chat(
        scoring_agent,
        message=f"{analyzed_reviews}\n\nNew task: {calculate_overall_task}",
        max_turns=2,
        summary_method="last_msg",
    )


if __name__ == "__main__":
    assert len(
        sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
