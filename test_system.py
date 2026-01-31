#!/usr/bin/env python3
"""
Comprehensive test script for Sarthi system
Tests all components: API endpoints, agents, database, vector store
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_api_endpoints():
    """Test all API endpoints"""
    print("🧪 Testing API endpoints...")

    async with aiohttp.ClientSession() as session:
        results = {}

        # Test root endpoint
        try:
            async with session.get(f"{BASE_URL}/") as response:
                results["root"] = response.status == 200
                print(f"✅ Root endpoint: {'PASS' if results['root'] else 'FAIL'}")
        except Exception as e:
            results["root"] = False
            print(f"❌ Root endpoint: FAIL - {e}")

        # Test settings endpoint
        try:
            async with session.get(f"{BASE_URL}/api/settings") as response:
                results["settings_get"] = response.status == 200
                print(f"✅ Settings GET: {'PASS' if results['settings_get'] else 'FAIL'}")
        except Exception as e:
            results["settings_get"] = False
            print(f"❌ Settings GET: FAIL - {e}")

        # Test agents endpoint
        try:
            async with session.get(f"{BASE_URL}/api/agents") as response:
                results["agents"] = response.status == 200
                if results["agents"]:
                    data = await response.json()
                    results["agents_count"] = len(data)
                print(f"✅ Agents endpoint: {'PASS' if results['agents'] else 'FAIL'}")
        except Exception as e:
            results["agents"] = False
            print(f"❌ Agents endpoint: FAIL - {e}")

        # Test memory endpoint
        try:
            async with session.get(f"{BASE_URL}/api/memory") as response:
                results["memory"] = response.status == 200
                print(f"✅ Memory endpoint: {'PASS' if results['memory'] else 'FAIL'}")
        except Exception as e:
            results["memory"] = False
            print(f"❌ Memory endpoint: FAIL - {e}")

        # Test observability endpoint
        try:
            async with session.get(f"{BASE_URL}/api/observability/events") as response:
                results["observability"] = response.status == 200
                print(f"✅ Observability endpoint: {'PASS' if results['observability'] else 'FAIL'}")
        except Exception as e:
            results["observability"] = False
            print(f"❌ Observability endpoint: FAIL - {e}")

        return results

async def test_agent_ingestion():
    """Test document ingestion agent"""
    print("\n📄 Testing document ingestion...")

    test_content = """
    # Incident Management Guide

    ## Common Issues
    1. Server downtime - Check network connectivity
    2. Database connection errors - Verify credentials
    3. Memory leaks - Monitor resource usage

    ## Best Practices
    - Always log incidents with timestamps
    - Include error messages and stack traces
    - Document resolution steps
    """

    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "source_type": "text",
                "value": test_content,
                "metadata": {
                    "filename": "test_guide.md",
                    "uploaded_at": "2024-01-01T00:00:00Z"
                }
            }

            async with session.post(
                f"{BASE_URL}/api/agents/ingestion",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Document ingestion: PASS - Indexed {data.get('chunks_indexed', 0)} chunks")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Document ingestion: FAIL - {error}")
                    return False
        except Exception as e:
            print(f"❌ Document ingestion: FAIL - {e}")
            return False

async def test_chat_flow():
    """Test the complete chat flow"""
    print("\n💬 Testing chat flow...")

    async with aiohttp.ClientSession() as session:
        try:
            # Test chat endpoint
            payload = {
                "message": "How do I handle a server downtime incident?",
                "session_id": "test_session_123"
            }

            async with session.post(
                f"{BASE_URL}/api/chat",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ Chat endpoint: PASS - Response received")
                    print(f"   Response preview: {data.get('response', '')[:100]}...")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Chat endpoint: FAIL - {error}")
                    return False
        except Exception as e:
            print(f"❌ Chat endpoint: FAIL - {e}")
            return False

async def test_self_service_agent():
    """Test self-service agent execution"""
    print("\n🤖 Testing self-service agent...")

    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "query": "Check system status and report any issues"
            }

            async with session.post(
                f"{BASE_URL}/api/agents/self-service/run",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    execution_id = data.get("execution_id")
                    print(f"✅ Self-service agent: PASS - Execution ID: {execution_id}")

                    # Wait a bit and check execution status
                    await asyncio.sleep(2)
                    return await check_execution_status(session, execution_id)
                else:
                    error = await response.text()
                    print(f"❌ Self-service agent: FAIL - {error}")
                    return False
        except Exception as e:
            print(f"❌ Self-service agent: FAIL - {e}")
            return False

async def check_execution_status(session, execution_id: str):
    """Check the status of an execution"""
    try:
        async with session.get(f"{BASE_URL}/api/memory/executions/{execution_id}") as response:
            if response.status == 200:
                data = await response.json()
                status = data.get("status", "unknown")
                print(f"   Execution status: {status}")
                return status in ["completed", "running"]
            else:
                print(f"   Could not check execution status")
                return False
    except Exception as e:
        print(f"   Error checking execution status: {e}")
        return False

async def test_feedback_system():
    """Test feedback submission"""
    print("\n📝 Testing feedback system...")

    async with aiohttp.ClientSession() as session:
        try:
            payload = {
                "execution_id": "test_execution_123",
                "rating": 5,
                "comments": "Great response, very helpful!",
                "user_id": "test_user"
            }

            async with session.post(
                f"{BASE_URL}/api/feedback",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    print("✅ Feedback submission: PASS")
                    return True
                else:
                    error = await response.text()
                    print(f"❌ Feedback submission: FAIL - {error}")
                    return False
        except Exception as e:
            print(f"❌ Feedback submission: FAIL - {e}")
            return False

async def run_comprehensive_test():
    """Run all tests"""
    print("🚀 Starting comprehensive Sarthi system test...")
    print("=" * 50)

    # Wait for server to be ready
    print("⏳ Waiting for server to be ready...")
    await asyncio.sleep(3)

    results = {}

    # Test API endpoints
    results["api_endpoints"] = await test_api_endpoints()

    # Test document ingestion
    results["ingestion"] = await test_agent_ingestion()

    # Test chat flow
    results["chat"] = await test_chat_flow()

    # Test self-service agent
    results["self_service"] = await test_self_service_agent()

    # Test feedback
    results["feedback"] = await test_feedback_system()

    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")

    total_tests = 0
    passed_tests = 0

    for category, tests in results.items():
        if isinstance(tests, dict):
            for test_name, passed in tests.items():
                if isinstance(passed, bool):
                    total_tests += 1
                    if passed:
                        passed_tests += 1
                    print(f"   {test_name}: {'✅' if passed else '❌'}")
        else:
            total_tests += 1
            if tests:
                passed_tests += 1
            print(f"   {category}: {'✅' if tests else '❌'}")

    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    print(f"\n🎯 Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")

    if success_rate >= 80:
        print("🎉 System test PASSED! Sarthi is ready for use.")
    else:
        print("⚠️  System test FAILED. Please check the errors above.")

    return success_rate >= 80

if __name__ == "__main__":
    success = asyncio.run(run_comprehensive_test())
    exit(0 if success else 1)