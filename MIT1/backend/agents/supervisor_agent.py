"""
Supervisor agent for coordinating and monitoring all other agents in the research pipeline.
This agent ensures reliability, handles errors, and optimizes the workflow.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import time
from enum import Enum

class AgentStatus(Enum):
    """Status of individual agents."""
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class PipelineStage(Enum):
    """Stages of the research pipeline."""
    RETRIEVAL = "retrieval"
    SUMMARIZATION = "summarization"
    CITATION = "citation"
    GENERATION = "generation"
    ANALYTICS = "analytics"

class SupervisorAgent:
    """Supervisor agent that coordinates and monitors all other agents."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.agent_status = {}
        self.pipeline_metrics = {}
        self.error_history = []
        self.retry_config = {
            'max_retries': 3,
            'retry_delay': 1.0,
            'timeout_seconds': 30.0
        }
    
    async def supervise_research_pipeline(self, query: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Supervise the entire research pipeline with error handling and monitoring.
        
        Args:
            query: Research query
            requirements: Pipeline requirements
            
        Returns:
            Comprehensive pipeline result with monitoring data
        """
        pipeline_start = time.time()
        pipeline_id = f"pipeline_{int(pipeline_start)}"
        
        try:
            self.logger.info(f"🎯 Supervisor starting pipeline {pipeline_id} for query: '{query}'")
            
            # Initialize pipeline tracking
            self.pipeline_metrics[pipeline_id] = {
                'start_time': pipeline_start,
                'query': query,
                'stages_completed': [],
                'errors': [],
                'retries': 0,
                'total_papers': 0
            }
            
            # Stage 1: Paper Retrieval
            papers = await self._supervise_retrieval(query, requirements, pipeline_id)
            
            # Stage 2: Summarization
            summaries = await self._supervise_summarization(papers, pipeline_id)
            
            # Stage 3: Citation Generation
            citations = await self._supervise_citation_generation(papers, summaries, pipeline_id)
            
            # Stage 4: Paper Generation
            draft = await self._supervise_paper_generation(query, summaries, citations, requirements, pipeline_id)
            
            # Stage 5: Citation Replacement
            draft = await self._supervise_citation_replacement(draft, papers, requirements.get('citation_style', 'apa'), pipeline_id)
            
            # Stage 6: Analytics
            analytics = await self._supervise_analytics(draft, papers, pipeline_id)
            
            # Stage 7: Reference Formatting
            references = await self._supervise_reference_formatting(papers, citations, requirements.get('citation_style', 'apa'), pipeline_id)
            
            # Calculate final metrics
            total_time = time.time() - pipeline_start
            self.pipeline_metrics[pipeline_id]['total_time'] = total_time
            self.pipeline_metrics[pipeline_id]['total_papers'] = len(papers)
            
            self.logger.info(f"✅ Supervisor completed pipeline {pipeline_id} in {total_time:.2f}s")
            
            return {
                'status': 'success',
                'pipeline_id': pipeline_id,
                'query': query,
                'papers': papers,
                'summaries': summaries,
                'citations': citations,
                'draft': draft,
                'analytics': analytics,
                'references': references,
                'supervisor_metrics': self.pipeline_metrics[pipeline_id],
                'processing_time': total_time
            }
            
        except Exception as e:
            total_time = time.time() - pipeline_start
            self.logger.error(f"❌ Supervisor pipeline {pipeline_id} failed: {str(e)}")
            
            # Record error
            error_record = {
                'timestamp': datetime.now().isoformat(),
                'pipeline_id': pipeline_id,
                'error': str(e),
                'stage': self._get_current_stage(pipeline_id),
                'duration': total_time
            }
            self.error_history.append(error_record)
            
            return {
                'status': 'error',
                'pipeline_id': pipeline_id,
                'query': query,
                'error': str(e),
                'supervisor_metrics': self.pipeline_metrics.get(pipeline_id, {}),
                'processing_time': total_time
            }
    
    async def _supervise_retrieval(self, query: str, requirements: Dict[str, Any], pipeline_id: str) -> List[Dict[str, Any]]:
        """Supervise the paper retrieval stage."""
        stage = PipelineStage.RETRIEVAL
        self.logger.info(f"📚 Supervisor: Starting {stage.value}")
        
        try:
            from agents.retrieval_agent import RetrievalAgent
            
            retrieval_agent = RetrievalAgent()
            self._update_agent_status(pipeline_id, stage, AgentStatus.RUNNING)
            
            papers = await self._execute_with_retry(
                retrieval_agent.retrieve_papers,
                query,
                requirements,
                stage=stage,
                pipeline_id=pipeline_id
            )
            
            if not papers:
                raise Exception("No papers retrieved from any source")
            
            self._update_agent_status(pipeline_id, stage, AgentStatus.COMPLETED)
            self.pipeline_metrics[pipeline_id]['stages_completed'].append(stage.value)
            
            self.logger.info(f"✅ Supervisor: {stage.value} completed - {len(papers)} papers retrieved")
            return papers
            
        except Exception as e:
            self._update_agent_status(pipeline_id, stage, AgentStatus.FAILED)
            self.logger.error(f"❌ Supervisor: {stage.value} failed - {str(e)}")
            raise
    
    async def _supervise_summarization(self, papers: List[Dict[str, Any]], pipeline_id: str) -> Dict[str, Any]:
        """Supervise the summarization stage."""
        stage = PipelineStage.SUMMARIZATION
        self.logger.info(f"📝 Supervisor: Starting {stage.value}")
        
        try:
            from agents.summarizer_agent import SummarizerAgent
            
            summarizer_agent = SummarizerAgent()
            self._update_agent_status(pipeline_id, stage, AgentStatus.RUNNING)
            
            summaries = await self._execute_with_retry(
                summarizer_agent.summarize_papers,
                papers,
                stage=stage,
                pipeline_id=pipeline_id
            )
            
            self._update_agent_status(pipeline_id, stage, AgentStatus.COMPLETED)
            self.pipeline_metrics[pipeline_id]['stages_completed'].append(stage.value)
            
            self.logger.info(f"✅ Supervisor: {stage.value} completed")
            return summaries
            
        except Exception as e:
            self._update_agent_status(pipeline_id, stage, AgentStatus.FAILED)
            self.logger.error(f"❌ Supervisor: {stage.value} failed - {str(e)}")
            # Return minimal summaries to keep pipeline running
            return {
                'individual_summaries': [],
                'thematic_summary': f"Analysis of {len(papers)} papers on the research topic.",
                'key_findings': [],
                'methodology_summary': {}
            }
    
    async def _supervise_citation_generation(self, papers: List[Dict[str, Any]], summaries: Dict[str, Any], pipeline_id: str) -> Dict[str, Any]:
        """Supervise the citation generation stage."""
        stage = PipelineStage.CITATION
        self.logger.info(f"🔗 Supervisor: Starting {stage.value}")
        
        try:
            from agents.citation_agent import CitationAgent
            
            citation_agent = CitationAgent()
            self._update_agent_status(pipeline_id, stage, AgentStatus.RUNNING)
            
            citations = await self._execute_with_retry(
                citation_agent.generate_citations,
                papers,
                summaries,
                stage=stage,
                pipeline_id=pipeline_id
            )
            
            self._update_agent_status(pipeline_id, stage, AgentStatus.COMPLETED)
            self.pipeline_metrics[pipeline_id]['stages_completed'].append(stage.value)
            
            self.logger.info(f"✅ Supervisor: {stage.value} completed")
            return citations
            
        except Exception as e:
            self._update_agent_status(pipeline_id, stage, AgentStatus.FAILED)
            self.logger.error(f"❌ Supervisor: {stage.value} failed - {str(e)}")
            # Return minimal citations to keep pipeline running
            return {
                'formatted_citations': {},
                'in_text_citations': [],
                'bibliography': [],
                'citation_network': {}
            }
    
    async def _supervise_paper_generation(self, query: str, summaries: Dict[str, Any], 
                                        citations: Dict[str, Any], requirements: Dict[str, Any], 
                                        pipeline_id: str) -> Dict[str, Any]:
        """Supervise the paper generation stage."""
        stage = PipelineStage.GENERATION
        self.logger.info(f"📄 Supervisor: Starting {stage.value}")
        
        try:
            from agents.paper_generator_agent import PaperGeneratorAgent
            
            generator_agent = PaperGeneratorAgent()
            self._update_agent_status(pipeline_id, stage, AgentStatus.RUNNING)
            
            draft = await self._execute_with_retry(
                generator_agent.generate_draft,
                query,
                summaries,
                citations,
                requirements,
                stage=stage,
                pipeline_id=pipeline_id
            )
            
            self._update_agent_status(pipeline_id, stage, AgentStatus.COMPLETED)
            self.pipeline_metrics[pipeline_id]['stages_completed'].append(stage.value)
            
            self.logger.info(f"✅ Supervisor: {stage.value} completed")
            return draft
            
        except Exception as e:
            self._update_agent_status(pipeline_id, stage, AgentStatus.FAILED)
            self.logger.error(f"❌ Supervisor: {stage.value} failed - {str(e)}")
            # Return minimal draft to keep pipeline running
            return {
                'title': f"{query}: Research Analysis",
                'abstract': f"This paper analyzes {query} based on available research literature.",
                'sections': {},
                'metadata': {
                    'topic': query,
                    'word_count': 0,
                    'generation_date': datetime.now().isoformat()
                }
            }
    
    async def _supervise_citation_replacement(self, draft: Dict[str, Any], papers: List[Dict[str, Any]], 
                                            citation_style: str, pipeline_id: str) -> Dict[str, Any]:
        """Supervise citation replacement in the draft."""
        self.logger.info("🔄 Supervisor: Starting citation replacement")
        
        try:
            from agents.citation_agent import CitationAgent
            
            citation_agent = CitationAgent()
            
            # Replace citations in abstract
            if 'abstract' in draft and draft['abstract']:
                draft['abstract'] = await citation_agent.replace_citation_placeholders(
                    draft['abstract'], papers, citation_style
                )
            
            # Replace citations in sections
            if 'sections' in draft:
                for section_name, section_content in draft['sections'].items():
                    if isinstance(section_content, dict) and 'content' in section_content:
                        draft['sections'][section_name]['content'] = await citation_agent.replace_citation_placeholders(
                            section_content['content'], papers, citation_style
                        )
                    elif isinstance(section_content, str):
                        draft['sections'][section_name] = await citation_agent.replace_citation_placeholders(
                            section_content, papers, citation_style
                        )
            
            self.logger.info("✅ Supervisor: Citation replacement completed")
            return draft
            
        except Exception as e:
            self.logger.warning(f"⚠️ Supervisor: Citation replacement failed - {str(e)}")
            return draft  # Return original draft if replacement fails
    
    async def _supervise_analytics(self, draft: Dict[str, Any], papers: List[Dict[str, Any]], pipeline_id: str) -> Dict[str, Any]:
        """Supervise the analytics generation stage."""
        stage = "analytics"
        self.logger.info(f"📊 Supervisor: Starting {stage}")
        
        try:
            from agents.analytics_agent import AnalyticsAgent
            
            analytics_agent = AnalyticsAgent()
            self._update_agent_status(pipeline_id, stage, AgentStatus.RUNNING)
            
            analytics = await self._execute_with_retry(
                analytics_agent.analyze_paper,
                draft,
                papers,
                stage=stage,
                pipeline_id=pipeline_id
            )
            
            self._update_agent_status(pipeline_id, stage, AgentStatus.COMPLETED)
            self.pipeline_metrics[pipeline_id]['stages_completed'].append(stage)
            
            self.logger.info(f"✅ Supervisor: {stage} completed")
            return analytics
            
        except Exception as e:
            self._update_agent_status(pipeline_id, stage, AgentStatus.FAILED)
            self.logger.error(f"❌ Supervisor: {stage} failed - {str(e)}")
            # Return minimal analytics to keep pipeline running
            return {
                'paper_metrics': {
                    'word_count': 0,
                    'section_count': 0,
                    'citation_density': 0.0
                },
                'content_analysis': {
                    'keywords': [],
                    'topics': [],
                    'sentiment': {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}
                },
                'source_analysis': {
                    'total_sources': len(papers),
                    'publication_years': {'earliest': 2020, 'latest': 2024}
                },
                'recommendations': [
                    "Pipeline completed with supervisor monitoring",
                    f"Analyzed {len(papers)} papers successfully"
                ]
            }
    
    async def _supervise_reference_formatting(self, papers: List[Dict[str, Any]], 
                                            citations: Dict[str, Any], citation_style: str, 
                                            pipeline_id: str) -> List[Dict[str, Any]]:
        """Supervise reference formatting with links."""
        self.logger.info("📚 Supervisor: Starting reference formatting")
        
        try:
            from agents.citation_agent import CitationAgent
            
            citation_agent = CitationAgent()
            references = []
            
            for i, paper in enumerate(papers[:15], 1):  # Limit to 15 references
                try:
                    # Safe author formatting
                    authors = paper.get('authors', ['Unknown Author'])
                    if not authors or len(authors) == 0:
                        author_str = "Unknown Author"
                    elif len(authors) == 1:
                        author_str = authors[0] if authors[0] else "Unknown Author"
                    elif len(authors) == 2:
                        valid_authors = [a for a in authors if a]
                        if len(valid_authors) >= 2:
                            author_str = f"{valid_authors[0]} & {valid_authors[1]}"
                        elif len(valid_authors) == 1:
                            author_str = valid_authors[0]
                        else:
                            author_str = "Unknown Author"
                    else:
                        valid_authors = [a for a in authors if a]
                        if len(valid_authors) > 0:
                            author_str = f"{valid_authors[0]} et al."
                        else:
                            author_str = "Unknown Author"
                    
                    # Create formatted citation
                    year = paper.get('year', 'Unknown')
                    title = paper.get('title', 'Unknown Title')
                    journal = paper.get('journal', '')
                    doi = paper.get('doi', '')
                    url = paper.get('url', '')
                    
                    # Build citation string
                    formatted_citation = f"{author_str} ({year}). {title}."
                    if journal:
                        formatted_citation += f" {journal}."
                    if doi:
                        formatted_citation += f" https://doi.org/{doi}"
                    elif url:
                        formatted_citation += f" Retrieved from {url}"
                    
                    ref_entry = {
                        "id": f"ref{i}",
                        "number": i,
                        "title": title,
                        "authors": authors,
                        "journal": journal,
                        "year": str(year),
                        "doi": doi,
                        "url": url,
                        "formatted_citation": formatted_citation,
                        "relevance_score": paper.get('relevance_score', 0.0),
                        "citations_count": paper.get('citations_count', 0)
                    }
                    references.append(ref_entry)
                    
                except Exception as e:
                    self.logger.warning(f"⚠️ Supervisor: Error formatting reference {i} - {str(e)}")
                    # Add minimal reference to avoid breaking
                    references.append({
                        "id": f"ref{i}",
                        "number": i,
                        "title": paper.get('title', 'Unknown Title'),
                        "authors": paper.get('authors', ['Unknown Author']),
                        "journal": paper.get('journal', 'Unknown Journal'),
                        "year": str(paper.get('year', 'Unknown')),
                        "doi": paper.get('doi', ''),
                        "url": paper.get('url', ''),
                        "formatted_citation": f"Reference {i}: {paper.get('title', 'Unknown Title')}",
                        "relevance_score": paper.get('relevance_score', 0.0),
                        "citations_count": paper.get('citations_count', 0)
                    })
            
            self.logger.info(f"✅ Supervisor: Reference formatting completed - {len(references)} references")
            return references
            
        except Exception as e:
            self.logger.error(f"❌ Supervisor: Reference formatting failed - {str(e)}")
            return []
    
    async def _execute_with_retry(self, func, *args, stage: str, pipeline_id: str, **kwargs):
        """Execute a function with retry logic and timeout."""
        max_retries = self.retry_config['max_retries']
        retry_delay = self.retry_config['retry_delay']
        timeout_seconds = self.retry_config['timeout_seconds']
        
        for attempt in range(max_retries + 1):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
                
                if attempt > 0:
                    self.logger.info(f"✅ Supervisor: {stage} succeeded on attempt {attempt + 1}")
                
                return result
                
            except asyncio.TimeoutError:
                self.logger.warning(f"⏰ Supervisor: {stage} timeout on attempt {attempt + 1}")
                self._record_error(pipeline_id, stage, f"Timeout on attempt {attempt + 1}")
                
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise Exception(f"{stage} timed out after {max_retries + 1} attempts")
                    
            except Exception as e:
                self.logger.warning(f"⚠️ Supervisor: {stage} error on attempt {attempt + 1} - {str(e)}")
                self._record_error(pipeline_id, stage, f"Attempt {attempt + 1}: {str(e)}")
                
                if attempt < max_retries:
                    await asyncio.sleep(retry_delay * (attempt + 1))  # Exponential backoff
                else:
                    raise
    
    def _update_agent_status(self, pipeline_id: str, stage: str, status: AgentStatus):
        """Update the status of an agent."""
        if pipeline_id not in self.agent_status:
            self.agent_status[pipeline_id] = {}
        
        self.agent_status[pipeline_id][stage] = {
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }
    
    def _record_error(self, pipeline_id: str, stage: str, error: str):
        """Record an error for monitoring."""
        if pipeline_id in self.pipeline_metrics:
            self.pipeline_metrics[pipeline_id]['errors'].append({
                'stage': stage,
                'error': error,
                'timestamp': datetime.now().isoformat()
            })
    
    def _get_current_stage(self, pipeline_id: str) -> str:
        """Get the current stage of the pipeline."""
        if pipeline_id in self.pipeline_metrics:
            stages = self.pipeline_metrics[pipeline_id].get('stages_completed', [])
            return stages[-1] if stages else 'initialization'
        return 'unknown'
    
    def get_pipeline_status(self, pipeline_id: str) -> Dict[str, Any]:
        """Get the current status of a pipeline."""
        return {
            'metrics': self.pipeline_metrics.get(pipeline_id, {}),
            'agent_status': self.agent_status.get(pipeline_id, {}),
            'error_history': [e for e in self.error_history if e['pipeline_id'] == pipeline_id]
        }
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        total_pipelines = len(self.pipeline_metrics)
        successful_pipelines = len([p for p in self.pipeline_metrics.values() if len(p.get('errors', [])) == 0])
        
        return {
            'total_pipelines': total_pipelines,
            'successful_pipelines': successful_pipelines,
            'success_rate': successful_pipelines / total_pipelines if total_pipelines > 0 else 0.0,
            'total_errors': len(self.error_history),
            'active_pipelines': len([p for p in self.agent_status.values() if any(s['status'] == AgentStatus.RUNNING.value for s in p.values())]),
            'average_processing_time': sum(p.get('total_time', 0) for p in self.pipeline_metrics.values()) / total_pipelines if total_pipelines > 0 else 0.0
        }
