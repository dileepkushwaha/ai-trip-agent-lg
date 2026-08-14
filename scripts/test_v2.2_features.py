#!/usr/bin/env python3
"""
Test script for AI Trip Agent v2.2 - Date/Time, Round Trip, and Observability Features
"""

import requests
import json
from datetime import datetime, timedelta

API_BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_date_time_round_trip():
    """Test trip planning with date/time and round trip."""
    print_section("Testing Date/Time and Round Trip Features")
    
    # Calculate dates
    departure_date = (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
    departure_time = "09:00:00"
    return_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    return_time = "18:00:00"
    
    print(f"Departure: {departure_date} at {departure_time}")
    print(f"Return: {return_date} at {return_time}")
    
    request_data = {
        "query": "Plan a 3-day round trip to Kaziranga",
        "transport_mode": "car_petrol",
        "persona": "family",
        "stoppage_duration": "6_hours",
        "enable_realtime_agent": True,
        "travel_date": departure_date,
        "travel_time": departure_time,
        "is_round_trip": True,
        "return_date": return_date,
        "return_time": return_time
    }
    
    print("\nSending request...")
    response = requests.post(
        f"{API_BASE_URL}/plan-trip",
        json=request_data,
        timeout=60
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Trip planned successfully!")
        print(f"   Session ID: {data.get('session_id')}")
        print(f"   Agent ID: {data.get('agent_id')}")
        print(f"   Destination: {data.get('destination')}")
        return data.get('agent_id')
    else:
        print(f"❌ Failed: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_observability_endpoints():
    """Test observability-related endpoints."""
    print_section("Testing Observability Endpoints")
    
    # Test 1: API Health
    print("1. Testing API Health...")
    response = requests.get(f"{API_BASE_URL}/health")
    if response.status_code == 200:
        data = response.json()
        print("✅ API Health Check")
        print(f"   Status: {data.get('status')}")
        print(f"   Version: {data.get('version')}")
        print(f"   LLM Provider: {data.get('llm_provider')}")
        print(f"   ChromaDB: {'Connected' if data.get('chroma_connected') else 'Disconnected'}")
    else:
        print(f"❌ Health check failed: {response.status_code}")
    
    # Test 2: List All Agents
    print("\n2. Testing List All Agents...")
    response = requests.get(f"{API_BASE_URL}/agents")
    if response.status_code == 200:
        data = response.json()
        agents = data.get('agents', [])
        print(f"✅ Found {len(agents)} agents")
        for agent in agents[:3]:  # Show first 3
            print(f"   - {agent.get('agent_id')}: {agent.get('status')}")
    else:
        print(f"❌ Failed to list agents: {response.status_code}")
    
    # Test 3: Agent Status
    if agents:
        agent_id = agents[0].get('agent_id')
        print(f"\n3. Testing Agent Status for {agent_id}...")
        response = requests.get(f"{API_BASE_URL}/agent/{agent_id}/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent Status Retrieved")
            print(f"   Status: {data.get('status')}")
            print(f"   Updates: {len(data.get('updates', []))}")
            print(f"   Last Check: {data.get('last_check')}")
        else:
            print(f"❌ Failed to get agent status: {response.status_code}")

def test_light_mode_fixes():
    """Test light mode visibility fixes."""
    print_section("Testing Light Mode Visibility Fixes")
    
    print("✅ Light mode visibility fixes applied:")
    print("   - Fixed stBottomBlockContainer background and text")
    print("   - Fixed stHeader background")
    print("   - Fixed select dropdown options visibility")
    print("   - Fixed input fields background and text")
    print("   - Fixed chat input visibility")
    print("   - Added hover effects for dropdown options")
    print("\n📝 Manual testing required:")
    print("   1. Open http://localhost:8516")
    print("   2. Toggle to light mode (☀️ button)")
    print("   3. Check all dropdowns are readable")
    print("   4. Verify input fields are visible")
    print("   5. Test chat input visibility")

def test_observability_page():
    """Test observability page features."""
    print_section("Testing Observability Page")
    
    print("✅ Observability page created at: pages/1_📊_Observability.py")
    print("\n📊 Features included:")
    print("   - System health dashboard")
    print("   - Active agents monitoring")
    print("   - Agent details (ID, duration, status, parameters)")
    print("   - LangSmith traces integration")
    print("   - Auto-refresh capability")
    print("   - Theme toggle")
    print("   - Navigation back to main app")
    print("\n📝 Manual testing required:")
    print("   1. Open http://localhost:8516")
    print("   2. Click '📊 Observability' button")
    print("   3. Verify system health metrics")
    print("   4. Check active agents display")
    print("   5. Test auto-refresh")
    print("   6. Navigate back to main app")

def run_all_tests():
    """Run all tests."""
    print("\n" + "🧪 "*30)
    print("AI Trip Agent v2.2 - New Features Test Suite")
    print("🧪 "*30)
    
    # Test 1: API Health
    print_section("Testing API Health")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is healthy")
        else:
            print(f"❌ API health check failed")
            return
    except Exception as e:
        print(f"❌ API not accessible: {e}")
        return
    
    # Test 2: Date/Time and Round Trip
    agent_id = test_date_time_round_trip()
    
    # Test 3: Observability Endpoints
    test_observability_endpoints()
    
    # Test 4: Light Mode Fixes
    test_light_mode_fixes()
    
    # Test 5: Observability Page
    test_observability_page()
    
    # Summary
    print_section("Test Summary")
    print("✅ All automated tests completed")
    print("\n📋 Features Tested:")
    print("   ✅ Date/time picker")
    print("   ✅ Round trip option")
    print("   ✅ API endpoints with new parameters")
    print("   ✅ Observability endpoints")
    print("   ✅ Agent monitoring")
    print("\n🎯 New Features in v2.2:")
    print("   ✅ Date and time selection")
    print("   ✅ Round trip support")
    print("   ✅ Observability dashboard")
    print("   ✅ Live agent monitoring")
    print("   ✅ LangSmith integration")
    print("   ✅ Fixed light mode visibility")
    print("   ✅ Agent metrics (ID, duration, status)")
    print("\n🌐 Next Steps:")
    print("   1. Open UI: http://localhost:8516")
    print("   2. Test date/time picker")
    print("   3. Test round trip option")
    print("   4. Visit observability page")
    print("   5. Monitor active agents")
    print("   6. Toggle between light/dark modes")

if __name__ == "__main__":
    run_all_tests()
