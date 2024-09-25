# Review Moderation Tool

## Overview
This is a Streamlit-based web application that helps analyze online reviews using both rule-based and machine learning moderation metrics. The tool utilizes the SightEngine API for moderation checks and OpenAI's GPT model to generate a detailed analysis of the review's legitimacy, sentiment, and overall conclusion.

## Features
- **Rule-based moderation**: Checks for various categories like profanity, personal attacks, spam, violence, etc.
- **Machine Learning moderation**: Provides metrics on general categories, including self-harm or violence.
- **Sentiment Analysis**: Generates a detailed analysis of the review, including a legitimacy score (0 to 1), sentiment (positive, negative, neutral), and a conclusion statement.

## Requirements

- Python 3.11
- Streamlit
- OpenAI Python Client
- python-dotenv
- SightEngine

## Installation

1. Clone the repository or download the code.

2. Create a `.env` file in the project root directory and add your OpenAI API key.

3. Run the app locally:

    - Create and activate a virtual environment:

    ```bash
    python -m venv venv
    venv\Scripts\activate # On Windows
    source venv/bin/activate  # On macOS/Linux
    ```

    - Install the requirements

    ```bash
    pip install -r requirements.txt
    ```
    - Run the app:

    ```bash
    streamlit run app.py
    ```

4. Run the app using docker:

    ```bash
    docker build -t review-moderation-app .
    docker run -p 8501:8501 review-moderation-app
    ```
