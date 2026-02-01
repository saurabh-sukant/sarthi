#!/usr/bin/env python3
"""
Test memory persistence - verify write and read work correctly
"""

import asyncio
from app.agents.memory_agent import MemoryAgent
from app.db.sqlite_client import get_memory_items


async def test_memory_write_and_read():
    """Test that memories are written to SQLite and can be read back"""
    print("\n🧪 Testing Memory Persistence...")
    
    # Write some memories
    memory_agent = MemoryAgent()
    
    test_cases = [
        {
            "content": "System optimization improved response time by 40%",
            "type": "semantic",
            "source": "test_optimization"
        },
        {
            "content": "User asked about database indexing strategies",
            "type": "episodic", 
            "source": "test_interaction"
        }
    ]
    
    print("\n📝 Writing memories...")
    written_ids = []
    for i, test in enumerate(test_cases):
        mem_id = await memory_agent.write_memory(
            content=test["content"],
            memory_type=test["type"],
            source=test["source"]
        )
        written_ids.append(mem_id)
        print(f"✅ Memory {i+1} written: {mem_id[:8]}... - {test['type']}")
    
    # Read back memories
    print("\n📖 Reading memories from database...")
    stored_memories = get_memory_items()
    
    print(f"✅ Found {len(stored_memories)} memories in database")
    
    if len(stored_memories) == 0:
        print("❌ ERROR: No memories found in database!")
        return False
    
    for i, mem in enumerate(stored_memories):
        print(f"   {i+1}. Type: {mem['type']}")
        print(f"      Content: {mem['content'][:60]}...")
        print(f"      Source: {mem['source']}")
    
    # Verify semantic memory is there
    semantic_mems = [m for m in stored_memories if m['type'] == 'semantic']
    episodic_mems = [m for m in stored_memories if m['type'] == 'episodic']
    
    print(f"\n📊 Memory Breakdown:")
    print(f"   - Semantic memories: {len(semantic_mems)}")
    print(f"   - Episodic memories: {len(episodic_mems)}")
    
    if len(stored_memories) >= 2:
        print("\n✅ Memory persistence test PASSED")
        return True
    else:
        print("\n❌ Memory persistence test FAILED")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("MEMORY PERSISTENCE TEST")
    print("=" * 60)
    
    try:
        success = asyncio.run(test_memory_write_and_read())
        if success:
            print("\n" + "=" * 60)
            print("✅ TEST PASSED")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ TEST FAILED")
            print("=" * 60)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
