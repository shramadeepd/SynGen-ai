#!/usr/bin/env python3
"""
SynGen AI - Comprehensive API Test Suite
Tests all endpoints and functionalities with detailed reporting
"""

import requests
import json
import time
import sys
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:8000"
TIMEOUT = 30

# Test Results Storage
@dataclass
class TestResult:
    name: str
    endpoint: str
    method: str
    status: str  # PASS, FAIL, SKIP
    response_code: Optional[int] = None
    response_time: Optional[float] = None
    error_message: Optional[str] = None
    details: Optional[str] = None

class APITester:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = TIMEOUT
        self.test_results: List[TestResult] = []
        self.auth_token: Optional[str] = None
        
        # Colors for output
        self.COLORS = {
            'RED': '\033[0;31m',
            'GREEN': '\033[0;32m',
            'YELLOW': '\033[1;33m',
            'BLUE': '\033[0;34m',
            'PURPLE': '\033[0;35m',
            'CYAN': '\033[0;36m',
            'NC': '\033[0m'  # No Color
        }
    
    def log(self, message: str, color: str = 'BLUE'):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{self.COLORS[color]}[{timestamp}] {message}{self.COLORS['NC']}")
    
    def success(self, message: str):
        print(f"{self.COLORS['GREEN']}✅ {message}{self.COLORS['NC']}")
    
    def error(self, message: str):
        print(f"{self.COLORS['RED']}❌ {message}{self.COLORS['NC']}")
    
    def warning(self, message: str):
        print(f"{self.COLORS['YELLOW']}⚠️  {message}{self.COLORS['NC']}")
    
    def info(self, message: str):
        print(f"{self.COLORS['CYAN']}ℹ️  {message}{self.COLORS['NC']}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper error handling"""
        url = f"{self.base_url}{endpoint}"
        
        # Add auth header if available
        if self.auth_token and 'headers' not in kwargs:
            kwargs['headers'] = {}
        if self.auth_token:
            kwargs['headers']['Authorization'] = f"Bearer {self.auth_token}"
        
        start_time = time.time()
        try:
            response = self.session.request(method, url, **kwargs)
            response_time = time.time() - start_time
            return response, response_time
        except requests.exceptions.RequestException as e:
            response_time = time.time() - start_time
            raise Exception(f"Request failed: {str(e)}")
    
    def add_result(self, name: str, endpoint: str, method: str, status: str, 
                   response_code: Optional[int] = None, response_time: Optional[float] = None,
                   error_message: Optional[str] = None, details: Optional[str] = None):
        """Add test result"""
        result = TestResult(
            name=name,
            endpoint=endpoint,
            method=method,
            status=status,
            response_code=response_code,
            response_time=response_time,
            error_message=error_message,
            details=details
        )
        self.test_results.append(result)
        
        # Print result
        if status == "PASS":
            self.success(f"{name} ({response_code}, {response_time:.2f}s)")
        elif status == "FAIL":
            self.error(f"{name} - {error_message}")
        else:
            self.warning(f"{name} - SKIPPED")
    
    def test_health_check(self):
        """Test health check endpoint"""
        try:
            response, response_time = self.make_request("GET", "/health")
            if response.status_code == 200:
                data = response.json()
                self.add_result("Health Check", "/health", "GET", "PASS", 
                              response.status_code, response_time,
                              details=f"Status: {data.get('status', 'unknown')}")
            else:
                self.add_result("Health Check", "/health", "GET", "FAIL",
                              response.status_code, response_time,
                              error_message=f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.add_result("Health Check", "/health", "GET", "FAIL",
                          error_message=str(e))
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        try:
            response, response_time = self.make_request("GET", "/")
            if response.status_code == 200:
                data = response.json()
                self.add_result("Root Endpoint", "/", "GET", "PASS",
                              response.status_code, response_time,
                              details=f"Version: {data.get('version', 'unknown')}")
            else:
                self.add_result("Root Endpoint", "/", "GET", "FAIL",
                              response.status_code, response_time,
                              error_message=f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.add_result("Root Endpoint", "/", "GET", "FAIL",
                          error_message=str(e))
    
    def test_authentication(self):
        """Test authentication endpoints"""
        # Test token endpoint
        try:
            data = {
                "username": "admin",
                "password": "admin123"
            }
            response, response_time = self.make_request(
                "POST", "/auth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.auth_token = token_data.get("access_token")
                self.add_result("Admin Login", "/auth/token", "POST", "PASS",
                              response.status_code, response_time,
                              details="Token obtained successfully")
            else:
                self.add_result("Admin Login", "/auth/token", "POST", "FAIL",
                              response.status_code, response_time,
                              error_message=f"Login failed: {response.text}")
        except Exception as e:
            self.add_result("Admin Login", "/auth/token", "POST", "FAIL",
                          error_message=str(e))
        
        # Test analyst login
        try:
            data = {
                "username": "analyst",
                "password": "analyst123"
            }
            response, response_time = self.make_request(
                "POST", "/auth/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data=data
            )
            
            if response.status_code == 200:
                self.add_result("Analyst Login", "/auth/token", "POST", "PASS",
                              response.status_code, response_time)
            else:
                self.add_result("Analyst Login", "/auth/token", "POST", "FAIL",
                              response.status_code, response_time,
                              error_message=f"Login failed: {response.text}")
        except Exception as e:
            self.add_result("Analyst Login", "/auth/token", "POST", "FAIL",
                          error_message=str(e))
        
        # Test current user endpoint
        if self.auth_token:
            try:
                response, response_time = self.make_request("GET", "/auth/me")
                if response.status_code == 200:
                    user_data = response.json()
                    self.add_result("Get Current User", "/auth/me", "GET", "PASS",
                                  response.status_code, response_time,
                                  details=f"User: {user_data.get('sub', 'unknown')}")
                else:
                    self.add_result("Get Current User", "/auth/me", "GET", "FAIL",
                                  response.status_code, response_time,
                                  error_message=f"Failed to get user info: {response.text}")
            except Exception as e:
                self.add_result("Get Current User", "/auth/me", "GET", "FAIL",
                              error_message=str(e))
    
    def test_sql_endpoints(self):
        """Test SQL generation endpoints"""
        if not self.auth_token:
            self.add_result("SQL Endpoints", "/api/sql", "POST", "SKIP",
                          error_message="No auth token available")
            return
        
        # Test cases for SQL generation
        test_cases = [
            {
                "name": "Simple Customer Query",
                "question": "Show me all customers from California"
            },
            {
                "name": "Sales Aggregation Query", 
                "question": "What are the total sales by region?"
            },
            {
                "name": "Top Customers Query",
                "question": "Who are the top 5 customers by sales?"
            },
            {
                "name": "Order Status Query",
                "question": "How many orders are pending delivery?"
            },
            {
                "name": "Product Category Query",
                "question": "What products are in the Electronics category?"
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {"question": test_case["question"]}
                response, response_time = self.make_request(
                    "POST", "/api/sql",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "sql" in data or "error" in data:
                        status = "PASS" if "sql" in data else "FAIL"
                        error_msg = data.get("error") if "error" in data else None
                        details = f"SQL generated: {len(data.get('sql', '')) > 0}" if "sql" in data else None
                        
                        self.add_result(test_case["name"], "/api/sql", "POST", status,
                                      response.status_code, response_time,
                                      error_message=error_msg, details=details)
                    else:
                        self.add_result(test_case["name"], "/api/sql", "POST", "FAIL",
                                      response.status_code, response_time,
                                      error_message="Unexpected response format")
                else:
                    self.add_result(test_case["name"], "/api/sql", "POST", "FAIL",
                                  response.status_code, response_time,
                                  error_message=f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.add_result(test_case["name"], "/api/sql", "POST", "FAIL",
                              error_message=str(e))
    
    def test_rag_endpoints(self):
        """Test RAG document endpoints"""
        if not self.auth_token:
            self.add_result("RAG Endpoints", "/api/rag/query", "POST", "SKIP",
                          error_message="No auth token available")
            return
        
        # Test RAG query
        test_cases = [
            {
                "name": "Policy Query",
                "question": "What is the anti-counterfeit policy?"
            },
            {
                "name": "Compliance Query",
                "question": "What are the requirements for supplier compliance?"
            },
            {
                "name": "Risk Management Query",
                "question": "How should we handle supply chain risks?"
            }
        ]
        
        for test_case in test_cases:
            try:
                payload = {"question": test_case["question"]}
                response, response_time = self.make_request(
                    "POST", "/api/rag/query",
                    headers={"Content-Type": "application/json"},
                    json=payload
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "answer" in data:
                        self.add_result(test_case["name"], "/api/rag/query", "POST", "PASS",
                                      response.status_code, response_time,
                                      details=f"Answer length: {len(data['answer'])}")
                    else:
                        self.add_result(test_case["name"], "/api/rag/query", "POST", "FAIL",
                                      response.status_code, response_time,
                                      error_message="No answer in response")
                else:
                    self.add_result(test_case["name"], "/api/rag/query", "POST", "FAIL",
                                  response.status_code, response_time,
                                  error_message=f"HTTP {response.status_code}: {response.text}")
            except Exception as e:
                self.add_result(test_case["name"], "/api/rag/query", "POST", "FAIL",
                              error_message=str(e))
        
        # Test document ingestion
        try:
            payload = {
                "document": "This is a test document for ingestion testing.",
                "metadata": {"source": "test", "type": "policy"}
            }
            response, response_time = self.make_request(
                "POST", "/api/rag/ingest",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 200:
                self.add_result("Document Ingestion", "/api/rag/ingest", "POST", "PASS",
                              response.status_code, response_time)
            else:
                self.add_result("Document Ingestion", "/api/rag/ingest", "POST", "FAIL",
                              response.status_code, response_time,
                              error_message=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.add_result("Document Ingestion", "/api/rag/ingest", "POST", "FAIL",
                          error_message=str(e))
    
    def test_admin_endpoints(self):
        """Test admin endpoints"""
        if not self.auth_token:
            self.add_result("Admin Endpoints", "/admin/users", "GET", "SKIP",
                          error_message="No auth token available")
            return
        
        try:
            response, response_time = self.make_request("GET", "/admin/users")
            if response.status_code == 200:
                users = response.json()
                self.add_result("List Users", "/admin/users", "GET", "PASS",
                              response.status_code, response_time,
                              details=f"Found {len(users)} users")
            else:
                self.add_result("List Users", "/admin/users", "GET", "FAIL",
                              response.status_code, response_time,
                              error_message=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.add_result("List Users", "/admin/users", "GET", "FAIL",
                          error_message=str(e))
    
    def test_user_registration(self):
        """Test user registration"""
        try:
            payload = {
                "username": f"testuser_{int(time.time())}",
                "email": f"test_{int(time.time())}@example.com",
                "password": "testpassword123",
                "full_name": "Test User",
                "region": "test_region"
            }
            response, response_time = self.make_request(
                "POST", "/auth/register",
                headers={"Content-Type": "application/json"},
                json=payload
            )
            
            if response.status_code == 201:
                self.add_result("User Registration", "/auth/register", "POST", "PASS",
                              response.status_code, response_time)
            else:
                self.add_result("User Registration", "/auth/register", "POST", "FAIL",
                              response.status_code, response_time,
                              error_message=f"HTTP {response.status_code}: {response.text}")
        except Exception as e:
            self.add_result("User Registration", "/auth/register", "POST", "FAIL",
                          error_message=str(e))
    
    def test_edge_cases(self):
        """Test edge cases and error handling"""
        # Test invalid endpoints
        try:
            response, response_time = self.make_request("GET", "/nonexistent")
            if response.status_code == 404:
                self.add_result("404 Handling", "/nonexistent", "GET", "PASS",
                              response.status_code, response_time)
            else:
                self.add_result("404 Handling", "/nonexistent", "GET", "FAIL",
                              response.status_code, response_time,
                              error_message=f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.add_result("404 Handling", "/nonexistent", "GET", "FAIL",
                          error_message=str(e))
        
        # Test malformed requests
        if self.auth_token:
            try:
                response, response_time = self.make_request(
                    "POST", "/api/sql",
                    headers={"Content-Type": "application/json"},
                    json={"invalid_field": "test"}
                )
                if response.status_code == 422 or response.status_code == 400:
                    self.add_result("Invalid Request Handling", "/api/sql", "POST", "PASS",
                                  response.status_code, response_time)
                else:
                    self.add_result("Invalid Request Handling", "/api/sql", "POST", "FAIL",
                                  response.status_code, response_time,
                                  error_message=f"Expected 400/422, got {response.status_code}")
            except Exception as e:
                self.add_result("Invalid Request Handling", "/api/sql", "POST", "FAIL",
                              error_message=str(e))
    
    def run_all_tests(self):
        """Run all test suites"""
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    🧪 API Test Suite                         ║
║                  SynGen AI Comprehensive Tests               ║
╚══════════════════════════════════════════════════════════════╝

🎯 Target: {self.base_url}
⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        # Test suites
        test_suites = [
            ("Basic Endpoints", [
                self.test_health_check,
                self.test_root_endpoint
            ]),
            ("Authentication", [
                self.test_authentication,
                self.test_user_registration
            ]),
            ("SQL Generation", [
                self.test_sql_endpoints
            ]),
            ("RAG System", [
                self.test_rag_endpoints
            ]),
            ("Admin Functions", [
                self.test_admin_endpoints
            ]),
            ("Edge Cases", [
                self.test_edge_cases
            ])
        ]
        
        for suite_name, tests in test_suites:
            self.log(f"Running {suite_name} Tests...", "PURPLE")
            for test_func in tests:
                try:
                    test_func()
                except Exception as e:
                    self.error(f"Test suite {suite_name} failed: {str(e)}")
            print()
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate test report"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r.status == "PASS"])
        failed = len([r for r in self.test_results if r.status == "FAIL"])
        skipped = len([r for r in self.test_results if r.status == "SKIP"])
        
        avg_response_time = sum(r.response_time for r in self.test_results if r.response_time) / max(1, len([r for r in self.test_results if r.response_time]))
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║                      📊 Test Report                          ║
╚══════════════════════════════════════════════════════════════╝

📈 Summary:
   Total Tests: {total}
   ✅ Passed: {passed} ({passed/total*100:.1f}%)
   ❌ Failed: {failed} ({failed/total*100:.1f}%)
   ⚠️  Skipped: {skipped} ({skipped/total*100:.1f}%)
   ⏱️  Avg Response: {avg_response_time:.2f}s

""")
        
        if failed > 0:
            print("❌ Failed Tests:")
            for result in self.test_results:
                if result.status == "FAIL":
                    print(f"   • {result.name}: {result.error_message}")
            print()
        
        if skipped > 0:
            print("⚠️  Skipped Tests:")
            for result in self.test_results:
                if result.status == "SKIP":
                    print(f"   • {result.name}: {result.error_message}")
            print()
        
        # Detailed results
        print("📋 Detailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result.status == "PASS" else "❌" if result.status == "FAIL" else "⚠️"
            time_str = f"{result.response_time:.2f}s" if result.response_time else "N/A"
            code_str = str(result.response_code) if result.response_code else "N/A"
            print(f"   {status_icon} {result.name:<30} {result.method:<6} {code_str:<4} {time_str}")
        
        # Save results to file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_file = f"/tmp/syngen_test_results_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump([{
                'name': r.name,
                'endpoint': r.endpoint,
                'method': r.method,
                'status': r.status,
                'response_code': r.response_code,
                'response_time': r.response_time,
                'error_message': r.error_message,
                'details': r.details
            } for r in self.test_results], f, indent=2)
        
        print(f"\n💾 Results saved to: {results_file}")
        
        # Return exit code based on results
        return 0 if failed == 0 else 1

def main():
    """Main function"""
    # Check if API is running
    try:
        response = requests.get(f"{API_BASE_URL}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ API not responding correctly at {API_BASE_URL}")
            sys.exit(1)
    except requests.exceptions.RequestException:
        print(f"❌ API not accessible at {API_BASE_URL}")
        print("💡 Make sure the API server is running: ./full_app_run.sh")
        sys.exit(1)
    
    # Run tests
    tester = APITester(API_BASE_URL)
    exit_code = tester.run_all_tests()
    
    sys.exit(exit_code)

if __name__ == "__main__":
    main()