#!/usr/bin/env python3
"""
System test script for JMA Client Knowledge Base Platform
Validates all components and functionality
"""

import sys
import os
import requests
import json
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def test_database_connection():
    """Test database connection and basic operations"""
    print("🔍 Testing database connection...")
    
    try:
        from app.database import SessionLocal, engine
        from app.models.client import Client
        
        # Test connection
        db = SessionLocal()
        client_count = db.query(Client).count()
        db.close()
        
        print(f"   ✅ Database connection successful. Found {client_count} clients.")
        return True
    except Exception as e:
        print(f"   ❌ Database connection failed: {e}")
        return False

def test_embeddings_service():
    """Test embeddings service"""
    print("🔍 Testing embeddings service...")
    
    try:
        from app.utils.embeddings import embedding_service
        
        # Test embedding generation
        test_text = "This is a test document for embedding generation."
        embedding = embedding_service.generate_embedding(test_text)
        
        if len(embedding) == 384:  # Expected dimension
            print(f"   ✅ Embeddings service working. Generated {len(embedding)}-dimensional vector.")
            return True
        else:
            print(f"   ❌ Embeddings service failed. Expected 384 dimensions, got {len(embedding)}.")
            return False
    except Exception as e:
        print(f"   ❌ Embeddings service failed: {e}")
        return False

def test_ai_service():
    """Test AI service"""
    print("🔍 Testing AI service...")
    
    try:
        from app.utils.ai_service import ai_service
        
        # Test mock response generation
        client_info = {"name": "Test Client", "industry": "Technology", "description": "Test description"}
        stakeholder_info = {"name": "Test Stakeholder", "role": "CTO", "tone": "direct", "priority_1": "Efficiency"}
        knowledge_context = [{"title": "Test Meeting", "content": "Test content", "entry_type": "meeting_transcript"}]
        
        content = ai_service.generate_deliverable_content(
            client_info, stakeholder_info, knowledge_context, "Test Report", ["executive_summary"]
        )
        
        if content and "executive_summary" in content:
            print("   ✅ AI service working. Generated mock content successfully.")
            return True
        else:
            print("   ❌ AI service failed. No content generated.")
            return False
    except Exception as e:
        print(f"   ❌ AI service failed: {e}")
        return False

def test_document_generator():
    """Test document generator"""
    print("🔍 Testing document generator...")
    
    try:
        from app.utils.document_generator import document_generator
        
        # Test document creation
        content_sections = {
            "executive_summary": "This is a test executive summary.",
            "key_recommendations": "These are test recommendations."
        }
        
        file_path = document_generator.create_deliverable(
            "Test Client", "Test Report", content_sections, "Test Stakeholder"
        )
        
        if os.path.exists(file_path):
            print(f"   ✅ Document generator working. Created: {file_path}")
            return True
        else:
            print("   ❌ Document generator failed. File not created.")
            return False
    except Exception as e:
        print(f"   ❌ Document generator failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("🔍 Testing API endpoints...")
    
    base_url = "http://localhost:8000/api"
    tests_passed = 0
    total_tests = 0
    
    try:
        # Test health endpoint
        total_tests += 1
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ Health endpoint working")
            tests_passed += 1
        else:
            print(f"   ❌ Health endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Health endpoint failed: {e}")
    
    try:
        # Test clients endpoint
        total_tests += 1
        response = requests.get(f"{base_url}/clients", timeout=5)
        if response.status_code == 200:
            clients = response.json()
            print(f"   ✅ Clients endpoint working. Found {len(clients)} clients")
            tests_passed += 1
        else:
            print(f"   ❌ Clients endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Clients endpoint failed: {e}")
    
    try:
        # Test stakeholders endpoint
        total_tests += 1
        response = requests.get(f"{base_url}/stakeholders", timeout=5)
        if response.status_code == 200:
            stakeholders = response.json()
            print(f"   ✅ Stakeholders endpoint working. Found {len(stakeholders)} stakeholders")
            tests_passed += 1
        else:
            print(f"   ❌ Stakeholders endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stakeholders endpoint failed: {e}")
    
    try:
        # Test knowledge endpoint
        total_tests += 1
        response = requests.get(f"{base_url}/knowledge", timeout=5)
        if response.status_code == 200:
            knowledge = response.json()
            print(f"   ✅ Knowledge endpoint working. Found {len(knowledge)} entries")
            tests_passed += 1
        else:
            print(f"   ❌ Knowledge endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Knowledge endpoint failed: {e}")
    
    try:
        # Test search endpoint
        total_tests += 1
        response = requests.get(f"{base_url}/search/semantic", params={"query": "test"}, timeout=5)
        if response.status_code == 200:
            search = response.json()
            print(f"   ✅ Search endpoint working. Found {search['total_found']} results")
            tests_passed += 1
        else:
            print(f"   ❌ Search endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Search endpoint failed: {e}")
    
    print(f"   📊 API tests: {tests_passed}/{total_tests} passed")
    return tests_passed == total_tests

def test_rag_pipeline():
    """Test complete RAG pipeline"""
    print("🔍 Testing RAG pipeline...")
    
    base_url = "http://localhost:8000/api"
    
    try:
        # Get a client and stakeholder
        response = requests.get(f"{base_url}/clients", timeout=5)
        if response.status_code != 200:
            print("   ❌ Could not get clients for RAG test")
            return False
        
        clients = response.json()
        if not clients:
            print("   ❌ No clients found for RAG test")
            return False
        
        client = clients[0]
        
        response = requests.get(f"{base_url}/stakeholders/client/{client['id']}", timeout=5)
        if response.status_code != 200:
            print("   ❌ Could not get stakeholders for RAG test")
            return False
        
        stakeholders = response.json()
        if not stakeholders:
            print("   ❌ No stakeholders found for RAG test")
            return False
        
        stakeholder = stakeholders[0]
        
        # Test deliverable generation
        deliverable_request = {
            "client_id": client['id'],
            "title": "System Test Report",
            "deliverable_type": "Test Report",
            "target_stakeholder_id": stakeholder['id'],
            "sections": ["executive_summary", "key_recommendations"]
        }
        
        response = requests.post(f"{base_url}/deliverables/generate", json=deliverable_request, timeout=30)
        
        if response.status_code == 200:
            deliverable = response.json()
            print(f"   ✅ RAG pipeline working. Generated deliverable: {deliverable['title']}")
            return True
        else:
            print(f"   ❌ RAG pipeline failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ RAG pipeline test failed: {e}")
        return False

def run_all_tests():
    """Run all system tests"""
    print("="*60)
    print("JMA CLIENT KNOWLEDGE BASE - SYSTEM TESTS")
    print("="*60)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("Embeddings Service", test_embeddings_service),
        ("AI Service", test_ai_service),
        ("Document Generator", test_document_generator),
        ("API Endpoints", test_api_endpoints),
        ("RAG Pipeline", test_rag_pipeline)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "="*60)
    print(f"TEST SUMMARY: {passed}/{total} tests passed")
    print("="*60)
    
    if passed == total:
        print("🎉 All tests passed! System is working correctly.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)