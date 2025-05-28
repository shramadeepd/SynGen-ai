#!/usr/bin/env python3
"""
Test script for SynGen AI using real questions from test_questions.py
Tests both SQL and document queries with real data
"""

import asyncio
import json
import requests
import time
from typing import Dict, Any, List
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Questions from test_questions.py
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

class TestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.results = []
    
    def test_server_connection(self) -> bool:
        """Test if server is running"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Server is running")
                return True
            else:
                logger.error(f"❌ Server returned status: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Cannot connect to server: {e}")
            return False
    
    def query_api(self, question: str) -> Dict[str, Any]:
        """Send query to API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/query",
                json={"question": question},
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"API returned status {response.status_code}",
                    "details": response.text
                }
                
        except Exception as e:
            return {
                "error": f"Request failed: {str(e)}"
            }
    
    def evaluate_response(self, question: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate the response quality"""
        evaluation = {
            "question": question,
            "response": response,
            "status": "PASS",
            "issues": []
        }
        
        # Check for errors
        if "error" in response:
            evaluation["status"] = "FAIL"
            evaluation["issues"].append(f"Error: {response['error']}")
            return evaluation
        
        # Check response type and content
        response_type = response.get("type", "unknown")
        
        if response_type == "sql_query":
            # SQL query evaluation
            if "rows" not in response:
                evaluation["status"] = "FAIL"
                evaluation["issues"].append("Missing 'rows' in SQL response")
            elif not isinstance(response["rows"], list):
                evaluation["status"] = "FAIL"
                evaluation["issues"].append("'rows' is not a list")
            elif len(response["rows"]) == 0:
                evaluation["issues"].append("Query returned no results")
            
            if "sql" not in response:
                evaluation["issues"].append("Missing SQL query in response")
        
        elif response_type == "policy_query":
            # Document query evaluation
            if "answer" not in response:
                evaluation["status"] = "FAIL"
                evaluation["issues"].append("Missing 'answer' in document response")
            elif len(response.get("answer", "")) < 10:
                evaluation["status"] = "FAIL"
                evaluation["issues"].append("Answer too short")
            
            if "sources" not in response:
                evaluation["issues"].append("Missing sources in response")
        
        else:
            evaluation["issues"].append(f"Unknown response type: {response_type}")
        
        return evaluation
    
    def run_tests(self) -> Dict[str, Any]:
        """Run all tests"""
        logger.info("🚀 Starting SynGen AI test suite...")
        
        # Check server connection
        if not self.test_server_connection():
            return {"error": "Cannot connect to server"}
        
        # Test database stats
        try:
            stats_response = requests.get(f"{self.base_url}/api/stats", timeout=10)
            if stats_response.status_code == 200:
                stats = stats_response.json()
                logger.info(f"📊 Database stats: {stats['statistics']}")
            else:
                logger.warning("Could not retrieve database stats")
        except Exception as e:
            logger.warning(f"Stats check failed: {e}")
        
        # Run question tests
        passed = 0
        failed = 0
        
        for i, question in enumerate(QUESTIONS, 1):
            logger.info(f"\n--- Test {i}/{len(QUESTIONS)} ---")
            logger.info(f"Question: {question}")
            
            start_time = time.time()
            response = self.query_api(question)
            duration = time.time() - start_time
            
            evaluation = self.evaluate_response(question, response)
            evaluation["duration"] = round(duration, 2)
            
            # Log results
            if evaluation["status"] == "PASS":
                logger.info(f"✅ PASS ({duration:.2f}s)")
                if evaluation["issues"]:
                    logger.info(f"   ⚠️  Warnings: {'; '.join(evaluation['issues'])}")
                passed += 1
            else:
                logger.error(f"❌ FAIL ({duration:.2f}s)")
                logger.error(f"   Issues: {'; '.join(evaluation['issues'])}")
                failed += 1
            
            # Log response summary
            response_type = response.get("type", "unknown")
            if response_type == "sql_query":
                row_count = len(response.get("rows", []))
                logger.info(f"   SQL query returned {row_count} rows")
            elif response_type == "policy_query":
                answer_length = len(response.get("answer", ""))
                source_count = len(response.get("sources", []))
                logger.info(f"   Document query: {answer_length} chars, {source_count} sources")
            
            self.results.append(evaluation)
            time.sleep(0.5)  # Brief pause between requests
        
        # Summary
        summary = {
            "total_tests": len(QUESTIONS),
            "passed": passed,
            "failed": failed,
            "pass_rate": round((passed / len(QUESTIONS)) * 100, 1),
            "results": self.results
        }
        
        logger.info(f"\n{'='*50}")
        logger.info(f"🎯 TEST SUMMARY")
        logger.info(f"{'='*50}")
        logger.info(f"Total tests: {summary['total_tests']}")
        logger.info(f"Passed: {summary['passed']}")
        logger.info(f"Failed: {summary['failed']}")
        logger.info(f"Pass rate: {summary['pass_rate']}%")
        
        if summary['pass_rate'] >= 80:
            logger.info("🎉 EXCELLENT! System is working well")
        elif summary['pass_rate'] >= 60:
            logger.info("✅ GOOD! System is mostly functional")
        else:
            logger.warning("⚠️  NEEDS IMPROVEMENT! Many tests failed")
        
        return summary

if __name__ == "__main__":
    import sys
    
    base_url = "http://localhost:8000"
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    
    runner = TestRunner(base_url)
    results = runner.run_tests()
    
    # Save results
    with open("/mnt/d/Coding/SynGen-ai/test_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    
    logger.info(f"\n📄 Results saved to test_results.json")
    
    # Exit with appropriate code
    if results.get("pass_rate", 0) >= 80:
        sys.exit(0)
    else:
        sys.exit(1)