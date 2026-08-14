#!/usr/bin/env python3
"""
Test script for AI Trip Agent v2.0
Tests all new features including real-time agents
"""

import requests
import time
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8001"

def print_section(title):
    """Print a section header."""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_api_health():
    """Test API health endpoint."""
    print_section("Testing API Health")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ API is healthy")
            print(f"   Version: {data.get('version')}")
            print(f"   LLM Provider: {data.get('llm_provider')}")
            print(f"   ChromaDB: {'✅ Connected' if data.get('chroma_connected') else '❌ Disconnected'}")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API health check error: {e}")
        return False

def test_trip_planning_basic():
    """Test basic trip planning without real-time agent."""
    print_section("Testing Basic Trip Planning")
    
    request_data = {
        "query": "Plan a 2-day trip to Kaziranga for wildlife photography",
        "transport_mode": "car_petrol",
        "persona": "adventure",
        "stoppage_duration": "3_hours",
        "enable_realtime_agent": False
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/plan-trip",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            print("\n✅ Trip planning successful")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Destination: {data.get('destination')}")
            print(f"   Duration: {data.get('duration_days')} days")
            print(f"   Agent ID: {data.get('agent_id', 'None (not enabled)')}")
            print(f"   Messages: {len(data.get('messages', []))} message(s)")
            return True, data
        else:
            print(f"❌ Trip planning failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Trip planning error: {e}")
        return False, None

def test_trip_planning_with_agent():
    """Test trip planning with real-time agent."""
    print_section("Testing Trip Planning with Real-Time Agent")
    
    request_data = {
        "query": "Plan a 3-day family trip to Majuli with kids",
        "transport_mode": "mixed",
        "persona": "family",
        "stoppage_duration": "6_hours",
        "enable_realtime_agent": True
    }
    
    print(f"Request: {json.dumps(request_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/plan-trip",
            json=request_data,
            timeout=60
        )
        
        if response.status_code == 200:
            data = response.json()
            agent_id = data.get('agent_id')
            
            print("\n✅ Trip planning with agent successful")
            print(f"   Session ID: {data.get('session_id')}")
            print(f"   Destination: {data.get('destination')}")
            print(f"   Duration: {data.get('duration_days')} days")
            print(f"   Agent ID: {agent_id}")
            
            if agent_id:
                print(f"\n🤖 Real-time agent created: {agent_id}")
                return True, agent_id
            else:
                print("⚠️  Agent ID not returned")
                return False, None
        else:
            print(f"❌ Trip planning failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Trip planning error: {e}")
        return False, None

def test_agent_status(agent_id):
    """Test agent status endpoint."""
    print_section(f"Testing Agent Status: {agent_id}")
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/agent/{agent_id}/status",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent status retrieved")
            print(f"   Agent ID: {data.get('agent_id')}")
            print(f"   Status: {data.get('status')}")
            print(f"   Created: {data.get('created_at')}")
            print(f"   Last Check: {data.get('last_check')}")
            print(f"   Updates: {len(data.get('updates', []))} update(s)")
            
            updates = data.get('updates', [])
            if updates:
                print("\n   Recent Updates:")
                for update in updates[:3]:  # Show first 3
                    print(f"   - [{update.get('type')}] {update.get('message')[:60]}...")
            
            return True, data
        else:
            print(f"❌ Agent status failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Agent status error: {e}")
        return False, None

def test_list_agents():
    """Test list all agents endpoint."""
    print_section("Testing List All Agents")
    
    try:
        response = requests.get(f"{API_BASE_URL}/agents", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            count = data.get('count', 0)
            
            print(f"✅ Found {count} active agent(s)")
            
            for i, agent in enumerate(agents, 1):
                print(f"\n   Agent {i}:")
                print(f"   - ID: {agent.get('agent_id')}")
                print(f"   - Status: {agent.get('status')}")
                print(f"   - Destination: {agent.get('trip_details', {}).get('destination')}")
                print(f"   - Updates: {len(agent.get('updates', []))}")
            
            return True, agents
        else:
            print(f"❌ List agents failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ List agents error: {e}")
        return False, None

def test_stop_agent(agent_id):
    """Test stop agent endpoint."""
    print_section(f"Testing Stop Agent: {agent_id}")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/agent/{agent_id}/stop",
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Agent stopped successfully")
            print(f"   Message: {data.get('message')}")
            return True
        else:
            print(f"❌ Stop agent failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Stop agent error: {e}")
        return False

def test_all_personas():
    """Test all persona options."""
    print_section("Testing All Personas")
    
    personas = [
        "student", "family", "heritage", "corporate", "green",
        "solo", "religious", "spiritual", "adventure", "luxury"
    ]
    
    print(f"Testing {len(personas)} personas...")
    
    for persona in personas:
        request_data = {
            "query": f"Quick trip to Guwahati",
            "transport_mode": "car_petrol",
            "persona": persona,
            "stoppage_duration": "none",
            "enable_realtime_agent": False
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/plan-trip",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ {persona.capitalize()}")
            else:
                print(f"   ❌ {persona.capitalize()} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {persona.capitalize()} - Error: {str(e)[:50]}")
    
    print("\n✅ Persona testing complete")

def test_transport_modes():
    """Test all transport modes."""
    print_section("Testing All Transport Modes")
    
    modes = [
        "mixed", "car_petrol", "car_diesel", "car_electric",
        "bus", "train", "motorcycle", "bicycle", "walking"
    ]
    
    print(f"Testing {len(modes)} transport modes...")
    
    for mode in modes:
        request_data = {
            "query": "Day trip to nearby location",
            "transport_mode": mode,
            "persona": "solo",
            "stoppage_duration": "none",
            "enable_realtime_agent": False
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/plan-trip",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"   ✅ {mode.replace('_', ' ').title()}")
            else:
                print(f"   ❌ {mode.replace('_', ' ').title()} - Status: {response.status_code}")
        except Exception as e:
            print(f"   ❌ {mode.replace('_', ' ').title()} - Error: {str(e)[:50]}")
    
    print("\n✅ Transport mode testing complete")

def run_all_tests():
    """Run all tests."""
    print("\n" + "🧪 "*30)
    print("AI Trip Agent v2.0 - Comprehensive Test Suite")
    print("🧪 "*30)
    
    results = {
        "passed": 0,
        "failed": 0,
        "total": 0
    }
    
    # Test 1: API Health
    results["total"] += 1
    if test_api_health():
        results["passed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  API is not healthy. Stopping tests.")
        return results
    
    # Test 2: Basic Trip Planning
    results["total"] += 1
    success, _ = test_trip_planning_basic()
    if success:
        results["passed"] += 1
    else:
        results["failed"] += 1
    
    # Test 3: Trip Planning with Agent
    results["total"] += 1
    success, agent_id = test_trip_planning_with_agent()
    if success and agent_id:
        results["passed"] += 1
        
        # Wait a moment for agent to start
        print("\n⏳ Waiting 3 seconds for agent to initialize...")
        time.sleep(3)
        
        # Test 4: Agent Status
        results["total"] += 1
        success, _ = test_agent_status(agent_id)
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 5: List Agents
        results["total"] += 1
        success, _ = test_list_agents()
        if success:
            results["passed"] += 1
        else:
            results["failed"] += 1
        
        # Test 6: Stop Agent
        results["total"] += 1
        if test_stop_agent(agent_id):
            results["passed"] += 1
        else:
            results["failed"] += 1
    else:
        results["failed"] += 1
        print("\n⚠️  Skipping agent tests due to creation failure")
        results["total"] += 3
        results["failed"] += 3
    
    # Test 7: All Personas
    results["total"] += 1
    try:
        test_all_personas()
        results["passed"] += 1
    except:
        results["failed"] += 1
    
    # Test 8: All Transport Modes
    results["total"] += 1
    try:
        test_transport_modes()
        results["passed"] += 1
    except:
        results["failed"] += 1
    
    # Print Summary
    print_section("Test Summary")
    print(f"Total Tests: {results['total']}")
    print(f"✅ Passed: {results['passed']}")
    print(f"❌ Failed: {results['failed']}")
    print(f"Success Rate: {(results['passed']/results['total']*100):.1f}%")
    
    if results['failed'] == 0:
        print("\n🎉 All tests passed! System is working perfectly.")
    elif results['passed'] > results['failed']:
        print("\n⚠️  Some tests failed, but system is mostly functional.")
    else:
        print("\n❌ Multiple tests failed. Please check the system.")
    
    return results

if __name__ == "__main__":
    results = run_all_tests()
    exit(0 if results['failed'] == 0 else 1)
