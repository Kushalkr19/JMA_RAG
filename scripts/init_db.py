#!/usr/bin/env python3
"""
Database initialization script for JMA Client Knowledge Base Platform
Populates the database with sample data for demonstration
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models.client import Client
from app.models.stakeholder import Stakeholder
from app.models.engagement import Engagement
from app.models.knowledge_entry import KnowledgeEntry
from app.models.knowledge_embedding import KnowledgeEmbedding
from app.utils.embeddings import embedding_service
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with sample data"""
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_clients = db.query(Client).count()
        if existing_clients > 0:
            logger.info("Database already contains data. Skipping initialization.")
            return
        
        logger.info("Initializing database with sample data...")
        
        # Create sample clients
        clients = [
            Client(
                name="TechCorp Inc.",
                industry="Technology",
                description="A mid-sized technology company specializing in enterprise software solutions with 500+ employees and $50M annual revenue."
            ),
            Client(
                name="HealthSolutions Ltd.",
                industry="Healthcare",
                description="A healthcare technology provider focused on patient management systems and telemedicine platforms."
            )
        ]
        
        for client in clients:
            db.add(client)
        db.commit()
        
        # Refresh to get IDs
        for client in clients:
            db.refresh(client)
        
        logger.info(f"Created {len(clients)} clients")
        
        # Create sample stakeholders
        stakeholders = [
            # TechCorp stakeholders
            Stakeholder(
                client_id=clients[0].id,
                name="Sarah Johnson",
                role="Chief Technology Officer",
                tone="direct",
                priority_1="System modernization",
                priority_2="Security enhancement",
                priority_3="Cost optimization",
                email="sarah.johnson@techcorp.com",
                phone="555-0101"
            ),
            Stakeholder(
                client_id=clients[0].id,
                name="Michael Chen",
                role="VP of Engineering",
                tone="collaborative",
                priority_1="Team productivity",
                priority_2="Code quality",
                priority_3="Innovation",
                email="michael.chen@techcorp.com",
                phone="555-0102"
            ),
            Stakeholder(
                client_id=clients[0].id,
                name="Lisa Rodriguez",
                role="Chief Financial Officer",
                tone="analytical",
                priority_1="Budget control",
                priority_2="ROI measurement",
                priority_3="Risk management",
                email="lisa.rodriguez@techcorp.com",
                phone="555-0103"
            ),
            
            # HealthSolutions stakeholders
            Stakeholder(
                client_id=clients[1].id,
                name="Dr. Robert Wilson",
                role="Chief Medical Officer",
                tone="strategic",
                priority_1="Patient safety",
                priority_2="Clinical efficiency",
                priority_3="Regulatory compliance",
                email="r.wilson@healthsolutions.com",
                phone="555-0201"
            ),
            Stakeholder(
                client_id=clients[1].id,
                name="Jennifer Park",
                role="VP of Operations",
                tone="direct",
                priority_1="Operational efficiency",
                priority_2="Staff training",
                priority_3="Process improvement",
                email="j.park@healthsolutions.com",
                phone="555-0202"
            ),
            Stakeholder(
                client_id=clients[1].id,
                name="David Thompson",
                role="IT Director",
                tone="collaborative",
                priority_1="System integration",
                priority_2="Data security",
                priority_3="User experience",
                email="d.thompson@healthsolutions.com",
                phone="555-0203"
            )
        ]
        
        for stakeholder in stakeholders:
            db.add(stakeholder)
        db.commit()
        
        # Refresh to get IDs
        for stakeholder in stakeholders:
            db.refresh(stakeholder)
        
        logger.info(f"Created {len(stakeholders)} stakeholders")
        
        # Create sample engagements
        engagements = [
            Engagement(
                client_id=clients[0].id,
                name="Digital Transformation Initiative",
                description="Comprehensive technology modernization project",
                status="active",
                start_date=datetime.now().date() - timedelta(days=30),
                end_date=datetime.now().date() + timedelta(days=90),
                daaeg_phase="analyze"
            ),
            Engagement(
                client_id=clients[1].id,
                name="Patient Management System Upgrade",
                description="Upgrade legacy patient management system",
                status="active",
                start_date=datetime.now().date() - timedelta(days=15),
                end_date=datetime.now().date() + timedelta(days=60),
                daaeg_phase="assess"
            )
        ]
        
        for engagement in engagements:
            db.add(engagement)
        db.commit()
        
        # Refresh to get IDs
        for engagement in engagements:
            db.refresh(engagement)
        
        logger.info(f"Created {len(engagements)} engagements")
        
        # Create sample knowledge entries
        knowledge_entries = [
            # TechCorp meeting transcripts
            KnowledgeEntry(
                client_id=clients[0].id,
                engagement_id=engagements[0].id,
                stakeholder_id=stakeholders[0].id,
                entry_type="meeting_transcript",
                title="Initial Technology Assessment Meeting",
                content="""
                Meeting with Sarah Johnson, CTO of TechCorp Inc.
                
                Key Discussion Points:
                - Current technology stack is outdated and causing performance issues
                - Security vulnerabilities identified in legacy systems
                - Need for cloud migration strategy
                - Budget constraints require phased approach
                - Team concerns about change management
                
                Action Items:
                - Conduct detailed security audit
                - Develop migration roadmap
                - Create training plan for development team
                - Establish governance structure
                """,
                meeting_date=datetime.now() - timedelta(days=25)
            ),
            KnowledgeEntry(
                client_id=clients[0].id,
                engagement_id=engagements[0].id,
                stakeholder_id=stakeholders[1].id,
                entry_type="meeting_transcript",
                title="Engineering Team Feedback Session",
                content="""
                Meeting with Michael Chen, VP of Engineering
                
                Engineering Team Concerns:
                - Current development tools are slow and inefficient
                - Code deployment process takes too long
                - Lack of automated testing infrastructure
                - Team morale affected by technical debt
                
                Positive Aspects:
                - Strong team collaboration culture
                - Good domain knowledge
                - Willingness to learn new technologies
                
                Recommendations:
                - Implement CI/CD pipeline
                - Introduce modern development tools
                - Establish code review processes
                - Provide training on new technologies
                """,
                meeting_date=datetime.now() - timedelta(days=20)
            ),
            KnowledgeEntry(
                client_id=clients[0].id,
                engagement_id=engagements[0].id,
                stakeholder_id=stakeholders[2].id,
                entry_type="email",
                title="Budget Approval for Technology Upgrade",
                content="""
                From: Lisa Rodriguez, CFO
                Subject: Budget Approval for Technology Upgrade
                
                After reviewing the proposed technology upgrade plan, I have the following concerns:
                
                Financial Considerations:
                - Total project cost estimated at $2.5M over 18 months
                - Need to demonstrate clear ROI within 12 months
                - Risk of budget overruns given scope complexity
                - Opportunity cost of not investing in other areas
                
                Recommendations:
                - Phase the implementation to spread costs
                - Establish clear success metrics
                - Regular budget reviews and adjustments
                - Contingency planning for unexpected costs
                
                Approval granted with conditions:
                1. Monthly budget reviews
                2. ROI tracking from month 6
                3. Risk mitigation plan required
                """,
                meeting_date=datetime.now() - timedelta(days=15)
            ),
            
            # HealthSolutions meeting transcripts
            KnowledgeEntry(
                client_id=clients[1].id,
                engagement_id=engagements[1].id,
                stakeholder_id=stakeholders[3].id,
                entry_type="meeting_transcript",
                title="Clinical Requirements Gathering",
                content="""
                Meeting with Dr. Robert Wilson, CMO of HealthSolutions Ltd.
                
                Clinical Requirements:
                - System must integrate with existing EMR systems
                - Real-time patient data access for clinicians
                - Automated alerts for critical patient conditions
                - Compliance with HIPAA and other regulations
                - User-friendly interface for medical staff
                
                Current Pain Points:
                - Manual data entry causing errors
                - Delayed access to patient information
                - Inconsistent data across systems
                - Training time for new staff
                
                Success Criteria:
                - 50% reduction in data entry errors
                - 30% faster patient information access
                - 100% regulatory compliance
                - Positive user feedback from medical staff
                """,
                meeting_date=datetime.now() - timedelta(days=10)
            ),
            KnowledgeEntry(
                client_id=clients[1].id,
                engagement_id=engagements[1].id,
                stakeholder_id=stakeholders[4].id,
                entry_type="meeting_transcript",
                title="Operational Impact Assessment",
                content="""
                Meeting with Jennifer Park, VP of Operations
                
                Operational Impact Analysis:
                - Current system processes 500+ patients daily
                - Staff training will require 2 weeks per department
                - System downtime must be minimized during transition
                - Backup procedures needed for critical functions
                
                Resource Requirements:
                - 3 IT staff for system administration
                - 2 trainers for staff education
                - Additional support during go-live period
                - Ongoing maintenance and support
                
                Timeline Considerations:
                - Phased rollout by department recommended
                - 6-month total implementation timeline
                - Parallel running with legacy system for 2 weeks
                - Full cutover after validation period
                """,
                meeting_date=datetime.now() - timedelta(days=5)
            )
        ]
        
        for entry in knowledge_entries:
            db.add(entry)
        db.commit()
        
        # Refresh to get IDs
        for entry in knowledge_entries:
            db.refresh(entry)
        
        logger.info(f"Created {len(knowledge_entries)} knowledge entries")
        
        # Generate embeddings for knowledge entries
        logger.info("Generating embeddings for knowledge entries...")
        for entry in knowledge_entries:
            try:
                embedding_vector = embedding_service.generate_embedding(entry.content)
                db_embedding = KnowledgeEmbedding(
                    knowledge_entry_id=entry.id,
                    embedding=embedding_vector
                )
                db.add(db_embedding)
                logger.info(f"Generated embedding for entry: {entry.title}")
            except Exception as e:
                logger.error(f"Failed to generate embedding for entry {entry.id}: {e}")
        
        db.commit()
        
        logger.info("Database initialization completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("JMA CLIENT KNOWLEDGE BASE - SAMPLE DATA SUMMARY")
        print("="*50)
        print(f"Clients: {len(clients)}")
        print(f"Stakeholders: {len(stakeholders)}")
        print(f"Engagements: {len(engagements)}")
        print(f"Knowledge Entries: {len(knowledge_entries)}")
        print("\nSample Client IDs:")
        for client in clients:
            print(f"  - {client.name}: ID {client.id}")
        print("\nSample Stakeholder IDs:")
        for stakeholder in stakeholders:
            print(f"  - {stakeholder.name} ({stakeholder.role}): ID {stakeholder.id}")
        print("="*50)
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_database()