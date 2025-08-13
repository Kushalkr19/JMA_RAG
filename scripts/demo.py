#!/usr/bin/env python3
"""
Demo script for JMA Client Knowledge Base Platform
Demonstrates the RAG pipeline and deliverable generation
"""

import sys
import os
import requests
import json
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

def demo_rag_pipeline():
    """Demonstrate the complete RAG pipeline"""
    
    base_url = "http://localhost:8000/api"
    
    print("="*60)
    print("JMA CLIENT KNOWLEDGE BASE - RAG PIPELINE DEMO")
    print("="*60)
    
    try:
        # 1. Get clients
        print("\n1. Retrieving clients...")
        response = requests.get(f"{base_url}/clients")
        clients = response.json()
        
        if not clients:
            print("No clients found. Please run the database initialization first.")
            return
        
        client = clients[0]  # Use first client
        print(f"   Using client: {client['name']} (ID: {client['id']})")
        
        # 2. Get stakeholders
        print("\n2. Retrieving stakeholders...")
        response = requests.get(f"{base_url}/stakeholders/client/{client['id']}")
        stakeholders = response.json()
        
        if not stakeholders:
            print("No stakeholders found for this client.")
            return
        
        stakeholder = stakeholders[0]  # Use first stakeholder
        print(f"   Using stakeholder: {stakeholder['name']} ({stakeholder['role']})")
        print(f"   Tone: {stakeholder['tone']}")
        print(f"   Priorities: {stakeholder['priority_1']}, {stakeholder['priority_2']}, {stakeholder['priority_3']}")
        
        # 3. Get knowledge entries
        print("\n3. Retrieving knowledge entries...")
        response = requests.get(f"{base_url}/knowledge/client/{client['id']}")
        knowledge_entries = response.json()
        
        print(f"   Found {len(knowledge_entries)} knowledge entries")
        for entry in knowledge_entries:
            print(f"   - {entry['title']} ({entry['entry_type']}) - Has embedding: {entry['has_embedding']}")
        
        # 4. Test semantic search
        print("\n4. Testing semantic search...")
        search_query = "technology modernization security"
        response = requests.get(f"{base_url}/search/semantic", params={
            "query": search_query,
            "client_id": client['id'],
            "limit": 3
        })
        search_results = response.json()
        
        print(f"   Search query: '{search_query}'")
        print(f"   Found {search_results['total_found']} relevant entries")
        for result in search_results['results']:
            print(f"   - {result['title']} (similarity: {result['similarity']})")
        
        # 5. Test stakeholder priority search
        print("\n5. Testing stakeholder priority search...")
        response = requests.get(f"{base_url}/search/by-stakeholder-priority", params={
            "stakeholder_id": stakeholder['id'],
            "limit": 3
        })
        priority_results = response.json()
        
        print(f"   Stakeholder priorities: {priority_results['stakeholder_priorities']}")
        print(f"   Found {priority_results['total_found']} relevant entries")
        for result in priority_results['results']:
            print(f"   - {result['title']} (similarity: {result['similarity']})")
        
        # 6. Generate deliverable
        print("\n6. Generating deliverable using RAG pipeline...")
        deliverable_request = {
            "client_id": client['id'],
            "title": f"Technology Assessment Report for {client['name']}",
            "deliverable_type": "Technology Assessment",
            "target_stakeholder_id": stakeholder['id'],
            "sections": ["executive_summary", "key_recommendations", "background", "analysis", "next_steps"]
        }
        
        response = requests.post(f"{base_url}/deliverables/generate", json=deliverable_request)
        
        if response.status_code == 200:
            deliverable = response.json()
            print(f"   ✅ Deliverable generated successfully!")
            print(f"   Title: {deliverable['title']}")
            print(f"   Status: {deliverable['status']}")
            print(f"   File path: {deliverable['file_path']}")
            
            # Display generated content
            if deliverable['ai_generated_content']:
                print(f"\n   Generated content preview:")
                content_preview = deliverable['ai_generated_content'][:500] + "..."
                print(f"   {content_preview}")
        else:
            print(f"   ❌ Failed to generate deliverable: {response.text}")
        
        # 7. Test hybrid search
        print("\n7. Testing hybrid search...")
        response = requests.get(f"{base_url}/search/hybrid", params={
            "query": "system modernization",
            "client_id": client['id'],
            "stakeholder_id": stakeholder['id'],
            "limit": 3
        })
        hybrid_results = response.json()
        
        print(f"   Hybrid search results:")
        for result in hybrid_results['results']:
            print(f"   - {result['title']}")
            print(f"     Semantic score: {result['semantic_score']}, Priority score: {result['priority_score']}")
            print(f"     Combined score: {result['combined_score']}")
        
        print("\n" + "="*60)
        print("DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        
        # Print next steps
        print("\nNext steps:")
        print("1. Check the generated Word document in the data/deliverables/ directory")
        print("2. Review the API documentation at http://localhost:8000/docs")
        print("3. Test different stakeholders and search queries")
        print("4. Approve deliverables to enrich the knowledge base")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print("   Make sure the server is running: python backend/main.py")
    except Exception as e:
        print(f"❌ Demo failed: {e}")

def demo_api_endpoints():
    """Demonstrate individual API endpoints"""
    
    base_url = "http://localhost:8000/api"
    
    print("\n" + "="*60)
    print("API ENDPOINTS DEMO")
    print("="*60)
    
    try:
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        print(f"Health check: {response.json()}")
        
        # Test clients endpoint
        response = requests.get(f"{base_url}/clients")
        clients = response.json()
        print(f"Clients endpoint: {len(clients)} clients found")
        
        # Test stakeholders endpoint
        if clients:
            response = requests.get(f"{base_url}/stakeholders/client/{clients[0]['id']}")
            stakeholders = response.json()
            print(f"Stakeholders endpoint: {len(stakeholders)} stakeholders found")
        
        # Test knowledge endpoint
        response = requests.get(f"{base_url}/knowledge")
        knowledge = response.json()
        print(f"Knowledge endpoint: {len(knowledge)} entries found")
        
        # Test search endpoint
        response = requests.get(f"{base_url}/search/semantic", params={"query": "technology"})
        search = response.json()
        print(f"Search endpoint: {search['total_found']} results found")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
    except Exception as e:
        print(f"❌ API demo failed: {e}")

if __name__ == "__main__":
    print("JMA Client Knowledge Base Platform - Demo")
    print("This demo will test the complete RAG pipeline and API functionality.")
    
    # Run the main demo
    demo_rag_pipeline()
    
    # Run API endpoints demo
    demo_api_endpoints()