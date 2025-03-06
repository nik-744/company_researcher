import groq
import streamlit as st
from duckduckgo_search import DDGS  
from serpapi import GoogleSearch

import os
from dotenv import load_dotenv
load_dotenv()

# Get API keys from environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERP_API_KEY = os.getenv("SERP_API_KEY")

# Initialize Groq client (use a secure way to store API keys)
groq_client = groq.Client(api_key=GROQ_API_KEY)  

# Function to search company information
def search_company(company_name):
    with DDGS() as dgs:  # Corrected usage
        search_results = list(dgs.text(company_name, max_results=3))  # Corrected function usage
    return search_results

# Function to summarize search results using Groq AI
def summarize_search_results(company_name, search_results):
    prompt = f"""
    Research the company "{company_name}" based on the following search results: {search_results}
    As the search is basically made as an individual has his/her interview over their.
    Provide necessary information about the company which you think is important for the interview in a well structured format.
    """
    response = groq_client.chat.completions.create(  # Fixed API call
        model="llama3-8b-8192",
        messages=[{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": prompt}],
        max_tokens=250,
    )
    return response.choices[0].message.content.strip()

def get_linkedin_profile(company_name):
    params ={
        "q": company_name + " linkedin",
        "api_key": SERP_API_KEY
    }
    search = GoogleSearch(params)
    results = search.get_dict()

    if "organic_results" in results:
        for result in results["organic_results"]:
            if "linkedin.com" in result["link"]:
                return result["link"]
    return "No LinkedIn profile found"


# Streamlit UI
st.title("🔍 Company Researcher Agent")

company_name = st.text_input("Enter the company name:")
if st.button("Research"):
    if company_name:
        st.write("🔎 Searching for company details...")
        search_results = search_company(company_name)
        
        if search_results:
            st.write("✅ Information found! Summarizing...")
            summary = summarize_search_results(company_name, search_results)  # Fixed function call
            st.success(summary)
        else:
            st.error("❌ No information found! Try again with a different company name.")
        linkedin = get_linkedin_profile(company_name)
        st.write(f"🔗 [View LinkedIn Profile]({linkedin}")
