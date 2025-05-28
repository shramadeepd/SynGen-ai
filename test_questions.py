# Test script for evaluating the application based on sample questions.
# This script is a template. You will need to adapt the
# `query_application` function to interact with your actual application
# and refine the `evaluate_response` function based on expected outputs
# for each question.

import json
import requests

# Questions extracted from d:\Coding\SynGen-ai\test_questions.txt
QUESTIONS = [
    "What is the total sales amount for all orders?",
    "What is our company's definition of slow-moving inventory according to the Inventory Management policy?",
    "What are the required steps for handling obsolete inventory write-offs?",
    "What sustainability practices should our logistics partners follow according to our Environmental Sustainability policy?",
    "What criteria do we use to qualify new suppliers based on our Supplier Selection policy?",
    "How does our Returns and Reverse Logistics policy handle customer claims for damaged products?",
    "What are the key performance indicators for measuring supplier performance as defined in our Performance Measurement policy?",
    "What cyber security measures must be implemented to protect supply chain data according to our Data Security policy?",
    "What was the total sales amount for the Southwest region in the last quarter?",
    "Which products have the highest profit margin across all categories?",
    "Which shipping mode has the lowest rate of on-time deliveries?",
    "Who are our top 10 customers by total order value?",
    "What is the average time between order date and shipping date by country?",
    "Which product categories have shown declining sales over the past three quarters?",
    "What is the distribution of orders by customer segment and region?",
    "Which inventory items qualify as \"no-movers\" according to our policy, and what is their total current value?",
    "Are there any suppliers who don't meet our minimum ethical sourcing requirements as defined in our Supplier Code of Conduct, and what percentage of our total spend do they represent?",
    "Based on our Product Quality Assurance standards, which products had the highest number of quality-related returns in the past year?",
    "According to our Transportation and Logistics policy, are we using the optimal shipping modes for high-value orders to international destinations?",
    "Which products that are classified as \"hazardous materials\" according to our HSE policy are currently being stored in facilities not certified for such materials?",
    "Based on our Risk Management framework, which supply chain disruptions occurred in the past year that exceeded our defined risk tolerance thresholds, and what was their financial impact?"
]

def query_application(question: str) -> any:
    """
    Query the SynGen AI application API with real implementation
    """
    print(f"\n[INFO] Sending query to application: \"{question}\"")
    
    try:
        import requests
        # Use the actual API endpoint
        response = requests.post(
            "http://localhost:8000/api/query", 
            json={"question": question}, 
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] API request failed: {str(e)}")
        return {"error": f"API request failed: {str(e)}"}
    except Exception as e:
        print(f"[ERROR] Unexpected error: {str(e)}")
        return {"error": f"Unexpected error: {str(e)}"}

def evaluate_response(question: str, response: any) -> tuple[bool, str]:
    """
    Evaluates the response from the application.
    Checks for basic flaws. This function should be significantly expanded
    with more specific checks based on expected outcomes for each question.
    
    Returns:
        tuple[bool, str]: (is_valid, flaw_description_or_success_message)
    """
    print(f"[INFO] Received response: {json.dumps(response, indent=2) if isinstance(response, (dict, list)) else response}")

    # 1. Basic checks for any response
    if response is None:
        return False, "Flaw: No response received from the application (response is None)."
    
    if isinstance(response, dict) and "error" in response:
        return False, f"Flaw: Application returned an error: {response.get('error_details', response['error'])}"

    # 2. Generic content checks
    # If response is expected to be a dict with an 'answer' key
    if isinstance(response, dict):
        if "answer" not in response:
            return False, "Flaw: Response is a dictionary but missing the 'answer' key."
        if not response["answer"] and response["answer"] != 0 and response["answer"] != False: # Allow 0 and False as valid answers
             # This might be a flaw or expected for some queries (e.g., "no items found")
             # You'll need to decide based on the question.
            print(f"[WARNING] Response 'answer' field is empty: {response['answer']}") 
            # return False, "Flaw: Response 'answer' field is empty." # Uncomment if empty answer is always a flaw

    # 3. Question-specific checks (examples - expand significantly)
    question_lower = question.lower()
    
    if "total sales amount" in question_lower:
        if not (isinstance(response, dict) and "answer" in response and isinstance(response["answer"], (int, float))):
            return False, f"Flaw: Expected a numerical sales amount in 'answer', got: {type(response.get('answer')) if isinstance(response, dict) else type(response)}"
        if response["answer"] < 0:
            return False, f"Flaw: Sales amount cannot be negative, got: {response['answer']}"
            
    elif "definition of" in question_lower or "policy" in question_lower or "steps for" in question_lower:
        if not (isinstance(response, dict) and "answer" in response and isinstance(response["answer"], str) and len(response["answer"]) > 10): # Arbitrary length
            return False, f"Flaw: Expected a textual policy description (string, length > 10) in 'answer', got: {response}"
            
    elif "which products" in question_lower or "top 10 customers" in question_lower or "which inventory items" in question_lower:
        if not (isinstance(response, dict) and "answer" in response and isinstance(response["answer"], list)):
            return False, f"Flaw: Expected a list of items in 'answer', got: {type(response.get('answer')) if isinstance(response, dict) else type(response)}"
        if "top 10 customers" in question_lower and (not response["answer"] or len(response["answer"]) > 10):
             # This check depends on whether an empty list is acceptable or if it must be exactly 10
             pass # Add more specific logic here

    # Add more checks for other question types:
    # - "average time": expect number or specific string format
    # - "distribution": expect dict or list of dicts with certain keys
    # - "yes/no" questions (e.g., "Are there any suppliers..."): expect boolean or clear textual confirmation/denial.

    # If no specific flaws detected by the above, assume basic validity.
    # More sophisticated checks would involve:
    # - Comparing against known correct answers (if available).
    # - Schema validation for structured data.
    # - Semantic correctness (harder, might require NLP or domain knowledge).
    return True, "Success: Response passed basic checks (further validation may be needed)."

def main():
    print("Starting Test Script for Application Backend Queries...")
    passed_tests = 0
    failed_tests = 0
    test_results_summary = []

    for i, question_text in enumerate(QUESTIONS):
        print(f"\n--- Test Case {i+1}/{len(QUESTIONS)} ---")
        application_response = query_application(question_text)
        is_valid, message = evaluate_response(question_text, application_response)

        result_status = "PASS" if is_valid else "FAIL"
        print(f"[{result_status}] {message}")
        
        if is_valid:
            passed_tests += 1
        else:
            failed_tests += 1
        
        test_results_summary.append({"question_id": i+1, "question": question_text, "status": result_status, "details": message, "response": application_response})

    print("\n--- Test Execution Summary ---")
    print(f"Total tests run: {len(QUESTIONS)}")
    print(f"Tests Passed: {passed_tests}")
    print(f"Tests Failed: {failed_tests}")

    # Save detailed results to test_results.json
    report_file = "test_results.json"
    with open(report_file, "w") as f:
        json.dump(test_results_summary, f, indent=4)
    print(f"\nDetailed test report saved to {report_file}")

if __name__ == "__main__":
    main()