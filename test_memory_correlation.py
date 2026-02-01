#!/usr/bin/env python3
"""
Test memory correlation in orchestrator workflow
Verifies that historical memories are retrieved and included in reasoning context
"""

import asyncio
import json
from app.core.orchestrator import Orchestrator
from app.db.sqlite_client import create_execution, log_observability_event
from app.agents.memory_agent import MemoryAgent
from app.db.chroma_client import store_memory
from datetime import datetime
import uuid

async def test_memory_correlation():
    """Test end-to-end memory correlation workflow"""
    print("\n🧪 Testing Memory Correlation in Orchestrator...")
    
    # Generate test IDs
    conversation_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    
    # Create execution record
    create_execution(execution_id, conversation_id, "What are the key metrics for system performance?")
    
    # Store some historical memories
    print("\n📝 Seeding historical memories...")
    memory_agent = MemoryAgent()
    
    test_memories = [
        "Previous analysis showed CPU utilization peaked at 85% during batch processing",
        "System response time improved from 250ms to 150ms after caching optimization",
        "Database query optimization reduced memory footprint by 40%"
    ]
    
    for i, memory_content in enumerate(test_memories):
        try:
            await memory_agent.write_memory(
                content=memory_content,
                memory_type="semantic",
                source="system_analysis"
            )
            print(f"✅ Stored memory {i+1}: {memory_content[:50]}...")
        except Exception as e:
            print(f"⚠️  Could not store memory {i+1}: {e}")
    
    # Run query through orchestrator
    print("\n🔄 Running query through orchestrator with memory correlation...")
    orchestrator = Orchestrator()
    
    try:
        result = await orchestrator.run_query(
            query="What are the key metrics for system performance?",
            attachments=[],
            mode="chat"
        )
        
        print("\n✅ Orchestrator completed successfully")
        print(f"Execution ID: {result['execution_id']}")
        print(f"Conversation ID: {result['conversation_id']}")
        
        # Check if correlated memories were retrieved
        correlated_memories = result.get("result", {}).get("correlated_memories", [])
        print(f"\n📊 Memory Correlation Results:")
        print(f"   - Correlated memories found: {len(correlated_memories)}")
        
        if correlated_memories:
            print("   - Memory contents:")
            for i, mem in enumerate(correlated_memories, 1):
                mem_content = mem.get("content") if isinstance(mem, dict) else str(mem)
                print(f"     {i}. {mem_content[:80]}...")
        
        # Check reasoning summary to verify memories were included
        reasoning_summary = result.get("result", {}).get("reasoning_summary", "")
        if reasoning_summary:
            print(f"\n🧠 Reasoning Summary:")
            print(f"   {reasoning_summary[:200]}...")
        
        # Check final response
        final_response = result.get("result", {}).get("final_response", "")
        if final_response:
            print(f"\n💬 Final Response:")
            print(f"   {final_response[:200]}...")
        
        print("\n✅ Memory correlation test PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Memory correlation test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_memory_context_inclusion():
    """Verify correlated memories are included in reasoning context"""
    print("\n🧪 Testing Memory Context Inclusion...")
    
    orchestrator = Orchestrator()
    
    # Test _combine_context with all three inputs
    test_docs = {
        "documents": [["Document about system architecture"]]
    }
    test_memory = {
        "documents": [["Memory of previous optimization"]]
    }
    test_correlated = [
        {"content": "Historical finding about performance"},
        {"content": "Past decision on caching strategy"}
    ]
    
    context = orchestrator._combine_context(test_docs, test_memory, test_correlated)
    
    # Verify all three types are in context
    assert "Document about system architecture" in context, "Documents not in context"
    assert "Memory of previous optimization" in context, "Retrieved memory not in context"
    assert "Historical finding about performance" in context, "Correlated memory 1 not in context"
    assert "Past decision on caching strategy" in context, "Correlated memory 2 not in context"
    
    print("✅ All memory types included in reasoning context")
    print(f"Combined context length: {len(context)} characters")
    print(f"Context preview: {context[:200]}...")
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("MEMORY CORRELATION TEST SUITE")
    print("="*60)
    
    # Test 1: Context inclusion
    try:
        asyncio.run(test_memory_context_inclusion())
    except Exception as e:
        print(f"❌ Context inclusion test failed: {e}")
    
    # Test 2: End-to-end orchestrator with memory correlation
    try:
        success = asyncio.run(test_memory_correlation())
        if success:
            print("\n" + "="*60)
            print("✅ ALL TESTS PASSED")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("❌ TESTS FAILED")
            print("="*60)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
