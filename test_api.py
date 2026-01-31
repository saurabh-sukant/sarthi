#!/usr/bin/env python3
"""
Simple test script for Sarthi API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_root():
    """Test root endpoint"""
    response = requests.get(f"{BASE_URL}/")
    print(f"Root endpoint: {response.status_code}")
    print(response.json())

def test_chat_query():
    """Test chat query submission"""
    payload = {
        "query": "Why is my gateway timing out?",
        "attachments": [],
        "mode": "chat"
    }
    response = requests.post(f"{BASE_URL}/api/chat/query", json=payload)
    print(f"Chat query: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Response: {result}")
        return result.get("execution_id")
    return None

def test_memory_list():
    """Test memory listing"""
    response = requests.get(f"{BASE_URL}/api/memory")
    print(f"Memory list: {response.status_code}")
    if response.status_code == 200:
        memories = response.json()
        print(f"Memories: {len(memories)} items")

def test_agents_list():
    """Test agents listing"""
    response = requests.get(f"{BASE_URL}/api/agents")
    print(f"Agents list: {response.status_code}")
    if response.status_code == 200:
        agents = response.json()
        print(f"Agents: {agents}")

def test_ingestion():
    """Test document ingestion"""
    payload = {
        "source_type": "text",
        "value": "Test document about authentication failures",
        "metadata": {"category": "security"}
    }
    response = requests.post(f"{BASE_URL}/api/agents/ingestion", json=payload)
    print(f"Ingestion: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Ingestion result: {result}")

if __name__ == "__main__":
    print("Testing Sarthi API...")

    test_root()
    print()

    test_memory_list()
    print()

    test_agents_list()
    print()

    test_ingestion()
    print()

    execution_id = test_chat_query()
    print()

    if execution_id:
        print(f"Execution ID: {execution_id}")
        # Could test streaming here, but requires SSE client

    print("API tests completed!")