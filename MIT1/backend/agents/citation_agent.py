"""
Citation agent for managing and generating proper citations for research papers.
"""

import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import re
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class CitationAgent:
    """Agent responsible for generating and managing citations."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.citation_styles = {
            'apa': self._format_apa,
            'mla': self._format_mla,
            'chicago': self._format_chicago,
            'ieee': self._format_ieee
        }
        self.citation_placeholder_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
    
    async def generate_citations(self, papers: List[Dict[str, Any]], summaries: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate citations for the provided papers.
        
        Args:
            papers: List of research papers
            summaries: Paper summaries
            
        Returns:
            Dictionary containing formatted citations
        """
        try:
            self.logger.info(f"Generating citations for {len(papers)} papers")
            
            citations = {
                'formatted_citations': await self._generate_formatted_citations(papers),
                'in_text_citations': await self._generate_in_text_citations(papers, summaries),
                'bibliography': await self._generate_bibliography(papers),
                'citation_network': await self._build_citation_network(papers)
            }
            
            self.logger.info("Citation generation completed successfully")
            return citations
            
        except Exception as e:
            self.logger.error(f"Error in citation generation: {str(e)}")
            return {'error': str(e)}
    
    async def replace_citation_placeholders(self, text: str, papers: List[Dict[str, Any]], 
                                          citation_style: str = 'apa') -> str:
        """
        Replace citation placeholders [1], [2], [3] with actual citations.
        
        Args:
            text: Text containing citation placeholders
            papers: List of papers to use for citations
            citation_style: Citation style (apa, mla, chicago, ieee)
            
        Returns:
            Text with placeholders replaced by citations
        """
        try:
            # Find all citation placeholders
            placeholders = re.findall(self.citation_placeholder_pattern, text)
            
            if not placeholders:
                return text
            
            # Replace placeholders with citations
            def replace_placeholder(match):
                placeholder_content = match.group(1)
                
                # Handle multiple citations like "1, 2, 3"
                citation_nums = [num.strip() for num in placeholder_content.split(',')]
                citation_texts = []
                
                for citation_num in citation_nums:
                    try:
                        placeholder_idx = int(citation_num) - 1  # Convert to 0-based index
                        
                        if placeholder_idx < len(papers):
                            paper = papers[placeholder_idx]
                            
                            # Generate in-text citation based on style
                            if citation_style == 'apa':
                                authors = paper.get('authors', ['Unknown'])
                                year = paper.get('year', 'n.d.')
                                if len(authors) == 1:
                                    citation_text = f"{authors[0].split()[-1] if authors[0] else 'Unknown'}, {year}"
                                elif len(authors) == 2:
                                    last_names = [a.split()[-1] if a else 'Unknown' for a in authors[:2]]
                                    citation_text = f"{' & '.join(last_names)}, {year}"
                                else:
                                    first_author = authors[0].split()[-1] if authors[0] else 'Unknown'
                                    citation_text = f"{first_author} et al., {year}"
                            
                            elif citation_style == 'mla':
                                authors = paper.get('authors', ['Unknown'])
                                if len(authors) >= 1:
                                    first_author = authors[0].split()[-1] if authors[0] else 'Unknown'
                                    citation_text = first_author
                                else:
                                    citation_text = "Unknown"
                            
                            elif citation_style == 'chicago':
                                authors = paper.get('authors', ['Unknown'])
                                year = paper.get('year', 'n.d.')
                                if len(authors) >= 1:
                                    first_author = authors[0].split()[-1] if authors[0] else 'Unknown'
                                    citation_text = f"{first_author} {year}"
                                else:
                                    citation_text = f"Unknown {year}"
                            
                            elif citation_style == 'ieee':
                                citation_text = citation_num
                            
                            else:
                                # Default to APA style
                                authors = paper.get('authors', ['Unknown'])
                                year = paper.get('year', 'n.d.')
                                first_author = authors[0].split()[-1] if authors and authors[0] else 'Unknown'
                                citation_text = f"{first_author}, {year}"
                            
                            citation_texts.append(citation_text)
                        else:
                            # If we don't have enough papers, keep the number
                            citation_texts.append(citation_num)
                    except (ValueError, IndexError):
                        citation_texts.append(citation_num)
                
                # Format the final citation
                if citation_style == 'ieee':
                    return f"[{', '.join(citation_texts)}]"
                else:
                    return f"({'; '.join(citation_texts)})"
            
            result_text = re.sub(self.citation_placeholder_pattern, replace_placeholder, text)
            
            return result_text
            
        except Exception as e:
            self.logger.error(f"Error replacing citation placeholders: {str(e)}")
            return text
    
    def _format_citation(self, paper: Dict[str, Any], style: str) -> str:
        """Format a single paper citation in the specified style."""
        if style in self.citation_styles:
            return self.citation_styles[style](paper)
        else:
            return self._format_apa(paper)  # Default to APA
    
    async def _generate_formatted_citations(self, papers: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Generate citations in multiple formats."""
        formatted_citations = {}
        
        for style_name, style_function in self.citation_styles.items():
            formatted_citations[style_name] = []
            
            for paper in papers:
                try:
                    citation = style_function(paper)
                    formatted_citations[style_name].append(citation)
                except Exception as e:
                    self.logger.error(f"Error formatting {style_name} citation: {str(e)}")
                    continue
        
        return formatted_citations
    
    async def _generate_in_text_citations(self, papers: List[Dict[str, Any]], summaries: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate in-text citations with context."""
        in_text_citations = []
        
        for paper in papers:
            try:
                # Find where this paper should be cited based on summaries
                citation_contexts = await self._find_citation_contexts(paper, summaries)
                
                for context in citation_contexts:
                    in_text_citations.append({
                        'paper_id': paper.get('id', ''),
                        'paper_title': paper.get('title', ''),
                        'context': context['context'],
                        'citation_text': context['citation_text'],
                        'relevance_score': context['relevance_score']
                    })
                    
            except Exception as e:
                self.logger.error(f"Error generating in-text citation: {str(e)}")
                continue
        
        return in_text_citations
    
    async def _generate_bibliography(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate a comprehensive bibliography."""
        bibliography = []
        
        for paper in papers:
            try:
                bib_entry = {
                    'id': paper.get('id', ''),
                    'title': paper.get('title', ''),
                    'authors': paper.get('authors', []),
                    'publication_date': paper.get('published_date', ''),
                    'journal': paper.get('journal', ''),
                    'volume': paper.get('volume', ''),
                    'issue': paper.get('issue', ''),
                    'pages': paper.get('pages', ''),
                    'doi': paper.get('doi', ''),
                    'url': paper.get('url', ''),
                    'abstract': paper.get('abstract', ''),
                    'keywords': paper.get('keywords', []),
                    'relevance_score': paper.get('relevance_score', 0.0)
                }
                
                bibliography.append(bib_entry)
                
            except Exception as e:
                self.logger.error(f"Error creating bibliography entry: {str(e)}")
                continue
        
        # Sort by relevance score
        bibliography.sort(key=lambda x: x['relevance_score'], reverse=True)
        
        return bibliography
    
    async def _build_citation_network(self, papers: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build a network of paper citations."""
        try:
            citation_network = {
                'nodes': [],
                'edges': [],
                'central_papers': [],
                'network_stats': {}
            }
            
            # Create nodes for each paper
            for paper in papers:
                node = {
                    'id': paper.get('id', ''),
                    'title': paper.get('title', ''),
                    'authors': paper.get('authors', []),
                    'year': paper.get('year', ''),
                    'relevance_score': paper.get('relevance_score', 0.0),
                    'citation_count': paper.get('citations_count', 0)
                }
                citation_network['nodes'].append(node)
            
            # Find connections between papers (simplified)
            edges = await self._find_paper_connections(papers)
            citation_network['edges'] = edges
            
            # Identify central papers
            citation_network['central_papers'] = await self._identify_central_papers(papers)
            
            # Calculate network statistics
            citation_network['network_stats'] = await self._calculate_network_stats(citation_network)
            
            return citation_network
            
        except Exception as e:
            self.logger.error(f"Error building citation network: {str(e)}")
            return {'error': str(e)}
    
    def _format_apa(self, paper: Dict[str, Any]) -> str:
        """Format citation in APA style."""
        authors = paper.get('authors', [])
        title = paper.get('title', '')
        journal = paper.get('journal', '')
        year = paper.get('year', '')
        volume = paper.get('volume', '')
        pages = paper.get('pages', '')
        doi = paper.get('doi', '')
        url = paper.get('url', '')
        
        # Format authors safely
        if not authors or len(authors) == 0:
            author_str = "Unknown Author"
        elif len(authors) == 1:
            author_str = authors[0] if authors[0] else "Unknown Author"
        elif len(authors) <= 7:
            valid_authors = [a for a in authors if a]  # Filter out empty authors
            if len(valid_authors) >= 2:
                author_str = ', '.join(valid_authors[:-1]) + ', & ' + valid_authors[-1]
            elif len(valid_authors) == 1:
                author_str = valid_authors[0]
            else:
                author_str = "Unknown Author"
        else:
            valid_authors = [a for a in authors if a]  # Filter out empty authors
            if len(valid_authors) >= 6:
                author_str = ', '.join(valid_authors[:6]) + ', ... ' + valid_authors[-1]
            elif len(valid_authors) > 0:
                author_str = ', '.join(valid_authors[:3]) + ' et al.'
            else:
                author_str = "Unknown Author"
        
        # Build citation
        citation = f"{author_str} ({year}). {title}. "
        
        if journal:
            citation += f"{journal}"
            if volume:
                citation += f", {volume}"
            if pages:
                citation += f", {pages}"
        
        # Add DOI or URL link
        if doi:
            citation += f". https://doi.org/{doi}"
        elif url:
            citation += f". Retrieved from {url}"
        
        return citation
    
    def _format_mla(self, paper: Dict[str, Any]) -> str:
        """Format citation in MLA style."""
        authors = paper.get('authors', [])
        title = paper.get('title', '')
        journal = paper.get('journal', '')
        year = paper.get('year', '')
        volume = paper.get('volume', '')
        pages = paper.get('pages', '')
        url = paper.get('url', '')
        
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = ', '.join(authors[:-1]) + ', and ' + authors[-1]
        
        # Build citation
        citation = f"{author_str}. \"{title}.\" "
        
        if journal:
            citation += f"{journal}"
            if volume:
                citation += f", vol. {volume}"
            if pages:
                citation += f", {year}, pp. {pages}"
            else:
                citation += f", {year}"
        
        # Add URL if available
        if url:
            citation += f". Web. {url}"
        
        return citation
    
    def _format_chicago(self, paper: Dict[str, Any]) -> str:
        """Format citation in Chicago style."""
        authors = paper.get('authors', [])
        title = paper.get('title', '')
        journal = paper.get('journal', '')
        year = paper.get('year', '')
        volume = paper.get('volume', '')
        pages = paper.get('pages', '')
        doi = paper.get('doi', '')
        url = paper.get('url', '')
        
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = ', '.join(authors[:-1]) + ', and ' + authors[-1]
        
        # Build citation
        citation = f"{author_str}. \"{title}.\" "
        
        if journal:
            citation += f"{journal}"
            if volume:
                citation += f" {volume}"
            if pages:
                citation += f", no. {paper.get('issue', '')} ({year}): {pages}"
            else:
                citation += f" ({year})"
        
        # Add DOI or URL link
        if doi:
            citation += f". https://doi.org/{doi}"
        elif url:
            citation += f". {url}"
        
        return citation
    
    def _format_ieee(self, paper: Dict[str, Any]) -> str:
        """Format citation in IEEE style."""
        authors = paper.get('authors', [])
        title = paper.get('title', '')
        journal = paper.get('journal', '')
        year = paper.get('year', '')
        volume = paper.get('volume', '')
        pages = paper.get('pages', '')
        doi = paper.get('doi', '')
        url = paper.get('url', '')
        
        # Format authors
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 6:
            author_str = ', '.join(authors)
        else:
            author_str = ', '.join(authors[:3]) + ' et al.'
        
        # Build citation
        citation = f"{author_str}, \"{title},\" "
        
        if journal:
            citation += f"{journal}"
            if volume:
                citation += f", vol. {volume}"
            if pages:
                citation += f", pp. {pages}"
            citation += f", {year}"
        
        # Add DOI or URL link
        if doi:
            citation += f", doi: {doi}"
        elif url:
            citation += f". [Online]. Available: {url}"
        
        return citation
    
    async def _find_citation_contexts(self, paper: Dict[str, Any], summaries: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find contexts where this paper should be cited."""
        contexts = []
        
        # Simple context matching based on keywords
        paper_keywords = paper.get('keywords', [])
        paper_title = paper.get('title', '').lower()
        
        # Check individual summaries for relevant contexts
        individual_summaries = summaries.get('individual_summaries', [])
        
        for summary in individual_summaries:
            if any(keyword.lower() in summary.get('summary', '').lower() for keyword in paper_keywords):
                contexts.append({
                    'context': summary.get('summary', ''),
                    'citation_text': f"({paper.get('authors', ['Unknown'])[0]}, {paper.get('year', '')})",
                    'relevance_score': 0.8
                })
        
        return contexts
    
    async def _find_paper_connections(self, papers: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Find connections between papers."""
        edges = []
        
        # Simple connection based on shared keywords
        for i, paper1 in enumerate(papers):
            for j, paper2 in enumerate(papers[i+1:], i+1):
                keywords1 = set(paper1.get('keywords', []))
                keywords2 = set(paper2.get('keywords', []))
                
                # If papers share significant keywords, create an edge
                if len(keywords1.intersection(keywords2)) >= 2:
                    edges.append({
                        'source': paper1.get('id', ''),
                        'target': paper2.get('id', ''),
                        'weight': len(keywords1.intersection(keywords2))
                    })
        
        return edges
    
    async def _identify_central_papers(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify central papers in the citation network."""
        # Sort by relevance score and citation count
        central_papers = sorted(
            papers,
            key=lambda x: (x.get('relevance_score', 0.0), x.get('citations_count', 0)),
            reverse=True
        )
        
        return central_papers[:5]  # Top 5 central papers
    
    async def _calculate_network_stats(self, citation_network: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate network statistics."""
        nodes = citation_network.get('nodes', [])
        edges = citation_network.get('edges', [])
        
        stats = {
            'total_papers': len(nodes),
            'total_connections': len(edges),
            'average_connections_per_paper': len(edges) / len(nodes) if nodes else 0,
            'most_connected_paper': '',
            'network_density': 0.0
        }
        
        if nodes:
            # Find most connected paper
            connection_counts = {}
            for edge in edges:
                source = edge.get('source', '')
                target = edge.get('target', '')
                connection_counts[source] = connection_counts.get(source, 0) + 1
                connection_counts[target] = connection_counts.get(target, 0) + 1
            
            if connection_counts:
                most_connected_id = max(connection_counts, key=connection_counts.get)
                most_connected_paper = next(
                    (node for node in nodes if node['id'] == most_connected_id),
                    {}
                )
                stats['most_connected_paper'] = most_connected_paper.get('title', '')
            
            # Calculate network density
            max_possible_edges = len(nodes) * (len(nodes) - 1) / 2
            stats['network_density'] = len(edges) / max_possible_edges if max_possible_edges > 0 else 0
        
        return stats
