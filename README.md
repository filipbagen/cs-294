# CS294/194-196 Large Language Model Agents

This repository contains three labs that demonstrate the capabilities and security challenges of large language models (LLMs) through a series of hands-on tasks.

## Lab 1: 📝 Summarizing Unstructured, Natural-Language Data (Restaurant Reviews)

In this lab, I worked with Large Language Models (LLMs) to analyze unstructured text data from restaurant reviews. I used the OpenAI API to process and understand the reviews, making it a powerful tool for extracting meaningful insights.

### Lab Context
I focused on analyzing reviews to give each restaurant a score based on food and service quality. By using the AutoGen framework, I automated the process of fetching reviews, summarizing them, and answering queries about different restaurants.

### Key Features
- **Restaurant Review Analysis:** Fetches and processes restaurant reviews to extract ratings.
- **AutoGen Framework:** Used multi-agent workflows and sequential chats to coordinate review analysis.
- **Scoring System:** Created a keyword-based scoring system (1 to 5) for food and service.

### Example Queries
- "How good is Subway as a restaurant?"
- "What would you rate In N Out?"

[Explore Lab 1](./lab01)

---

## Lab 2: 🕵️ LLM Security - Writing Attack Prompts

With LLMs increasingly integrated into critical systems, it’s important to understand their vulnerabilities. In this lab, I explored adversarial prompt attacks, focusing on extracting sensitive information from a simulated system.

### Lab Context
I designed two attack prompts to extract a secret key hidden within the model’s system instructions. Each prompt exploits different techniques to deceive the model into revealing the information by embedding instructions in seemingly innocent requests.

### Key Features
- **Deceptive Code Simulation:** My first attack mimicked a request to generate and simulate code, subtly instructing the model to find and output the content following a specific keyword.
- **Narrative-based Puzzle Attack:** The second attack disguised the information extraction as a virtual escape room puzzle, with indirect hints leading to the system’s secret, engaging the model in a problem-solving scenario.

### Common Attack Techniques
- **Payload Splitting**
- **Virtualization**
- **Narrative Obfuscation**

[Explore Lab 2](./lab02)

---

## Lab 3: 🛡️ LLM Security - Writing Defense Prompts

In this lab, the focus shifts from attacking to defending. I worked on creating a robust defense prompt to shield LLMs from adversarial attacks aimed at extracting sensitive information like the secret key hidden within system messages.

### Lab Context
The challenge was to craft a defense prompt capable of withstanding attacks similar to those designed in Lab 2. This involved anticipating and neutralizing various exploitative techniques by instructing the model to maintain security and resist manipulation.

### Key Features
- **Defense Prompt Design:** I created a defense prompt that explicitly prevents sensitive data leaks, covering multiple attack scenarios.
- **Comprehensive Safeguarding Techniques:** The defense includes checks against creative or indirect methods of information extraction.

### Defense Techniques
- **Contextual Safeguards**
- **Obfuscation Detection**
- **Payload Splitting Prevention**

[Explore Lab 3](./lab03)
