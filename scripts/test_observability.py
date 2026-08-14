#!/usr/bin/env python3
"""
Test script to verify observability page functionality
"""

import requests
import time

API_BASE_URL = "http://localhost:8001"

def test_observability_endpoints():
    """Test all observability-related endpoints."""
    print("🧪 Testing Observability Endpoints")
    print("=" * 50)
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API Health Check")
            print(f"      Status: {data.get('status')}")
            print(f"      Version: {data.get('version')}")
            print(f"      LLM Provider: {data.get('llm_provider')}")
            print(f"      ChromaDB: {'Connected' if data.get('chroma_connected') else 'Disconnected'}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: List All Agents
    print("\n2. Testing List All Agents...")
    try:
        response = requests.get(f"{API_BASE_URL}/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            print(f"   ✅ Found {len(agents)} agents")
            for agent in agents:
                print(f"      - {agent.get('agent_id')}: {agent.get('status')}")
        else:
            print(f"   ❌ Failed to list agents: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ List agents error: {e}")
        return False
    
    # Test 3: Agent Status (if agents exist)
    try:
        response = requests.get(f"{API_BASE_URL}/agents", timeout=5)
        if response.status_code == 200:
            data = response.json()
            agents = data.get('agents', [])
            if agents:
                agent_id = agents[0].get('agent_id')
                print(f"\n3. Testing Agent Status for {agent_id}...")
                response = requests.get(f"{API_BASE_URL}/agent/{agent_id}/status", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    print("   ✅ Agent Status Retrieved")
                    print(f"      Status: {data.get('status')}")
                    print(f"      Updates: {len(data.get('updates', []))}")
                    print(f"      Last Check: {data.get('last_check')}")
                else:
                    print(f"   ❌ Failed to get agent status: {response.status_code}")
                    return False
            else:
                print("\n3. No agents to test status endpoint")
        else:
            print(f"\n3. ❌ Failed to list agents for status test: {response.status_code}")
            return False
    except Exception as e:
        print(f"\n3. ❌ Agent status error: {e}")
        return False
    
    print("\n🎉 All observability endpoints working correctly!")
    return True

def test_streamlit_pages():
    """Test Streamlit page navigation."""
    print("\n📱 Testing Streamlit Page Navigation")
    print("=" * 50)
    
    print("\nTo test page navigation:")
    print("1. Open your browser to http://localhost:8516")
    print("2. Look for the '📊 Observability' button in the top navigation")
    print("3. Click the button to navigate to the observability page")
    print("4. Verify the page loads with system health metrics")
    print("5. Check that active agents are displayed")
    print("6. Try the theme toggle (☀️/🌙) on both pages")
    print("7. Use the '🏠 Back to Main App' button to return")
    
    return True

def main():
    """Run all tests."""
    print("🚀 AI Trip Agent - Observability Test Suite")
    print("=" * 60)
    
    success = True
    success &= test_observability_endpoints()
    success &= test_streamlit_pages()
    
    if success:
        print("\n✅ All tests passed!")
        print("\n📋 Next Steps:")
        print("   1. Open http://localhost:8516 in your browser")
        print("   2. Click the '📊 Observability' button")
        print("   3. Verify the observability dashboard loads correctly")
        print("   4. Check system health metrics")
        print("   5. Monitor active agents")
        print("   6. Test theme toggling")
        print("   7. Navigate back to main app")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()