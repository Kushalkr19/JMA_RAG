import openai
from typing import List, Dict, Any, Optional
from app.utils.config import settings
import logging
import json

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        if settings.openai_api_key:
            openai.api_key = settings.openai_api_key
        self.client = openai.OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None
    
    def generate_deliverable_content(
        self,
        client_info: Dict[str, Any],
        stakeholder_info: Dict[str, Any],
        knowledge_context: List[Dict[str, Any]],
        deliverable_type: str,
        sections: List[str]
    ) -> Dict[str, str]:
        """
        Generate deliverable content using RAG pipeline
        """
        try:
            # Build the sophisticated prompt
            prompt = self._build_rag_prompt(
                client_info, stakeholder_info, knowledge_context, 
                deliverable_type, sections
            )
            
            # Generate content using OpenAI
            if self.client:
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert consultant from Jacob Meadow Associates."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3,
                    max_tokens=2000
                )
                
                content = response.choices[0].message.content
                
                # Parse the structured response
                return self._parse_ai_response(content, sections)
            else:
                # Fallback to mock response for demo
                return self._generate_mock_response(client_info, stakeholder_info, sections)
                
        except Exception as e:
            logger.error(f"Failed to generate deliverable content: {e}")
            return self._generate_mock_response(client_info, stakeholder_info, sections)
    
    def _build_rag_prompt(
        self,
        client_info: Dict[str, Any],
        stakeholder_info: Dict[str, Any],
        knowledge_context: List[Dict[str, Any]],
        deliverable_type: str,
        sections: List[str]
    ) -> str:
        """
        Build sophisticated RAG prompt with ethical guardrails
        """
        
        # Ethical guardrails (non-negotiable)
        ethical_guardrails = """
        ETHICAL GUARDRAILS (MANDATORY):
        - Your primary directive is to be objective and fact-based
        - Do not invent information not present in the provided context
        - Analyze the provided information without bias
        - Avoid loaded, subjective, or stereotypical language
        - If information is insufficient, clearly state what additional data is needed
        - Always maintain professional, consultative tone
        """
        
        # Client context
        client_context = f"""
        CLIENT INFORMATION:
        Name: {client_info.get('name', 'N/A')}
        Industry: {client_info.get('industry', 'N/A')}
        Description: {client_info.get('description', 'N/A')}
        """
        
        # Stakeholder context
        stakeholder_context = f"""
        TARGET STAKEHOLDER:
        Name: {stakeholder_info.get('name', 'N/A')}
        Role: {stakeholder_info.get('role', 'N/A')}
        Tone Preference: {stakeholder_info.get('tone', 'professional')}
        Top Priorities:
        1. {stakeholder_info.get('priority_1', 'N/A')}
        2. {stakeholder_info.get('priority_2', 'N/A')}
        3. {stakeholder_info.get('priority_3', 'N/A')}
        """
        
        # Knowledge context
        knowledge_text = "\n\n".join([
            f"Source: {entry.get('title', 'N/A')} ({entry.get('entry_type', 'N/A')})\n"
            f"Date: {entry.get('meeting_date', 'N/A')}\n"
            f"Content: {entry.get('content', 'N/A')}"
            for entry in knowledge_context
        ])
        
        knowledge_context = f"""
        RELEVANT KNOWLEDGE CONTEXT:
        {knowledge_text}
        """
        
        # Task specification
        task_spec = f"""
        TASK:
        Generate a {deliverable_type} deliverable for {client_info.get('name', 'the client')}.
        
        Required sections: {', '.join(sections)}
        
        TONE REQUIREMENTS:
        - Match the stakeholder's tone preference: {stakeholder_info.get('tone', 'professional')}
        - Use direct language for 'direct' tone
        - Use collaborative language for 'collaborative' tone
        - Use analytical language for 'analytical' tone
        - Use strategic language for 'strategic' tone
        - Reference the DAAEG framework where appropriate
        - Avoid jargon unless necessary
        """
        
        # Output format
        output_format = """
        OUTPUT FORMAT:
        Return a JSON object with the following structure:
        {
            "executive_summary": "Content for executive summary...",
            "key_recommendations": "Content for key recommendations...",
            "background": "Content for background section...",
            "analysis": "Content for analysis section...",
            "next_steps": "Content for next steps..."
        }
        
        Only include sections that were requested in the sections list.
        """
        
        # Combine all parts
        full_prompt = f"""
        {ethical_guardrails}
        
        {client_context}
        
        {stakeholder_context}
        
        {knowledge_context}
        
        {task_spec}
        
        {output_format}
        """
        
        return full_prompt
    
    def _parse_ai_response(self, content: str, sections: List[str]) -> Dict[str, str]:
        """
        Parse AI response and extract sections
        """
        try:
            # Try to parse as JSON
            if content.strip().startswith('{'):
                response_data = json.loads(content)
                return {section: response_data.get(section, '') for section in sections}
            else:
                # Fallback parsing for non-JSON responses
                return self._parse_text_response(content, sections)
        except json.JSONDecodeError:
            return self._parse_text_response(content, sections)
    
    def _parse_text_response(self, content: str, sections: List[str]) -> Dict[str, str]:
        """
        Parse text response when JSON parsing fails
        """
        result = {}
        current_section = None
        current_content = []
        
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if line contains section header
            for section in sections:
                if section.replace('_', ' ').lower() in line.lower():
                    if current_section:
                        result[current_section] = '\n'.join(current_content).strip()
                    current_section = section
                    current_content = []
                    break
            else:
                if current_section:
                    current_content.append(line)
        
        # Add final section
        if current_section and current_content:
            result[current_section] = '\n'.join(current_content).strip()
        
        # Ensure all requested sections are present
        for section in sections:
            if section not in result:
                result[section] = f"[{section.replace('_', ' ').title()} content to be generated]"
        
        return result
    
    def _generate_mock_response(
        self,
        client_info: Dict[str, Any],
        stakeholder_info: Dict[str, Any],
        sections: List[str]
    ) -> Dict[str, str]:
        """
        Generate mock response for demo purposes
        """
        client_name = client_info.get('name', 'the client')
        stakeholder_tone = stakeholder_info.get('tone', 'professional')
        
        mock_responses = {
            'executive_summary': f"""
            Executive Summary for {client_name}
            
            Based on our comprehensive analysis of {client_name}'s current state and strategic objectives, 
            we have identified key opportunities for improvement and growth. The organization demonstrates 
            strong foundational capabilities while facing specific challenges that require targeted intervention.
            
            Our assessment reveals that {client_name} is positioned to achieve significant operational 
            improvements through strategic technology investments and process optimization initiatives.
            """,
            
            'key_recommendations': f"""
            Key Recommendations
            
            1. **Immediate Priority Actions**
               - Implement the proposed technology roadmap within the next 90 days
               - Establish cross-functional governance structure for project oversight
               - Begin stakeholder alignment sessions to ensure buy-in
            
            2. **Strategic Initiatives**
               - Develop comprehensive change management strategy
               - Create detailed implementation timeline with milestone tracking
               - Establish metrics and KPIs for success measurement
            
            3. **Risk Mitigation**
               - Identify and address potential resistance points early
               - Develop contingency plans for critical path items
               - Ensure adequate resource allocation and budget planning
            """,
            
            'background': f"""
            Background and Context
            
            {client_name} operates in a dynamic industry environment characterized by rapid technological 
            change and increasing competitive pressures. The organization has maintained steady growth 
            while facing operational challenges that impact efficiency and scalability.
            
            Recent stakeholder discussions have highlighted concerns about system integration, 
            data management, and process automation capabilities.
            """,
            
            'analysis': f"""
            Analysis and Findings
            
            Our analysis of {client_name}'s current state reveals several key findings:
            
            **Strengths:**
            - Strong market position and brand recognition
            - Dedicated team with deep industry expertise
            - Established customer relationships and trust
            
            **Areas for Improvement:**
            - Technology infrastructure requires modernization
            - Process efficiency can be enhanced through automation
            - Data management and analytics capabilities need strengthening
            
            **Opportunities:**
            - Leverage emerging technologies for competitive advantage
            - Implement data-driven decision making processes
            - Optimize operational workflows for improved productivity
            """,
            
            'next_steps': f"""
            Next Steps and Implementation Plan
            
            To successfully implement the recommended changes, we propose the following next steps:
            
            **Phase 1 (Weeks 1-4):**
            - Finalize project scope and objectives
            - Establish project governance structure
            - Begin stakeholder engagement and communication planning
            
            **Phase 2 (Weeks 5-12):**
            - Execute technology implementation roadmap
            - Conduct training and change management activities
            - Monitor progress and adjust as needed
            
            **Phase 3 (Weeks 13-16):**
            - Complete implementation and testing
            - Conduct post-implementation review
            - Establish ongoing monitoring and optimization processes
            """
        }
        
        # Adjust tone based on stakeholder preference
        if stakeholder_tone == 'direct':
            for section, content in mock_responses.items():
                mock_responses[section] = content.replace('we have identified', 'we identified').replace('we propose', 'we recommend')
        elif stakeholder_tone == 'collaborative':
            for section, content in mock_responses.items():
                mock_responses[section] = content.replace('we recommend', 'we suggest working together to').replace('we identified', 'our collaborative analysis revealed')
        
        return {section: mock_responses.get(section, f"[{section.replace('_', ' ').title()} content]") for section in sections}

# Global AI service instance
ai_service = AIService()