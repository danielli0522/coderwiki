"""
Document Formatting Service

Provides comprehensive document formatting capabilities including:
- Markdown processing and structure analysis
- Template application and variable substitution
- Code highlighting and syntax processing
- Table of contents generation
- Document export functionality
"""

import logging
import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import markdown
from markdown.extensions import tables, toc, fenced_code, codehilite
import jinja2

from app.services.template_service import TemplateService
from app.services.highlight_service import HighlightService
from app.services.export_service import ExportService
from app.services.preview_service import PreviewService
from app.utils.markdown_utils import MarkdownUtils
from app.utils.template_utils import TemplateUtils
from app.utils.code_utils import CodeUtils

logger = logging.getLogger(__name__)


@dataclass
class FormattingOptions:
    """Configuration options for document formatting."""
    template_id: str = 'technical'
    highlight_theme: str = 'github'
    include_toc: bool = True
    include_line_numbers: bool = True
    enable_code_copy: bool = True
    custom_css: Optional[str] = None
    custom_js: Optional[str] = None
    export_formats: List[str] = None
    
    def __post_init__(self):
        if self.export_formats is None:
            self.export_formats = ['html', 'markdown']


@dataclass
class FormattingResult:
    """Result of document formatting operation."""
    success: bool
    formatted_content: str
    table_of_contents: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    export_urls: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None


class DocumentFormatter:
    """Main document formatting service."""
    
    def __init__(self):
        """Initialize the document formatter with required services."""
        self.template_service = TemplateService()
        self.highlight_service = HighlightService()
        self.export_service = ExportService()
        self.preview_service = PreviewService()
        self.markdown_utils = MarkdownUtils()
        self.template_utils = TemplateUtils()
        self.code_utils = CodeUtils()
        
        # Initialize markdown extensions
        self.md = markdown.Markdown(extensions=[
            'tables',
            'toc',
            'fenced_code',
            'codehilite',
            'sane_lists',
            'extra'
        ])
        
        logger.info("DocumentFormatter initialized")
    
    def format_document(self, 
                       content: str, 
                       options: FormattingOptions,
                       variables: Optional[Dict[str, Any]] = None) -> FormattingResult:
        """
        Format a document with the given options.
        
        Args:
            content: The raw document content to format
            options: Formatting configuration options
            variables: Template variables for substitution
            
        Returns:
            FormattingResult with formatted content and metadata
        """
        try:
            logger.info(f"Starting document formatting with template: {options.template_id}")
            
            # Step 1: Apply template if specified
            if options.template_id:
                template_result = self._apply_template(content, options.template_id, variables)
                if not template_result.success:
                    return FormattingResult(
                        success=False,
                        formatted_content="",
                        error_message=template_result.error_message
                    )
                processed_content = template_result.processed_content
            else:
                processed_content = content
            
            # Step 2: Process markdown
            markdown_result = self._process_markdown(processed_content, options)
            if not markdown_result.success:
                return FormattingResult(
                    success=False,
                    formatted_content="",
                    error_message=markdown_result.error_message
                )
            
            formatted_content = markdown_result.formatted_content
            table_of_contents = markdown_result.table_of_contents
            
            # Step 3: Apply code highlighting
            highlighted_content = self._apply_code_highlighting(
                formatted_content, 
                options.highlight_theme,
                options.include_line_numbers,
                options.enable_code_copy
            )
            
            # Step 4: Generate table of contents if requested
            toc_html = None
            if options.include_toc and table_of_contents:
                toc_html = self._generate_table_of_contents(table_of_contents)
            
            # Step 5: Prepare final HTML structure
            final_content = self._create_document_structure(
                highlighted_content,
                toc_html,
                options
            )
            
            # Step 6: Prepare export formats
            export_urls = {}
            for format_type in options.export_formats:
                try:
                    export_url = self.export_service.export_document(
                        content=final_content,
                        format_type=format_type,
                        options=options
                    )
                    export_urls[format_type] = export_url
                except Exception as e:
                    logger.error(f"Failed to export to {format_type}: {e}")
            
            # Prepare metadata
            metadata = {
                'template_id': options.template_id,
                'highlight_theme': options.highlight_theme,
                'has_toc': options.include_toc,
                'word_count': len(content.split()),
                'code_blocks': self._count_code_blocks(content),
                'headings': self._extract_headings(content),
                'export_formats': options.export_formats
            }
            
            logger.info("Document formatting completed successfully")
            
            return FormattingResult(
                success=True,
                formatted_content=final_content,
                table_of_contents=toc_html,
                metadata=metadata,
                export_urls=export_urls if export_urls else None
            )
            
        except Exception as e:
            logger.error(f"Document formatting failed: {e}")
            return FormattingResult(
                success=False,
                formatted_content="",
                error_message=str(e)
            )
    
    def _apply_template(self, 
                        content: str, 
                        template_id: str,
                        variables: Optional[Dict[str, Any]] = None) -> Any:
        """Apply template to the content."""
        try:
            return self.template_service.apply_template(content, template_id, variables)
        except Exception as e:
            logger.error(f"Template application failed: {e}")
            return type('TemplateResult', (), {
                'success': False,
                'processed_content': content,
                'error_message': str(e)
            })()
    
    def _process_markdown(self, content: str, options: FormattingOptions) -> Any:
        """Process markdown content and extract structure."""
        try:
            # Extract table of contents before processing
            toc_data = self.markdown_utils.extract_table_of_contents(content)
            
            # Process markdown
            formatted_content = self.md.convert(content)
            
            # Extract structure information
            structure_info = self.markdown_utils.analyze_structure(content)
            
            return type('MarkdownResult', (), {
                'success': True,
                'formatted_content': formatted_content,
                'table_of_contents': toc_data,
                'structure_info': structure_info
            })()
            
        except Exception as e:
            logger.error(f"Markdown processing failed: {e}")
            return type('MarkdownResult', (), {
                'success': False,
                'formatted_content': '',
                'error_message': str(e)
            })()
    
    def _apply_code_highlighting(self, 
                                 content: str, 
                                 theme: str,
                                 include_line_numbers: bool,
                                 enable_copy: bool) -> str:
        """Apply syntax highlighting to code blocks."""
        try:
            return self.highlight_service.highlight_code_blocks(
                content,
                theme=theme,
                include_line_numbers=include_line_numbers,
                enable_copy=enable_copy
            )
        except Exception as e:
            logger.error(f"Code highlighting failed: {e}")
            return content
    
    def _generate_table_of_contents(self, toc_data: List[Dict[str, Any]]) -> str:
        """Generate HTML table of contents from extracted data."""
        if not toc_data:
            return ""
        
        toc_html = '<div class="table-of-contents">\n'
        toc_html += '<h3>目录</h3>\n'
        toc_html += '<nav class="toc-nav">\n'
        toc_html += '<ul class="toc-list">\n'
        
        current_level = 0
        for item in toc_data:
            level = item.get('level', 1)
            title = item.get('title', '')
            anchor = item.get('anchor', '')
            
            # Handle nested lists
            if level > current_level:
                toc_html += '<ul class="toc-sublist">\n'
                current_level = level
            elif level < current_level:
                toc_html += '</ul>\n' * (current_level - level)
                current_level = level
            
            toc_html += f'<li class="toc-item toc-level-{level}">\n'
            toc_html += f'<a href="#{anchor}" class="toc-link">{title}</a>\n'
            toc_html += '</li>\n'
        
        # Close remaining lists
        toc_html += '</ul>\n' * (current_level + 1)
        toc_html += '</nav>\n'
        toc_html += '</div>\n'
        
        return toc_html
    
    def _create_document_structure(self, 
                                 content: str, 
                                 toc_html: Optional[str],
                                 options: FormattingOptions) -> str:
        """Create the final HTML document structure."""
        html_parts = []
        
        # HTML header
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html lang="zh-CN">')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('<title>Formatted Document</title>')
        
        # CSS styles
        html_parts.append('<style>')
        html_parts.append(self._get_default_styles())
        if options.custom_css:
            html_parts.append(options.custom_css)
        html_parts.append('</style>')
        
        # JavaScript
        html_parts.append('<script>')
        html_parts.append(self._get_default_javascript())
        if options.custom_js:
            html_parts.append(options.custom_js)
        html_parts.append('</script>')
        
        html_parts.append('</head>')
        html_parts.append('<body>')
        
        # Document container
        html_parts.append('<div class="document-container">')
        
        # Table of contents
        if toc_html:
            html_parts.append('<div class="toc-sidebar">')
            html_parts.append(toc_html)
            html_parts.append('</div>')
        
        # Main content
        html_parts.append('<div class="document-content">')
        html_parts.append(content)
        html_parts.append('</div>')
        
        html_parts.append('</div>')
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def _get_default_styles(self) -> str:
        """Get default CSS styles for formatted documents."""
        return """
        .document-container {
            display: flex;
            max-width: 1200px;
            margin: 0 auto;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .toc-sidebar {
            width: 250px;
            padding: 20px;
            background: #f8f9fa;
            border-right: 1px solid #e9ecef;
            position: sticky;
            top: 0;
            height: 100vh;
            overflow-y: auto;
        }
        
        .document-content {
            flex: 1;
            padding: 40px;
            background: white;
        }
        
        .table-of-contents h3 {
            margin-top: 0;
            color: #495057;
            font-size: 16px;
            font-weight: 600;
        }
        
        .toc-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .toc-sublist {
            list-style: none;
            padding-left: 20px;
            margin: 5px 0;
        }
        
        .toc-item {
            margin: 5px 0;
        }
        
        .toc-link {
            color: #6c757d;
            text-decoration: none;
            font-size: 14px;
            display: block;
            padding: 5px 0;
            border-radius: 4px;
            transition: all 0.2s ease;
        }
        
        .toc-link:hover {
            color: #007bff;
            background: #e9ecef;
        }
        
        .toc-level-1 .toc-link {
            font-weight: 600;
        }
        
        .toc-level-2 .toc-link {
            padding-left: 10px;
        }
        
        .toc-level-3 .toc-link {
            padding-left: 20px;
        }
        
        @media (max-width: 768px) {
            .document-container {
                flex-direction: column;
            }
            
            .toc-sidebar {
                width: 100%;
                height: auto;
                position: relative;
                border-right: none;
                border-bottom: 1px solid #e9ecef;
            }
            
            .document-content {
                padding: 20px;
            }
        }
        """
    
    def _get_default_javascript(self) -> str:
        """Get default JavaScript for document functionality."""
        return """
        document.addEventListener('DOMContentLoaded', function() {
            // Smooth scrolling for TOC links
            document.querySelectorAll('.toc-link').forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href').substring(1);
                    const targetElement = document.getElementById(targetId);
                    if (targetElement) {
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
            
            // Highlight current section in TOC
            const sections = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
            const tocLinks = document.querySelectorAll('.toc-link');
            
            function updateActiveTocLink() {
                const scrollPosition = window.scrollY;
                
                sections.forEach((section, index) => {
                    const sectionTop = section.offsetTop - 100;
                    const sectionHeight = section.offsetHeight;
                    
                    if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
                        tocLinks.forEach(link => link.classList.remove('active'));
                        if (tocLinks[index]) {
                            tocLinks[index].classList.add('active');
                        }
                    }
                });
            }
            
            window.addEventListener('scroll', updateActiveTocLink);
            updateActiveTocLink();
        });
        """
    
    def _count_code_blocks(self, content: str) -> int:
        """Count the number of code blocks in the content."""
        return len(re.findall(r'```[\s\S]*?```', content))
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract heading information from content."""
        headings = []
        heading_pattern = r'^(#+)\s+(.+)$'
        
        for line in content.split('\n'):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                headings.append({
                    'level': level,
                    'title': title
                })
        
        return headings
    
    def validate_formatting_options(self, options: FormattingOptions) -> List[str]:
        """Validate formatting options and return list of errors."""
        errors = []
        
        # Validate template ID
        try:
            template = self.template_service.get_template(options.template_id)
            if not template:
                errors.append(f"Template '{options.template_id}' not found")
        except Exception as e:
            errors.append(f"Template validation failed: {e}")
        
        # Validate highlight theme
        valid_themes = self.highlight_service.get_available_themes()
        if options.highlight_theme not in valid_themes:
            errors.append(f"Highlight theme '{options.highlight_theme}' not available")
        
        # Validate export formats
        valid_formats = self.export_service.get_supported_formats()
        for format_type in options.export_formats:
            if format_type not in valid_formats:
                errors.append(f"Export format '{format_type}' not supported")
        
        return errors
    
    def get_formatting_capabilities(self) -> Dict[str, Any]:
        """Get information about formatting capabilities."""
        return {
            'templates': self.template_service.get_available_templates(),
            'highlight_themes': self.highlight_service.get_available_themes(),
            'export_formats': self.export_service.get_supported_formats(),
            'markdown_extensions': [
                'tables', 'toc', 'fenced_code', 'codehilite', 
                'sane_lists', 'extra'
            ],
            'features': {
                'table_of_contents': True,
                'code_highlighting': True,
                'template_support': True,
                'export_functionality': True,
                'responsive_design': True
            }
        }