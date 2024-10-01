import os
import time
import requests
import json
import streamlit as st
import openai
from dotenv import load_dotenv

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
SIGHTENGINE_API_USER = os.getenv("SIGHTENGINE_API_USER")
SIGHTENGINE_API_SECRET = os.getenv("SIGHTENGINE_API_SECRET")


class SightEngineService:

    def get_sightengine_response(self, text):
        try:
            rule_based_moderation_data = {
                "text": text,
                "mode": "rules",
                "lang": "en",
                "categories": "profanity,personal,link,drug,weapon,spam,content-trade,money-transaction,extremism,violence,self-harm,medical",
                "api_user": SIGHTENGINE_API_USER,
                "api_secret": SIGHTENGINE_API_SECRET,
            }
            rule_based_moderation_response = requests.post(
                "https://api.sightengine.com/1.0/text/check.json",
                data=rule_based_moderation_data,
            )
            rule_based_moderation_output = json.loads(
                rule_based_moderation_response.text
            )

            ml_based_moderation_data = {
                "text": text,
                "mode": "ml",
                "lang": "en",
                "models": "general,self-harm",
                "api_user": SIGHTENGINE_API_USER,
                "api_secret": SIGHTENGINE_API_SECRET,
            }
            ml_based_moderation_response = requests.post(
                "https://api.sightengine.com/1.0/text/check.json",
                data=ml_based_moderation_data,
            )

            ml_based_moderation_output = json.loads(ml_based_moderation_response.text)
            return rule_based_moderation_output, ml_based_moderation_output
        except Exception as e:
            print(e)
            return None, None


class OpenAIChat:
    def __init__(self):
        self.openai_client = openai.Client(api_key=OPENAI_API_KEY)
        self.prompt = """
You are tasked with analyzing an online review and determining the legitimacy of the sentiment. You have been provided with both rule-based and machine learning moderation metrics. 

- Legitimacy should be expressed as a value from 0 to 1, where 0 indicates a completely illegitimate review, and 1 indicates a fully legitimate review.
- Sentiment analysis should consider both the text and the provided metrics to gauge whether the review is positive, negative, or neutral.
- The output should include the legitimacy score, sentiment (positive/negative/neutral), and a single conclusion statement summarizing the overall review.

Please provide a concise analysis.
"""

    def generate_post(
        self, input_data, rule_based_moderation_output, ml_based_moderation_output
    ):

        try:
            if rule_based_moderation_output and ml_based_moderation_output:
                message_content = f"""
Here are the metrics for the review that provide insights into the review:
Rule-based metrics:
{rule_based_moderation_output}
ML-based metrics:
{ml_based_moderation_output}

Here is the review data:
{input_data}
"""
            else:
                message_content = f"""Here is the review data:\n{input_data}"""
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that identifies and analyzes reviews.",
                    },
                    {
                        "role": "user",
                        "content": f"{self.prompt}\n\n{message_content}",
                    },
                ],
                temperature=0.1,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(e)
            st.error("An error occurred. Please try again later.")


if __name__ == "__main__":

    # Initialize session state variables
    if "review_analysis" not in st.session_state:
        st.session_state.review_analysis = None
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False

    review_form = st.form("review_form", clear_on_submit=True)
    review_form.title("Review Moderation Bot")

    review_form.markdown("")
    review = review_form.text_area("Review", placeholder="Provide the content of the review you wish to analyze").strip()
    stakeholder = review_form.text_input(
        "Stakeholder", placeholder="Enter the name of the stakeholder (e.g., Restaurant or Hotel Name)"
    ).strip()
    platform = review_form.selectbox(
        "Platform", options=["", "Google", "Yelp", "TripAdvisor", "Other"], help="Select the platform where the review was posted"
    )
    review_form.markdown("\nRating")
    selected_rating = review_form.feedback("stars")
    rating = 0
    if selected_rating is not None:
        rating = selected_rating + 1
    all_fields = review and stakeholder and platform
    submitted = review_form.form_submit_button(
        label="Analyze Review", disabled=st.session_state.analysis_started
    )

    if submitted:
        if all_fields:
            # Mark the analysis as started
            st.session_state.analysis_started = True
            with st.spinner("Analyzing Review..."):
                input_data = {
                    "review": review,
                    "stakeholder": stakeholder,
                    "rating": rating,
                    "platform": platform,
                }
                rule_based_moderation_output, ml_based_moderation_output = (
                    SightEngineService().get_sightengine_response(text=review)
                )
                st.session_state.review_analysis = OpenAIChat().generate_post(
                    input_data=input_data,
                    rule_based_moderation_output=rule_based_moderation_output,
                    ml_based_moderation_output=ml_based_moderation_output,
                )
            # Enable the form again after analysis
            st.session_state.analysis_started = False
        else:
            error_placeholder = st.empty()
            error_placeholder.error("Please fill all the fields")
            time.sleep(3)
            error_placeholder.empty()

    # Display the review analysis
    if st.session_state.review_analysis:
        st.title("Review Analysis")
        st.markdown("---")
        st.markdown(f"**Review content:** {review}")
        st.markdown(f"**Stakeholder:** {stakeholder}")
        st.markdown(f"**Rating:** {rating}")
        st.markdown(f"**Platform where review was posted:** {platform}")
        st.markdown("---")
        st.markdown(st.session_state.review_analysis)
