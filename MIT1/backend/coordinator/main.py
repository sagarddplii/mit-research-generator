"""
Main coordinator module for orchestrating the research paper generation workflow.
Also exposes an API router for POST /research-pipeline that orchestrates via HTTP.
"""

from typing import Dict, List, Any, Optional
import asyncio
import os
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
from .utils import Logger, Config

class ResearchCoordinator:
    """Coordinates the research paper generation process."""
    
    def __init__(self):
        self.logger = Logger(__name__)
        self.config = Config()
        self.agents = {}
        
    async def initialize_agents(self):
        """Initialize all required agents."""
        try:
            from agents.retrieval_agent import RetrievalAgent
            from agents.summarizer_agent import SummarizerAgent
            from agents.citation_agent import CitationAgent
            from agents.paper_generator_agent import PaperGeneratorAgent
            from agents.analytics_agent import AnalyticsAgent
            
            self.agents = {
                'retrieval': RetrievalAgent(),
                'summarizer': SummarizerAgent(),
                'citation': CitationAgent(),
                'paper_generator': PaperGeneratorAgent(),
                'analytics': AnalyticsAgent()
            }
            
            self.logger.info("All agents initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize agents: {str(e)}")
            raise
    
    async def generate_research_paper(self, topic: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main workflow for generating a research paper.
        
        Args:
            topic: Research topic
            requirements: Additional requirements for the paper
            
        Returns:
            Generated paper data
        """
        try:
            self.logger.info(f"Starting research paper generation for topic: {topic}")
            
            # Step 1: Retrieve relevant papers
            papers = await self.agents['retrieval'].retrieve_papers(topic, requirements)
            
            # Step 2: Summarize key findings
            summaries = await self.agents['summarizer'].summarize_papers(papers)
            
            # Step 3: Generate citations
            citations = await self.agents['citation'].generate_citations(papers, summaries)
            
            # Step 4: Generate paper draft
            paper_draft = await self.agents['paper_generator'].generate_draft(
                topic, summaries, citations, requirements
            )
            
            # Step 5: Replace citation placeholders with actual citations
            citation_style = requirements.get('citation_style', 'apa')
            paper_draft = await self._replace_citations_in_draft(paper_draft, papers, citation_style)
            
            # Step 6: Generate analytics
            analytics = await self.agents['analytics'].analyze_paper(paper_draft, papers)
            
            result = {
                'topic': topic,
                'paper_draft': paper_draft,
                'citations': citations,
                'analytics': analytics,
                'status': 'completed'
            }
            
            self.logger.info("Research paper generation completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in research paper generation: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    async def _replace_citations_in_draft(self, paper_draft: Dict[str, Any], papers: List[Dict[str, Any]], 
                                        citation_style: str) -> Dict[str, Any]:
        """Replace citation placeholders in the paper draft."""
        try:
            # Replace citations in abstract
            if 'abstract' in paper_draft:
                paper_draft['abstract'] = await self.agents['citation'].replace_citation_placeholders(
                    paper_draft['abstract'], papers, citation_style
                )
            
            # Replace citations in sections
            if 'sections' in paper_draft:
                for section_name, section_content in paper_draft['sections'].items():
                    if isinstance(section_content, dict) and 'content' in section_content:
                        paper_draft['sections'][section_name]['content'] = await self.agents['citation'].replace_citation_placeholders(
                            section_content['content'], papers, citation_style
                        )
                    elif isinstance(section_content, str):
                        paper_draft['sections'][section_name] = await self.agents['citation'].replace_citation_placeholders(
                            section_content, papers, citation_style
                        )
            
            return paper_draft
            
        except Exception as e:
            self.logger.error(f"Error replacing citations in draft: {str(e)}")
            return paper_draft

# -----------------------------
# FastAPI Router for Orchestration
# -----------------------------

router = APIRouter()

class ResearchPipelineRequest(BaseModel):
    query: str
    timeout_seconds: Optional[float] = 20.0

@router.post("/research-pipeline")
async def research_pipeline_endpoint(request: ResearchPipelineRequest):
    """
    Orchestrates via HTTP to the retrieval endpoint, with an explicit OpenAlex fallback,
    then runs summarizer -> generator -> analytics.
    Returns {status, papers, summaries, draft, analytics}.
    """
    logger = logging.getLogger(__name__)
    base_url = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
    timeout = httpx.Timeout(request.timeout_seconds or 20.0)

    try:
        # 1) Direct retrieval via agent (avoid HTTP circular dependency)
        from agents.retrieval_agent import RetrievalAgent
        retrieval_agent = RetrievalAgent()
        
        logger.info(f"Starting retrieval for query: {request.query}")
        papers = await retrieval_agent.retrieve_papers(request.query, {
            "max_papers": 10,
            "sources": ["semantic_scholar", "pubmed", "core", "openalex"]
        })
        
        logger.info(f"Retrieved {len(papers)} papers")
        
        # 2) Fallback to OpenAlex only if empty
        if not papers:
            logger.info("No papers returned; attempting OpenAlex fallback")
            papers = await retrieval_agent.retrieve_papers(request.query, {
                "max_papers": 10,
                "sources": ["openalex"]
            })

        if not papers:
            return {
                "status": "no_papers",
                "papers": [],
                "summaries": {},
                "draft": {},
                "analytics": {}
            }

        # 3) Use Supervisor Agent to coordinate all agents
        from agents.supervisor_agent import SupervisorAgent
        
        supervisor = SupervisorAgent()
        
        # Let supervisor handle the entire pipeline
        pipeline_requirements = {
            "max_papers": 10,
            "sources": ["semantic_scholar", "pubmed", "core", "openalex"],
            "length": "medium",
            "citation_style": "apa"
        }
        
        result = await supervisor.supervise_research_pipeline(request.query, pipeline_requirements)
        
        return {
            "status": result.get("status", "success"),
            "papers": result.get("papers", papers),
            "summaries": result.get("summaries", {}),
            "draft": result.get("draft", {}),
            "analytics": result.get("analytics", {}),
            "references": result.get("references", []),
            "supervisor_metrics": result.get("supervisor_metrics", {})
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Download endpoints
class DownloadRequest(BaseModel):
    research_data: Dict[str, Any]
    format: str

@router.post("/download/{format_type}")
async def download_research_paper(format_type: str, request: DownloadRequest):
    """Download research paper in specified format."""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.download_service import DownloadService
        
        download_service = DownloadService()
        
        if format_type not in download_service.supported_formats:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format_type}")
        
        result = await download_service.generate_download(request.research_data, format_type)
        
        if 'error' in result:
            raise HTTPException(status_code=500, detail=result['error'])
        
        # Return file content
        return Response(
            content=result['content'].encode('utf-8'),
            media_type=result['mime_type'],
            headers={
                'Content-Disposition': f'attachment; filename="{result["filename"]}"',
                'Content-Length': str(result['size'])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download failed: {str(e)}")

@router.get("/download/formats")
async def get_download_formats():
    """Get list of supported download formats."""
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from services.download_service import DownloadService
        
        download_service = DownloadService()
        return {
            'supported_formats': download_service.get_supported_formats()
        }
        
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting formats: {str(e)}")
        return {'error': str(e)}

async def main():
    """Main entry point."""
    coordinator = ResearchCoordinator()
    await coordinator.initialize_agents()
    
    # Example usage
    topic = "Machine Learning in Healthcare"
    requirements = {
        'length': 'medium',
        'focus_areas': ['diagnosis', 'treatment'],
        'publication_target': 'journal'
    }
    
    result = await coordinator.generate_research_paper(topic, requirements)
    print(f"Generation result: {result}")

if __name__ == "__main__":
    asyncio.run(main())
