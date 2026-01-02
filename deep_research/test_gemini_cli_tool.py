#!/usr/bin/env python3
"""
Test script for Gemini CLI LangChain Tool

This script tests the ask_gemini_cli_tool to verify it works correctly
both as a standalone tool and in the agent context.
"""

import os
import sys
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv(".env", override=True)

from research_agent.gemini_cli_tool import ask_gemini_cli_tool

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def test_simple_query():
    """Test 1: Simple query to verify basic functionality"""
    print_section("TEST 1: Simple Query")
    
    query = "What is the capital of France?"
    print(f"\nQuery: {query}")
    print("\nCalling tool...")
    
    try:
        result = ask_gemini_cli_tool.invoke({"query": query})
        print(f"\n✅ SUCCESS")
        print(f"\nResponse:\n{result}")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

def test_financial_query():
    """Test 2: Financial domain query"""
    print_section("TEST 2: Financial Query")
    
    query = "What are the key financial ratios investors should look at when analyzing a company?"
    print(f"\nQuery: {query}")
    print("\nCalling tool...")
    
    try:
        result = ask_gemini_cli_tool.invoke({"query": query})
        print(f"\n✅ SUCCESS")
        print(f"\nResponse (first 500 chars):\n{result[:500]}...")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

def test_verification_query():
    """Test 3: Verification use case"""
    print_section("TEST 3: Verification Use Case")
    
    query = "Verify this calculation: If a company has revenue of $100M and net income of $15M, what is the profit margin?"
    print(f"\nQuery: {query}")
    print("\nCalling tool...")
    
    try:
        result = ask_gemini_cli_tool.invoke({"query": query})
        print(f"\n✅ SUCCESS")
        print(f"\nResponse:\n{result}")
        return True
    except Exception as e:
        print(f"\n❌ FAILED: {str(e)}")
        return False

def test_tool_metadata():
    """Test 4: Verify tool has proper metadata for LangChain"""
    print_section("TEST 4: Tool Metadata")
    
    print(f"\nTool Name: {ask_gemini_cli_tool.name}")
    print(f"\nTool Description:\n{ask_gemini_cli_tool.description}")
    print(f"\nTool Args Schema: {ask_gemini_cli_tool.args_schema}")
    
    # Verify the tool has the required attributes
    assert hasattr(ask_gemini_cli_tool, 'name'), "Tool missing 'name' attribute"
    assert hasattr(ask_gemini_cli_tool, 'description'), "Tool missing 'description' attribute"
    assert ask_gemini_cli_tool.description, "Tool description is empty"
    
    print(f"\n✅ Tool metadata is properly configured")
    return True

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*78 + "╗")
    print("║" + " "*20 + "GEMINI CLI TOOL TEST SUITE" + " "*32 + "║")
    print("╚" + "="*78 + "╝")
    
    tests = [
        test_tool_metadata,
        test_simple_query,
        test_financial_query,
        test_verification_query,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)}")
            results.append(False)
    
    # Summary
    print_section("TEST SUMMARY")
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Passed: {passed}/{total}")
    print(f"❌ Failed: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
