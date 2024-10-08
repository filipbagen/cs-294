from typing import Dict, List
from autogen import ConversableAgent
import sys
import os


def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # Read the data from restaurant-data.txt
    with open('restaurant-data.txt') as f:
        data = f.read()

        # For each row, find the first word that starts with restaurant_name
        reviews = []
        for row in data.split("\n"):
            # If the row starts with the restaurant name, add the review to the list
            if row.startswith(restaurant_name):
                reviews.append(" ".join(row.split()[1:]))

    return {restaurant_name: reviews}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    N = len(food_scores)

    # Check for invalid inputs
    if N == 0:
        raise ValueError("The list of scores cannot be empty")

    if len(customer_service_scores) != N:
        raise ValueError(
            "The length of the food scores and customer service scores must be the same")

    total_score = 0
    for i in range(N):
        total_score += (food_scores[i]**2 *
                        customer_service_scores[i])**0.5 * 1/(N * 125**0.5)

    return {restaurant_name: total_score * 10}


def get_data_fetch_agent_prompt(restaurant_query: str) -> str:
    # TODO
    # It may help to organize messages/prompts within a function which returns a string.
    # For example, you could use this function to return a prompt for the data fetch agent
    # to use to fetch reviews for a specific restaurant.
    pass

# TODO: feel free to write as many additional functions as you'd like.

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
    entrypoint_agent.register_for_llm(
        name="fetch_restaurant_data", description="Fetches the reviews for a specific restaurant.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(
        name="fetch_restaurant_data")(fetch_restaurant_data)

    # TODO
    # Create more agents here.

    # TODO
    # Fill in the argument to `initiate_chats` below, calling the correct agents sequentially.
    # If you decide to use another conversation pattern, feel free to disregard this code.

    # Uncomment once you initiate the chat with at least one agent.
    # result = entrypoint_agent.initiate_chats([{}])


# DO NOT modify this code below.
if __name__ == "__main__":
    assert len(
        sys.argv) > 1, "Please ensure you include a query for some restaurant when executing main."
    main(sys.argv[1])
