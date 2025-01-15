"""
Script for text moderation using the Eden AI content moderation API.
This script allows batch processing from an Excel file or a single manual test.
"""

import os
import time
import requests
import pandas as pd
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

# Environment variables
API_KEY = os.getenv("API_KEY")
API_URL_POST = os.getenv("API_URL_POST")
API_URL_GET = os.getenv("API_URL_GET")

# API headers
headers = {
    "Authorization": f"Bearer {API_KEY}",
}

def post_text_to_moderate(text):
    """
    Sends text to the moderation API via a POST request and returns the execution ID.

    Args:
        text (str): The text to moderate.

    Returns:
        str: The execution ID of the moderation request.

    Raises:
        Exception: If no ID is returned in the POST response.
    """
    payload = {"text": text}
    response = requests.post(API_URL_POST, json=payload, headers=headers)
    result = response.json()

    if "id" in result:
        return result["id"]
    else:
        raise Exception("Error: No ID found in the POST response.")

def get_moderation_result(execution_id):
    """
    Retrieves moderation results from the API via a GET request.
    Waits until the result is ready.

    Args:
        execution_id (str): The ID of the moderation request.

    Returns:
        dict: The moderation results.

    Raises:
        Exception: If the moderation process fails or encounters an unexpected status.
    """
    url = API_URL_GET.replace("{execution_id}", execution_id)
    wait_interval = 5  # Seconds between attempts

    while True:
        response = requests.get(url, headers=headers)
        result = response.json()
        status = result.get("content", {}).get("status", "")

        if status == "succeeded":
            return result
        elif status == "failed":
            raise Exception(f"Moderation failed: {result}")
        elif status == "processing":
            time.sleep(wait_interval)
        else:
            raise Exception(f"Unexpected status: {status}")

def process_moderation_results(results, rejection_threshold=0.2):
    """
    Processes moderation results and determines rejection status based on a threshold.

    Args:
        results (dict): The moderation results.
        rejection_threshold (float): Threshold for rejecting text based on NSFW likelihood.

    Returns:
        tuple: Rejection chance (float), highest category (str), status (str).
    """
    moderation_results = results.get("content", {}).get("results", {})
    if "text__moderation" not in moderation_results:
        return 0, "Unknown", "success"

    text_results = moderation_results["text__moderation"].get("results", [])
    for result in text_results:
        nsfw_likelihood_score = result.get("nsfw_likelihood_score", 0)
        status = "rejected" if nsfw_likelihood_score >= rejection_threshold else "validated"
        highest_category = "Unknown"
        highest_score = 0
        items = result.get("items", [])
        for subitem in items:
            if subitem.get("likelihood_score", 0) > highest_score:
                highest_category = subitem.get("category", "Unknown")
                highest_score = subitem.get("likelihood_score", 0)
        return nsfw_likelihood_score * 100, highest_category, status

    return 0, "Unknown", "succeeded"

def process_file(file_path):
    """
    Processes a batch of texts from an Excel file and writes results to a new file.

    Args:
        file_path (str): Path to the input Excel file.

    Raises:
        Exception: If the input file is missing required columns or encounters errors.
    """
    df = pd.read_excel(file_path)

    if "Données à tester" not in df.columns:
        raise Exception("Error: 'Données à tester' column is missing in the input file.")

    df["Taux de rejet (%)"] = 0.0
    df["Catégorie"] = ""
    df["Status"] = ""

    for index, row in tqdm(df.iterrows(), total=len(df), desc="Processing rows"):
        text = row["Données à tester"]
        try:
            execution_id = post_text_to_moderate(text)
            results = get_moderation_result(execution_id)
            rejection_chance, category, status = process_moderation_results(results)
            df.at[index, "Taux de rejet (%)"] = float(rejection_chance)
            df.at[index, "Catégorie"] = str(category)
            df.at[index, "Status"] = str(status)
        except Exception as error:
            tqdm.write(f"Error processing row {str(index)}: {error}")
            df.at[index, "Status"] = "Error"

    df.to_excel("SyntheticDataResult.xlsx", index=False)
    print(f"Results saved")

def test_single_text():
    """
    Processes a single text input for moderation.
    """
    text = input("Enter the text to moderate: ")
    try:
        execution_id = post_text_to_moderate(text)
        results = get_moderation_result(execution_id)
        rejection_chance, category, status = process_moderation_results(results)
        print("\n--- Results ---")
        print(f"Rejection Chance: {rejection_chance:.2f}%")
        print(f"Category: {category}")
        print(f"Status: {status}")
    except Exception as error:
        print(f"Error: {error}")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Process a complete file")
    print("2. Test a single input manually")
    choice = input("Your choice (1 or 2): ")

    if choice == "1":
        input_file = input("Enter the path to the input Excel file: ")
        try:
            process_file(input_file)
        except Exception as e:
            print(f"Error: {e}")
    elif choice == "2":
        test_single_text()
    else:
        print("Invalid choice. Please restart the script.")
