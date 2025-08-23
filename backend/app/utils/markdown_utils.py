"""
Markdown Utilities

Provides comprehensive markdown processing capabilities including:
- Standard markdown parsing and conversion
- Extended syntax support (tables, math formulas, etc.)
- Structure analysis and extraction
- Table of contents generation
- Content validation and optimization
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import markdown
from markdown.extensions import tables, toc, fenced_code, codehilite, sane_lists, extra
import html

logger = logging.getLogger(__name__)


@dataclass
class MarkdownStructure:
    """Represents the structure of a markdown document."""
    headings: List[Dict[str, Any]]
    code_blocks: List[Dict[str, Any]]
    links: List[Dict[str, str]]
    images: List[Dict[str, str]]
    tables: List[Dict[str, Any]]
    lists: List[Dict[str, Any]]
    metadata: Dict[str, Any]


@dataclass
class TocItem:
    """Represents an item in the table of contents."""
    level: int
    title: str
    anchor: str
    children: List['TocItem']


class MarkdownUtils:
    """Utility class for markdown processing and analysis."""
    
    def __init__(self):
        """Initialize markdown processor with extensions."""
        self.md = markdown.Markdown(extensions=[
            'tables',
            'toc',
            'fenced_code',
            'codehilite',
            'sane_lists',
            'extra'
        ])
        logger.info("MarkdownUtils initialized")
    
    def convert_to_html(self, content: str) -> str:
        """Convert markdown content to HTML."""
        try:
            return self.md.convert(content)
        except Exception as e:
            logger.error(f"Markdown to HTML conversion failed: {e}")
            return content
    
    def extract_table_of_contents(self, content: str) -> List[Dict[str, Any]]:
        """Extract table of contents data from markdown content."""
        toc_items = []
        heading_pattern = r'^(#+)\s+(.+)$'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                
                # Generate anchor from title
                anchor = self._generate_anchor(title)
                
                toc_items.append({
                    'level': level,
                    'title': title,
                    'anchor': anchor,
                    'line_number': line_num
                })
        
        return toc_items
    
    def analyze_structure(self, content: str) -> MarkdownStructure:
        """Analyze the structure of markdown content."""
        headings = self._extract_headings(content)
        code_blocks = self._extract_code_blocks(content)
        links = self._extract_links(content)
        images = self._extract_images(content)
        tables = self._extract_tables(content)
        lists = self._extract_lists(content)
        metadata = self._extract_metadata(content)
        
        return MarkdownStructure(
            headings=headings,
            code_blocks=code_blocks,
            links=links,
            images=images,
            tables=tables,
            lists=lists,
            metadata=metadata
        )
    
    def optimize_markdown(self, content: str) -> str:
        """Optimize markdown content for better readability and performance."""
        # Normalize line endings
        content = content.replace('\r\n', '\n')
        
        # Remove excessive blank lines
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Ensure consistent heading spacing
        content = re.sub(r'^(#+)\s*([^\n]*)$', r'\1 \2', content, flags=re.MULTILINE)
        
        # Optimize code block formatting
        content = re.sub(r'```(\w+)\s*\n', r'```\1\n', content)
        content = re.sub(r'\n\s*```', r'\n```', content)
        
        # Fix common markdown syntax issues
        content = self._fix_common_issues(content)
        
        return content.strip()
    
    def validate_markdown(self, content: str) -> Dict[str, Any]:
        """Validate markdown content and return validation results."""
        issues = []
        warnings = []
        suggestions = []
        
        # Check for unbalanced brackets
        if content.count('[') != content.count(']'):
            issues.append("Unbalanced brackets detected")
        
        # Check for unbalanced parentheses
        if content.count('(') != content.count(')'):
            issues.append("Unbalanced parentheses detected")
        
        # Check for heading hierarchy
        heading_levels = self._extract_heading_levels(content)
        if heading_levels and self._has_heading_hierarchy_issues(heading_levels):
            warnings.append("Heading hierarchy may have skips (e.g., H1 to H3)")
        
        # Check for broken links
        broken_links = self._find_broken_links(content)
        if broken_links:
            issues.extend([f"Broken link: {link}" for link in broken_links])
        
        # Check for very long lines
        long_lines = self._find_long_lines(content)
        if long_lines:
            suggestions.append(f"Consider wrapping {len(long_lines)} long lines for better readability")
        
        # Check for missing alt text
        missing_alt = self._find_missing_alt_text(content)
        if missing_alt:
            warnings.extend([f"Image missing alt text: {img}" for img in missing_alt])
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings,
            'suggestions': suggestions,
            'statistics': self._generate_statistics(content)
        }
    
    def extract_front_matter(self, content: str) -> Dict[str, Any]:
        """Extract front matter from markdown content."""
        front_matter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.search(front_matter_pattern, content, re.DOTALL)
        
        if match:
            front_matter_content = match.group(1)
            return self._parse_yaml_front_matter(front_matter_content)
        
        return {}
    
    def add_front_matter(self, content: str, metadata: Dict[str, Any]) -> str:
        """Add front matter to markdown content."""
        front_matter = self._generate_yaml_front_matter(metadata)
        
        # Remove existing front matter if present
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        return f"---\n{front_matter}\n---\n\n{content}"
    
    def generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a summary of the markdown content."""
        # Remove front matter
        content = re.sub(r'^---\s*\n.*?\n---\s*\n', '', content, flags=re.DOTALL)
        
        # Extract first paragraph or heading
        lines = content.strip().split('\n')
        summary_lines = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                summary_lines.append(line)
                if len(' '.join(summary_lines)) >= max_length:
                    break
            elif line.startswith('#') and not summary_lines:
                # Use first heading as summary
                return re.sub(r'^#+\s*', '', line)
        
        summary = ' '.join(summary_lines)
        if len(summary) > max_length:
            summary = summary[:max_length-3] + '...'
        
        return summary
    
    def _generate_anchor(self, title: str) -> str:
        """Generate URL-friendly anchor from title."""
        # Remove special characters and convert to lowercase
        anchor = re.sub(r'[^\w\s-]', '', title.lower())
        # Replace spaces with hyphens
        anchor = re.sub(r'\s+', '-', anchor)
        # Remove consecutive hyphens
        anchor = re.sub(r'-+', '-', anchor)
        # Remove leading/trailing hyphens
        anchor = anchor.strip('-')
        
        return anchor
    
    def _extract_headings(self, content: str) -> List[Dict[str, Any]]:
        """Extract heading information from content."""
        headings = []
        heading_pattern = r'^(#+)\s+(.+)$'
        
        for line_num, line in enumerate(content.split('\n'), 1):
            match = re.match(heading_pattern, line)
            if match:
                level = len(match.group(1))
                title = match.group(2).strip()
                anchor = self._generate_anchor(title)
                
                headings.append({
                    'level': level,
                    'title': title,
                    'anchor': anchor,
                    'line_number': line_num
                })
        
        return headings
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, Any]]:
        """Extract code blocks from content."""
        code_blocks = []
        code_block_pattern = r'```(\w*)\s*\n(.*?)\n```'
        
        for match in re.finditer(code_block_pattern, content, re.DOTALL):
            language = match.group(1) or 'text'
            code_content = match.group(2)
            
            code_blocks.append({
                'language': language,
                'content': code_content,
                'line_count': len(code_content.split('\n'))
            })
        
        return code_blocks
    
    def _extract_links(self, content: str) -> List[Dict[str, str]]:
        """Extract links from content."""
        links = []
        link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            text = match.group(1)
            url = match.group(2)
            
            links.append({
                'text': text,
                'url': url
            })
        
        return links
    
    def _extract_images(self, content: str) -> List[Dict[str, str]]:
        """Extract images from content."""
        images = []
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        for match in re.finditer(image_pattern, content):
            alt_text = match.group(1)
            url = match.group(2)
            
            images.append({
                'alt_text': alt_text,
                'url': url
            })
        
        return images
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """Extract tables from content."""
        tables = []
        table_pattern = r'\|(.+)\|\s*\n\|[\s\|-]+\|\s*\n((?:\|.*\|\s*\n)+)'
        
        for match in re.finditer(table_pattern, content):
            header_row = match.group(1)
            table_body = match.group(2)
            
            # Parse header
            headers = [cell.strip() for cell in header_row.split('|') if cell.strip()]
            
            # Parse body rows
            rows = []
            for line in table_body.strip().split('\n'):
                if line.strip():
                    cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                    rows.append(cells)
            
            tables.append({
                'headers': headers,
                'rows': rows,
                'row_count': len(rows)
            })
        
        return tables
    
    def _extract_lists(self, content: str) -> List[Dict[str, Any]]:
        """Extract lists from content."""
        lists = []
        # This is a simplified implementation
        # In a real implementation, you'd want more sophisticated list parsing
        list_pattern = r'^([*\-\+]\s+.+)(?:\n([*\-\+]\s+.+))*'
        
        for match in re.finditer(list_pattern, content, re.MULTILINE):
            list_content = match.group(0)
            items = [line.strip()[2:] for line in list_content.split('\n')]
            
            lists.append({
                'type': 'unordered',
                'items': items,
                'item_count': len(items)
            })
        
        return lists
    
    def _extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract metadata from content."""
        metadata = {}
        
        # Extract front matter
        front_matter = self.extract_front_matter(content)
        metadata.update(front_matter)
        
        # Add content statistics without recursion
        metadata.update({
            'word_count': len(content.split()),
            'character_count': len(content),
            'heading_count': len(self._extract_headings(content)),
            'code_block_count': len(self._extract_code_blocks(content)),
            'link_count': len(self._extract_links(content)),
            'image_count': len(self._extract_images(content)),
            'table_count': len(self._extract_tables(content))
        })
        
        return metadata
    
    def _extract_heading_levels(self, content: str) -> List[int]:
        """Extract heading levels from content."""
        levels = []
        heading_pattern = r'^(#+)\s+'
        
        for line in content.split('\n'):
            match = re.match(heading_pattern, line)
            if match:
                levels.append(len(match.group(1)))
        
        return levels
    
    def _has_heading_hierarchy_issues(self, levels: List[int]) -> bool:
        """Check if heading hierarchy has issues."""
        if not levels:
            return False
        
        for i in range(1, len(levels)):
            if levels[i] > levels[i-1] + 1:
                return True
        
        return False
    
    def _find_broken_links(self, content: str) -> List[str]:
        """Find potentially broken links in content."""
        # This is a simplified implementation
        # In a real implementation, you'd want to check URL validity
        broken_links = []
        link_pattern = r'\[[^\]]+\]\(([^)]+)\)'
        
        for match in re.finditer(link_pattern, content):
            url = match.group(1)
            if not url.startswith(('http://', 'https://', '#', 'mailto:', 'tel:')):
                # Consider relative links without .md extension as potentially broken
                if not (url.endswith('.md') or url.endswith('.html') or '/' in url):
                    broken_links.append(url)
        
        return broken_links
    
    def _find_long_lines(self, content: str, max_length: int = 120) -> List[str]:
        """Find lines that are too long."""
        long_lines = []
        
        for line_num, line in enumerate(content.split('\n'), 1):
            if len(line) > max_length and not line.startswith('```'):
                long_lines.append(f"Line {line_num}: {len(line)} characters")
        
        return long_lines
    
    def _find_missing_alt_text(self, content: str) -> List[str]:
        """Find images missing alt text."""
        missing_alt = []
        image_pattern = r'!\[\]\(([^)]+)\)'
        
        for match in re.finditer(image_pattern, content):
            url = match.group(1)
            missing_alt.append(url)
        
        return missing_alt
    
    def _fix_common_issues(self, content: str) -> str:
        """Fix common markdown syntax issues."""
        # Fix bold/italic spacing
        content = re.sub(r'\*\*([^\*]+)\*\*', r'**\1**', content)
        content = re.sub(r'\*([^\*]+)\*', r'*\1*', content)
        
        # Fix link formatting
        content = re.sub(r'\[([^\]]+)\s*\]\s*\(([^)]+)\)', r'[\1](\2)', content)
        
        # Fix image formatting
        content = re.sub(r'!\s*\[\s*([^\]]*)\s*\]\s*\(\s*([^)]*)\s*\)', r'![\1](\2)', content)
        
        return content
    
    def _generate_statistics(self, content: str) -> Dict[str, Any]:
        """Generate content statistics."""
        structure = self.analyze_structure(content)
        
        return {
            'total_lines': len(content.split('\n')),
            'total_words': len(content.split()),
            'total_characters': len(content),
            'headings': len(structure.headings),
            'code_blocks': len(structure.code_blocks),
            'links': len(structure.links),
            'images': len(structure.images),
            'tables': len(structure.tables),
            'lists': len(structure.lists)
        }
    
    def _parse_yaml_front_matter(self, content: str) -> Dict[str, Any]:
        """Parse YAML front matter content."""
        # This is a simplified implementation
        # In a real implementation, you'd use a proper YAML parser
        metadata = {}
        
        for line in content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip().strip('"\'')
        
        return metadata
    
    def _generate_yaml_front_matter(self, metadata: Dict[str, Any]) -> str:
        """Generate YAML front matter from metadata."""
        lines = []
        
        for key, value in metadata.items():
            if isinstance(value, str):
                lines.append(f'{key}: "{value}"')
            elif isinstance(value, (int, float, bool)):
                lines.append(f'{key}: {value}')
            elif isinstance(value, list):
                lines.append(f'{key}:')
                for item in value:
                    lines.append(f'  - "{item}"')
            elif isinstance(value, dict):
                lines.append(f'{key}:')
                for k, v in value.items():
                    lines.append(f'  {k}: "{v}"')
        
        return '\n'.join(lines)
    
    def get_markdown_extensions(self) -> List[str]:
        """Get list of supported markdown extensions."""
        return [
            'tables',
            'toc',
            'fenced_code',
            'codehilite',
            'sane_lists',
            'extra',
            'attr_list',
            'def_list',
            'fenced_code',
            'footnotes',
            'md_in_html',
            'tables',
            'toc',
            'wikilinks'
        ]
    
    def is_valid_markdown(self, content: str) -> bool:
        """Check if content is valid markdown."""
        try:
            # Try to convert to HTML
            html = self.convert_to_html(content)
            return True
        except Exception:
            return False