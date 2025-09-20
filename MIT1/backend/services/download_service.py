"""
Download service for generating research papers in multiple formats.
Supports PDF, DOCX, TXT, JSON, and BibTeX formats.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime
import tempfile
import os

class DownloadService:
    """Service for generating downloadable research papers in multiple formats."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.supported_formats = ['pdf', 'docx', 'txt', 'json', 'bibtex', 'markdown']
    
    def _make_citations_clickable(self, text: str, references: list, format_type: str = 'markdown') -> str:
        """Make citations clickable with reference links."""
        import re
        
        # Pattern to match citations like [1], [2], [1, 2, 3], etc.
        citation_pattern = r'\[(\d+(?:,\s*\d+)*)\]'
        
        def replace_citation(match):
            numbers = match.group(1)
            citation_numbers = [n.strip() for n in numbers.split(',')]
            
            if format_type == 'markdown':
                links = []
                for num in citation_numbers:
                    ref_index = int(num) - 1
                    if ref_index < len(references):
                        reference = references[ref_index]
                        url = reference.get('url', '')
                        title = reference.get('title', f'Reference {num}')
                        if url:
                            links.append(f"[{num}]({url} \"{title}\")")
                        else:
                            links.append(f"[{num}]")
                    else:
                        links.append(f"[{num}]")
                return ', '.join(links)
            elif format_type == 'pdf':
                links = []
                for num in citation_numbers:
                    ref_index = int(num) - 1
                    if ref_index < len(references):
                        reference = references[ref_index]
                        url = reference.get('url', '')
                        title = reference.get('title', f'Reference {num}')
                        if url:
                            links.append(f'<link href="{url}" color="blue">[{num}]</link>')
                        else:
                            links.append(f"[{num}]")
                    else:
                        links.append(f"[{num}]")
                return ', '.join(links)
            else:
                # For other formats, keep original
                return match.group(0)
        
        return re.sub(citation_pattern, replace_citation, text)
    
    async def generate_download(self, research_data: Dict[str, Any], format_type: str) -> Dict[str, Any]:
        """
        Generate downloadable content in the specified format.
        
        Args:
            research_data: Complete research data including draft, references, etc.
            format_type: Format to generate (pdf, docx, txt, json, bibtex, markdown)
            
        Returns:
            Dictionary with download content and metadata
        """
        try:
            self.logger.info(f"Generating download in {format_type} format")
            
            if format_type not in self.supported_formats:
                raise ValueError(f"Unsupported format: {format_type}")
            
            # Route to appropriate formatter
            if format_type == 'pdf':
                return await self._generate_pdf(research_data)
            elif format_type == 'docx':
                return await self._generate_docx(research_data)
            elif format_type == 'txt':
                return await self._generate_txt(research_data)
            elif format_type == 'json':
                return await self._generate_json(research_data)
            elif format_type == 'bibtex':
                return await self._generate_bibtex(research_data)
            elif format_type == 'markdown':
                return await self._generate_markdown(research_data)
            else:
                raise ValueError(f"Format {format_type} not implemented")
                
        except Exception as e:
            self.logger.error(f"Error generating {format_type} download: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_txt(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate plain text format."""
        try:
            draft = research_data.get('draft', {})
            references = research_data.get('references', [])
            
            content_parts = []
            
            # Title
            title = draft.get('title', 'Research Paper')
            content_parts.append(f"{title}\n{'=' * len(title)}\n")
            
            # Abstract
            if draft.get('abstract'):
                content_parts.append(f"ABSTRACT\n--------\n{draft['abstract']}\n")
            
            # Sections
            if draft.get('sections'):
                for section_name, section_content in draft['sections'].items():
                    section_title = section_name.replace('_', ' ').title()
                    content_parts.append(f"{section_title.upper()}\n{'-' * len(section_title)}")
                    
                    if isinstance(section_content, dict) and 'content' in section_content:
                        content_parts.append(f"{section_content['content']}\n")
                    elif isinstance(section_content, str):
                        content_parts.append(f"{section_content}\n")
            
            # References
            if references:
                content_parts.append("REFERENCES\n----------")
                for i, ref in enumerate(references, 1):
                    formatted_citation = ref.get('formatted_citation', '')
                    if formatted_citation:
                        content_parts.append(f"[{i}] {formatted_citation}")
                    else:
                        authors = ', '.join(ref.get('authors', ['Unknown']))
                        title = ref.get('title', 'Unknown Title')
                        year = ref.get('year', 'Unknown')
                        content_parts.append(f"[{i}] {authors} ({year}). {title}.")
            
            # Metadata
            metadata = draft.get('metadata', {})
            if metadata:
                content_parts.append(f"\nGenerated on: {metadata.get('generation_date', datetime.now().isoformat())}")
                content_parts.append(f"Topic: {metadata.get('topic', 'Unknown')}")
                content_parts.append(f"Word count: {metadata.get('word_count', 0)}")
            
            content = '\n\n'.join(content_parts)
            
            return {
                'content': content,
                'filename': f"{title.replace(' ', '_')}.txt",
                'mime_type': 'text/plain',
                'size': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            self.logger.error(f"Error generating TXT: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_json(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate JSON format with complete data."""
        try:
            # Create comprehensive JSON export
            export_data = {
                'metadata': {
                    'export_date': datetime.now().isoformat(),
                    'format': 'json',
                    'version': '1.0'
                },
                'research_data': research_data
            }
            
            content = json.dumps(export_data, indent=2, ensure_ascii=False)
            title = research_data.get('draft', {}).get('title', 'Research Paper')
            
            return {
                'content': content,
                'filename': f"{title.replace(' ', '_')}_complete.json",
                'mime_type': 'application/json',
                'size': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            self.logger.error(f"Error generating JSON: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_markdown(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Markdown format."""
        try:
            draft = research_data.get('draft', {})
            references = research_data.get('references', [])
            
            content_parts = []
            
            # Title
            title = draft.get('title', 'Research Paper')
            content_parts.append(f"# {title}\n")
            
            # Abstract
            if draft.get('abstract'):
                abstract_with_links = self._make_citations_clickable(draft['abstract'], references, 'markdown')
                content_parts.append(f"## Abstract\n\n{abstract_with_links}\n")
            
            # Sections
            if draft.get('sections'):
                for section_name, section_content in draft['sections'].items():
                    section_title = section_name.replace('_', ' ').title()
                    content_parts.append(f"## {section_title}")
                    
                    if isinstance(section_content, dict) and 'content' in section_content:
                        content_with_links = self._make_citations_clickable(section_content['content'], references, 'markdown')
                        content_parts.append(f"{content_with_links}\n")
                    elif isinstance(section_content, str):
                        content_with_links = self._make_citations_clickable(section_content, references, 'markdown')
                        content_parts.append(f"{content_with_links}\n")
            
            # References
            if references:
                content_parts.append("## References\n")
                for i, ref in enumerate(references, 1):
                    formatted_citation = ref.get('formatted_citation', '')
                    url = ref.get('url', '')
                    
                    if formatted_citation and url:
                        # Make citations clickable in markdown
                        content_parts.append(f"{i}. [{formatted_citation}]({url})")
                    elif formatted_citation:
                        content_parts.append(f"{i}. {formatted_citation}")
                    else:
                        authors = ', '.join(ref.get('authors', ['Unknown']))
                        title = ref.get('title', 'Unknown Title')
                        year = ref.get('year', 'Unknown')
                        if url:
                            content_parts.append(f"{i}. [{authors} ({year}). {title}.]({url})")
                        else:
                            content_parts.append(f"{i}. {authors} ({year}). {title}.")
            
            content = '\n\n'.join(content_parts)
            
            return {
                'content': content,
                'filename': f"{title.replace(' ', '_')}.md",
                'mime_type': 'text/markdown',
                'size': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            self.logger.error(f"Error generating Markdown: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_bibtex(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate BibTeX format for references."""
        try:
            references = research_data.get('references', [])
            
            if not references:
                return {'error': 'No references available for BibTeX export'}
            
            bibtex_entries = []
            
            for i, ref in enumerate(references, 1):
                # Create BibTeX entry
                title = ref.get('title', 'Unknown Title').replace('{', '').replace('}', '')
                authors = ref.get('authors', ['Unknown'])
                year = ref.get('year', 'Unknown')
                journal = ref.get('journal', '')
                url = ref.get('url', '')
                doi = ref.get('doi', '')
                
                # Format authors for BibTeX
                if len(authors) > 0:
                    author_str = ' and '.join(authors)
                else:
                    author_str = 'Unknown'
                
                # Create entry key
                first_author = authors[0].split()[-1] if authors and authors[0] else 'Unknown'
                entry_key = f"{first_author}{year}_{i}"
                
                # Build BibTeX entry
                entry_lines = [f"@article{{{entry_key},"]
                entry_lines.append(f"  title={{{title}}},")
                entry_lines.append(f"  author={{{author_str}}},")
                entry_lines.append(f"  year={{{year}}},")
                
                if journal:
                    entry_lines.append(f"  journal={{{journal}}},")
                if doi:
                    entry_lines.append(f"  doi={{{doi}}},")
                if url:
                    entry_lines.append(f"  url={{{url}}},")
                
                entry_lines.append("}")
                
                bibtex_entries.append('\n'.join(entry_lines))
            
            content = '\n\n'.join(bibtex_entries)
            title = research_data.get('draft', {}).get('title', 'Research Paper')
            
            return {
                'content': content,
                'filename': f"{title.replace(' ', '_')}_references.bib",
                'mime_type': 'application/x-bibtex',
                'size': len(content.encode('utf-8'))
            }
            
        except Exception as e:
            self.logger.error(f"Error generating BibTeX: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_pdf(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate PDF format using reportlab."""
        try:
            # Try to import reportlab
            try:
                from reportlab.lib.pagesizes import letter, A4
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                from reportlab.lib.colors import blue, black
                import io
                
                self.logger.info("Using reportlab for PDF generation")
                
                draft = research_data.get('draft', {})
                references = research_data.get('references', [])
                
                # Create a PDF buffer
                buffer = io.BytesIO()
                
                # Create the PDF document
                doc = SimpleDocTemplate(buffer, pagesize=A4, 
                                      rightMargin=72, leftMargin=72,
                                      topMargin=72, bottomMargin=18)
                
                # Get styles
                styles = getSampleStyleSheet()
                
                # Academic paper styles
                title_style = ParagraphStyle(
                    'PaperTitle',
                    parent=styles['Title'],
                    fontSize=20,
                    spaceAfter=24,
                    spaceBefore=36,
                    alignment=1,  # Center alignment
                    textColor=black,
                    fontName='Helvetica-Bold'
                )
                
                author_style = ParagraphStyle(
                    'AuthorStyle',
                    parent=styles['Normal'],
                    fontSize=12,
                    spaceAfter=6,
                    alignment=1,  # Center alignment
                    textColor=black,
                    fontName='Helvetica'
                )
                
                affiliation_style = ParagraphStyle(
                    'AffiliationStyle',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=24,
                    alignment=1,  # Center alignment
                    textColor=black,
                    fontName='Helvetica',
                    fontStyle='italic'
                )
                
                abstract_title_style = ParagraphStyle(
                    'AbstractTitle',
                    parent=styles['Heading2'],
                    fontSize=12,
                    spaceAfter=6,
                    spaceBefore=18,
                    textColor=black,
                    fontName='Helvetica-Bold',
                    alignment=1  # Center alignment
                )
                
                heading_style = ParagraphStyle(
                    'SectionHeading',
                    parent=styles['Heading2'],
                    fontSize=12,
                    spaceAfter=8,
                    spaceBefore=16,
                    textColor=black,
                    fontName='Helvetica-Bold',
                    leftIndent=0
                )
                
                subheading_style = ParagraphStyle(
                    'SubHeading',
                    parent=styles['Heading3'],
                    fontSize=11,
                    spaceAfter=6,
                    spaceBefore=12,
                    textColor=black,
                    fontName='Helvetica-Bold',
                    leftIndent=0
                )
                
                body_style = ParagraphStyle(
                    'BodyText',
                    parent=styles['Normal'],
                    fontSize=10,
                    spaceAfter=6,
                    leading=12,
                    textColor=black,
                    fontName='Times-Roman',
                    alignment=0,  # Left alignment
                    firstLineIndent=0
                )
                
                citation_style = ParagraphStyle(
                    'CitationText',
                    parent=styles['Normal'],
                    fontSize=9,
                    spaceAfter=4,
                    leading=11,
                    textColor=black,
                    fontName='Times-Roman',
                    leftIndent=18,
                    bulletIndent=6
                )
                
                # Story (content) list
                story = []
                
                # Title
                title = draft.get('title', 'Research Paper')
                story.append(Paragraph(title, title_style))
                story.append(Spacer(1, 12))
                
                # Author and affiliation
                story.append(Paragraph("MIT AI Lab", author_style))
                story.append(Paragraph("Massachusetts Institute of Technology", affiliation_style))
                story.append(Spacer(1, 18))
                
                # Abstract
                if draft.get('abstract'):
                    story.append(Paragraph("ABSTRACT", abstract_title_style))
                    story.append(Spacer(1, 6))
                    abstract_with_links = self._make_citations_clickable(draft['abstract'], references, 'pdf')
                    story.append(Paragraph(abstract_with_links, body_style))
                    story.append(Spacer(1, 18))
                
                # Keywords (if available)
                story.append(Paragraph("<b>Keywords:</b> " + title.replace(' ', ', ').lower() + ", research, analysis", body_style))
                story.append(Spacer(1, 24))
                
                # Sections with academic numbering
                if draft.get('sections'):
                    section_counter = 1
                    section_order = ['introduction', 'literature_review', 'methodology', 'results', 'discussion', 'conclusion']
                    
                    # First, process sections in academic order
                    processed_sections = set()
                    
                    for ordered_section in section_order:
                        if ordered_section in draft['sections']:
                            section_content = draft['sections'][ordered_section]
                            section_title = ordered_section.replace('_', ' ').title()
                            
                            # Add section number and title
                            story.append(Paragraph(f"{section_counter}. {section_title.upper()}", heading_style))
                            story.append(Spacer(1, 8))
                            
                            if isinstance(section_content, dict) and 'content' in section_content:
                                content_with_links = self._make_citations_clickable(section_content['content'], references, 'pdf')
                            elif isinstance(section_content, str):
                                content_with_links = self._make_citations_clickable(section_content, references, 'pdf')
                            else:
                                content_with_links = str(section_content)
                            
                            # Split content into paragraphs and format properly
                            paragraphs = content_with_links.split('\n\n')
                            for para in paragraphs:
                                if para.strip():
                                    # Add proper paragraph spacing for academic format
                                    story.append(Paragraph(para.strip(), body_style))
                                    story.append(Spacer(1, 6))
                            
                            story.append(Spacer(1, 12))
                            section_counter += 1
                            processed_sections.add(ordered_section)
                    
                    # Then process any remaining sections
                    for section_name, section_content in draft['sections'].items():
                        if section_name not in processed_sections:
                            section_title = section_name.replace('_', ' ').title()
                            story.append(Paragraph(f"{section_counter}. {section_title.upper()}", heading_style))
                            story.append(Spacer(1, 8))
                            
                            if isinstance(section_content, dict) and 'content' in section_content:
                                content_with_links = self._make_citations_clickable(section_content['content'], references, 'pdf')
                            elif isinstance(section_content, str):
                                content_with_links = self._make_citations_clickable(section_content, references, 'pdf')
                            else:
                                content_with_links = str(section_content)
                            
                            paragraphs = content_with_links.split('\n\n')
                            for para in paragraphs:
                                if para.strip():
                                    story.append(Paragraph(para.strip(), body_style))
                                    story.append(Spacer(1, 6))
                            
                            story.append(Spacer(1, 12))
                            section_counter += 1
                
                # References section
                if references:
                    story.append(PageBreak())
                    story.append(Paragraph("REFERENCES", heading_style))
                    story.append(Spacer(1, 12))
                    
                    for i, ref in enumerate(references, 1):
                        formatted_citation = ref.get('formatted_citation', f"Reference {i}")
                        
                        # Make URLs clickable in PDF with proper formatting
                        if ref.get('url'):
                            formatted_citation = formatted_citation.replace(
                                ref['url'], 
                                f'<link href="{ref["url"]}" color="blue"><u>{ref["url"]}</u></link>'
                            )
                        
                        # Format citation with hanging indent (academic style)
                        citation_text = f"[{i}] {formatted_citation}"
                        story.append(Paragraph(citation_text, citation_style))
                        story.append(Spacer(1, 4))
                
                # Add footer with generation info
                story.append(Spacer(1, 24))
                from datetime import datetime
                footer_text = f"Generated on {datetime.now().strftime('%B %d, %Y')} by MIT AI Research Platform"
                footer_style = ParagraphStyle(
                    'Footer',
                    parent=styles['Normal'],
                    fontSize=8,
                    textColor=black,
                    fontName='Helvetica',
                    alignment=1,  # Center
                    spaceAfter=12
                )
                story.append(Paragraph(footer_text, footer_style))
                
                # Build the PDF
                doc.build(story)
                
                # Get the PDF content
                pdf_content = buffer.getvalue()
                buffer.close()
                
                title_clean = title.replace(' ', '_').replace('/', '_').replace('\\', '_')
                
                return {
                    'content': pdf_content,
                    'filename': f"{title_clean}.pdf",
                    'mime_type': 'application/pdf',
                    'size': len(pdf_content),
                    'is_binary': True
                }
                
            except ImportError:
                self.logger.warning("reportlab not available, falling back to text format")
                # Fallback to text format
                content = await self._generate_txt(research_data)
                
                return {
                    'content': content['content'],
                    'filename': f"{research_data.get('draft', {}).get('title', 'Research Paper').replace(' ', '_')}.txt",
                    'mime_type': 'text/plain',
                    'size': content['size'],
                    'note': 'PDF generation requires reportlab library. Providing text format as fallback.'
                }
                
        except Exception as e:
            self.logger.error(f"Error generating PDF: {str(e)}")
            return {'error': str(e)}
    
    async def _generate_docx(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate DOCX format (requires additional libraries)."""
        try:
            # For now, return instructions for DOCX generation
            # In production, you would use python-docx library
            
            content = await self._generate_markdown(research_data)
            
            return {
                'content': content['content'],
                'filename': f"{research_data.get('draft', {}).get('title', 'Research Paper').replace(' ', '_')}.md",
                'mime_type': 'text/markdown',
                'size': content['size'],
                'note': 'DOCX generation requires additional libraries. Providing Markdown format as fallback.'
            }
            
        except Exception as e:
            self.logger.error(f"Error generating DOCX: {str(e)}")
            return {'error': str(e)}
    
    def get_supported_formats(self) -> List[Dict[str, str]]:
        """Get list of supported download formats."""
        return [
            {
                'format': 'txt',
                'name': 'Plain Text',
                'description': 'Simple text format, universally readable',
                'mime_type': 'text/plain',
                'extension': '.txt'
            },
            {
                'format': 'markdown',
                'name': 'Markdown',
                'description': 'Formatted text with clickable links',
                'mime_type': 'text/markdown',
                'extension': '.md'
            },
            {
                'format': 'json',
                'name': 'JSON Data',
                'description': 'Complete structured data export',
                'mime_type': 'application/json',
                'extension': '.json'
            },
            {
                'format': 'bibtex',
                'name': 'BibTeX References',
                'description': 'Citation format for LaTeX and reference managers',
                'mime_type': 'application/x-bibtex',
                'extension': '.bib'
            },
            {
                'format': 'pdf',
                'name': 'PDF Document',
                'description': 'Portable document format (requires additional setup)',
                'mime_type': 'application/pdf',
                'extension': '.pdf'
            },
            {
                'format': 'docx',
                'name': 'Word Document',
                'description': 'Microsoft Word format (requires additional setup)',
                'mime_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'extension': '.docx'
            }
        ]
