"""
Comprehensive Test Suite for Chatterbox Chat Application
Tests all endpoints, WebSocket functionality, and edge cases
"""

import requests
import asyncio
import websockets
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/ws"

# Test colors
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name, passed, message=""):
    """Print test result"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"{status} - {name}")
    if message:
        print(f"     {message}")

def print_section(title):
    """Print section header"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"{title}")
    print(f"{'='*60}{Colors.END}\n")

# ============================================
# HTTP ENDPOINT TESTS
# ============================================

def test_health_check():
    """Test server health check"""
    print_section("TEST: Health Check")
    try:
        response = requests.get(f"{BASE_URL}/")
        data = response.json()
        passed = response.status_code == 200 and "status" in data
        print_test("Health Check", passed, f"Response: {data}")
        return passed
    except Exception as e:
        print_test("Health Check", False, f"Error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print_section("TEST: User Registration")
    
    # Test 1: Successful registration
    username = f"testuser_{int(time.time())}"
    password = "testpass123"
    
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        passed = response.status_code == 200
        print_test("Register new user", passed, f"User: {username}")
    except Exception as e:
        print_test("Register new user", False, f"Error: {e}")
        passed = False
    
    # Test 2: Duplicate registration
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": username, "password": password}
        )
        passed2 = response.status_code == 400
        print_test("Reject duplicate user", passed2, "Correctly rejected")
    except Exception as e:
        print_test("Reject duplicate user", False, f"Error: {e}")
        passed2 = False
    
    # Test 3: Short username
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": "ab", "password": "testpass123"}
        )
        passed3 = response.status_code == 400
        print_test("Reject short username", passed3, "Correctly rejected username < 3 chars")
    except Exception as e:
        print_test("Reject short username", False, f"Error: {e}")
        passed3 = False
    
    # Test 4: Short password
    try:
        response = requests.post(
            f"{BASE_URL}/register",
            json={"username": "validuser", "password": "12345"}
        )
        passed4 = response.status_code == 400
        print_test("Reject short password", passed4, "Correctly rejected password < 6 chars")
    except Exception as e:
        print_test("Reject short password", False, f"Error: {e}")
        passed4 = False
    
    return passed and passed2 and passed3 and passed4, username, password

def test_login(username, password):
    """Test user login"""
    print_section("TEST: User Login")
    
    # Test 1: Successful login
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": password}
        )
        data = response.json()
        token = data.get("token")
        passed = response.status_code == 200 and token is not None
        print_test("Login with valid credentials", passed, f"Token: {token[:20]}...")
    except Exception as e:
        print_test("Login with valid credentials", False, f"Error: {e}")
        return False, None
    
    # Test 2: Invalid password
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": username, "password": "wrongpassword"}
        )
        passed2 = response.status_code == 401
        print_test("Reject invalid password", passed2, "Correctly rejected")
    except Exception as e:
        print_test("Reject invalid password", False, f"Error: {e}")
        passed2 = False
    
    # Test 3: Non-existent user
    try:
        response = requests.post(
            f"{BASE_URL}/login",
            json={"username": "nonexistentuser999", "password": "password"}
        )
        passed3 = response.status_code == 401
        print_test("Reject non-existent user", passed3, "Correctly rejected")
    except Exception as e:
        print_test("Reject non-existent user", False, f"Error: {e}")
        passed3 = False
    
    return passed and passed2 and passed3, token

def test_stats():
    """Test stats endpoint"""
    print_section("TEST: Statistics Endpoint")
    try:
        response = requests.get(f"{BASE_URL}/stats")
        data = response.json()
        required_keys = ["total_users", "total_messages", "active_connections", "active_sessions"]
        passed = all(key in data for key in required_keys)
        print_test("Get statistics", passed, f"Stats: {data}")
        return passed
    except Exception as e:
        print_test("Get statistics", False, f"Error: {e}")
        return False

# ============================================
# WEBSOCKET TESTS
# ============================================

async def test_websocket_connection(token):
    """Test WebSocket connection"""
    print_section("TEST: WebSocket Connection")
    
    # Test 1: Valid token
    try:
        uri = f"{WS_URL}?token={token}"
        async with websockets.connect(uri) as ws:
            # Wait for history message
            message = await ws.recv()
            data = json.loads(message)
            passed = data.get("type") == "history"
            print_test("Connect with valid token", passed, "Received chat history")
    except Exception as e:
        print_test("Connect with valid token", False, f"Error: {e}")
        return False
    
    # Test 2: Invalid token
    try:
        uri = f"{WS_URL}?token=invalid-token-12345"
        async with websockets.connect(uri) as ws:
            await ws.recv()
        print_test("Reject invalid token", False, "Should have rejected connection")
        passed2 = False
    except websockets.exceptions.ConnectionClosedError:
        # Server closed connection after accepting - still a rejection
        print_test("Reject invalid token", True, "Correctly rejected (connection closed)")
        passed2 = True
    except websockets.exceptions.InvalidStatus as e:
        # Server rejected before connection - HTTP 403 = correct behavior
        if "403" in str(e):
            print_test("Reject invalid token", True, "Correctly rejected (HTTP 403 Forbidden)")
            passed2 = True
        else:
            print_test("Reject invalid token", False, f"Unexpected status: {e}")
            passed2 = False
    except Exception as e:
        print_test("Reject invalid token", False, f"Unexpected error: {e}")
        passed2 = False
    
    return passed and passed2

async def test_message_sending(token):
    """Test sending and receiving messages"""
    print_section("TEST: Message Sending & Broadcasting")
    
    try:
        uri = f"{WS_URL}?token={token}"
        async with websockets.connect(uri) as ws:
            # Receive history
            await ws.recv()
            
            # Send a test message
            test_content = f"Test message at {datetime.now().isoformat()}"
            await ws.send(json.dumps({"content": test_content}))
            
            # Receive the broadcast
            message = await asyncio.wait_for(ws.recv(), timeout=5.0)
            data = json.loads(message)
            
            passed = (
                data.get("type") == "message" and
                data.get("content") == test_content and
                "username" in data and
                "timestamp" in data
            )
            print_test("Send and receive message", passed, f"Content: {test_content}")
            
            # Test empty message
            await ws.send(json.dumps({"content": ""}))
            error_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            error_data = json.loads(error_msg)
            passed2 = error_data.get("type") == "error"
            print_test("Reject empty message", passed2, "Correctly rejected")
            
            # Test very long message
            long_content = "A" * 6000
            await ws.send(json.dumps({"content": long_content}))
            error_msg = await asyncio.wait_for(ws.recv(), timeout=5.0)
            error_data = json.loads(error_msg)
            passed3 = error_data.get("type") == "error"
            print_test("Reject too long message", passed3, "Correctly rejected (>5000 chars)")
            
            return passed and passed2 and passed3
            
    except asyncio.TimeoutError:
        print_test("Message sending", False, "Timeout waiting for response")
        return False
    except Exception as e:
        print_test("Message sending", False, f"Error: {e}")
        return False

async def test_concurrent_connections(token1, token2):
    """Test multiple concurrent connections"""
    print_section("TEST: Concurrent Connections")
    
    try:
        uri1 = f"{WS_URL}?token={token1}"
        uri2 = f"{WS_URL}?token={token2}"
        
        async with websockets.connect(uri1) as ws1, websockets.connect(uri2) as ws2:
            # Clear histories
            await ws1.recv()
            await ws2.recv()
            
            # Send from ws1
            test_content = "Message from user 1"
            await ws1.send(json.dumps({"content": test_content}))
            
            # Both should receive
            msg1 = await asyncio.wait_for(ws1.recv(), timeout=5.0)
            msg2 = await asyncio.wait_for(ws2.recv(), timeout=5.0)
            
            data1 = json.loads(msg1)
            data2 = json.loads(msg2)
            
            passed = (
                data1.get("content") == test_content and
                data2.get("content") == test_content
            )
            print_test("Broadcast to multiple clients", passed, "Both clients received message")
            return passed
            
    except Exception as e:
        print_test("Concurrent connections", False, f"Error: {e}")
        return False

# ============================================
# MAIN TEST RUNNER
# ============================================

async def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.YELLOW}")
    print("=" * 60)
    print("  CHATTERBOX - COMPREHENSIVE TEST SUITE")
    print("=" * 60)
    print(f"{Colors.END}")
    
    results = {
        "passed": 0,
        "failed": 0
    }
    
    # HTTP Tests
    if test_health_check():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    reg_result, username, password = test_registration()
    if reg_result:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    login_result, token = test_login(username, password)
    if login_result:
        results["passed"] += 1
    else:
        results["failed"] += 1
        print(f"\n{Colors.RED}Cannot continue WebSocket tests without valid token{Colors.END}")
        return
    
    if test_stats():
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # WebSocket Tests
    if await test_websocket_connection(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    if await test_message_sending(token):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Create second user for concurrent test
    username2 = f"testuser2_{int(time.time())}"
    requests.post(f"{BASE_URL}/register", json={"username": username2, "password": "testpass123"})
    resp = requests.post(f"{BASE_URL}/login", json={"username": username2, "password": "testpass123"})
    token2 = resp.json().get("token")
    
    if await test_concurrent_connections(token, token2):
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Print summary
    print_section("TEST SUMMARY")
    total = results["passed"] + results["failed"]
    percentage = (results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"{Colors.GREEN}Passed: {results['passed']}{Colors.END}")
    print(f"{Colors.RED}Failed: {results['failed']}{Colors.END}")
    print(f"Success Rate: {percentage:.1f}%\n")
    
    if results["failed"] == 0:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! 🎉{Colors.END}\n")
    else:
        print(f"{Colors.RED}⚠️  SOME TESTS FAILED ⚠️{Colors.END}\n")

if __name__ == "__main__":
    print("\nMake sure the server is running on http://127.0.0.1:8000\n")
    try:
        asyncio.run(run_all_tests())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n{Colors.RED}Test suite error: {e}{Colors.END}")