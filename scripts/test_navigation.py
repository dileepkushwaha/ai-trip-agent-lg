#!/usr/bin/env python3
"""
Test script to verify file paths and navigation for Streamlit pages
"""

import os
import sys
from pathlib import Path

def test_file_paths():
    """Test file paths and navigation."""
    print("🔍 Testing File Paths and Navigation")
    print("=" * 50)
    
    # Get current working directory
    cwd = os.getcwd()
    print(f"Current directory: {cwd}")
    
    # Check if we're in the right directory
    expected_files = [
        "ui/streamlit_app.py",
        "pages/1_📊_Observability.py"
    ]
    
    print("\n📁 Checking file locations:")
    for file_path in expected_files:
        full_path = os.path.join(cwd, file_path)
        exists = os.path.exists(full_path)
        print(f"  {'✅' if exists else '❌'} {file_path}")
        if not exists:
            print(f"     Full path: {full_path}")
    
    # Test relative paths from UI directory
    ui_dir = os.path.join(cwd, "ui")
    if os.path.exists(ui_dir):
        print(f"\n📂 Checking paths from UI directory ({ui_dir}):")
        os.chdir(ui_dir)
        
        # Test navigation to observability page
        obs_path_options = [
            "../pages/1_📊_Observability.py",
            "pages/1_📊_Observability.py"
        ]
        
        for path in obs_path_options:
            exists = os.path.exists(path)
            print(f"  {'✅' if exists else '❌'} {path}")
        
        # Test navigation back to main app
        main_app_options = [
            "../ui/streamlit_app.py",
            "streamlit_app.py"
        ]
        
        print(f"\n🏠 Checking navigation back to main app:")
        for path in main_app_options:
            exists = os.path.exists(path)
            print(f"  {'✅' if exists else '❌'} {path}")
        
        # Go back to original directory
        os.chdir(cwd)
    
    print("\n📋 File structure:")
    print("   ai-trip-agent/")
    print("   ├── ui/")
    print("   │   └── streamlit_app.py")
    print("   └── pages/")
    print("       └── 1_📊_Observability.py")
    
    return True

def test_streamlit_navigation():
    """Test Streamlit navigation recommendations."""
    print("\n🧭 Streamlit Navigation Test")
    print("=" * 50)
    
    print("To test navigation in Streamlit:")
    print("1. Start Streamlit from the project root:")
    print("   streamlit run ui/streamlit_app.py")
    print()
    print("2. Navigation should work with these paths:")
    print("   - Main app -> Observability: '../pages/1_📊_Observability.py'")
    print("   - Observability -> Main app: '../ui/streamlit_app.py'")
    print()
    print("3. Alternative paths (if started from different locations):")
    print("   - Main app -> Observability: 'pages/1_📊_Observability.py'")
    print("   - Observability -> Main app: 'ui/streamlit_app.py'")
    
    return True

def main():
    """Run all tests."""
    print("🚀 AI Trip Agent - Navigation Path Test")
    print("=" * 60)
    
    success = True
    success &= test_file_paths()
    success &= test_streamlit_navigation()
    
    if success:
        print("\n✅ All path tests completed!")
        print("\n📋 Next Steps:")
        print("   1. Start the API: uvicorn services.api.main:app --port 8001")
        print("   2. Start Streamlit: streamlit run ui/streamlit_app.py")
        print("   3. Click the '📊 Observability' button")
        print("   4. Verify the dashboard loads correctly")
        print("   5. Use the '🏠 Back to Main App' button to return")
    else:
        print("\n❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()