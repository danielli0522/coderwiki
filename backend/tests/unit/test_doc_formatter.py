"""
Unit tests for document formatting service
"""

import pytest
from unittest.mock import Mock, patch
from app.services.doc_formatter import DocumentFormatter, FormattingOptions, FormattingResult
from app.utils.markdown_utils import MarkdownUtils, MarkdownStructure


class TestDocumentFormatter:
    """Test cases for DocumentFormatter class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = DocumentFormatter()
        self.sample_content = """
# Test Document

This is a test document with **bold text** and *italic text*.

## Section 1

Here's some code:

```python
def hello_world():
    print("Hello, World!")
```

### Subsection

- Item 1
- Item 2
- Item 3

## Section 2

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
"""
    
    def test_init(self):
        """Test DocumentFormatter initialization."""
        formatter = DocumentFormatter()
        assert formatter.template_service is not None
        assert formatter.highlight_service is not None
        assert formatter.export_service is not None
        assert formatter.preview_service is not None
        assert formatter.markdown_utils is not None
    
    def test_format_document_success(self):
        """Test successful document formatting."""
        options = FormattingOptions(
            template_id='technical',
            highlight_theme='github',
            include_toc=True
        )
        
        with patch.object(self.formatter, '_apply_template') as mock_template, \
             patch.object(self.formatter, '_process_markdown') as mock_markdown, \
             patch.object(self.formatter, '_apply_code_highlighting') as mock_highlight, \
             patch.object(self.formatter, '_generate_table_of_contents') as mock_toc, \
             patch.object(self.formatter, '_create_document_structure') as mock_structure:
            
            # Mock template service
            mock_template.return_value = type('TemplateResult', (), {
                'success': True,
                'processed_content': self.sample_content
            })()
            
            # Mock markdown processing
            mock_markdown.return_value = type('MarkdownResult', (), {
                'success': True,
                'formatted_content': '<h1>Test Document</h1>',
                'table_of_contents': [{'level': 1, 'title': 'Test Document', 'anchor': 'test-document'}]
            })()
            
            # Mock other methods
            mock_highlight.return_value = '<h1>Test Document</h1>'
            mock_toc.return_value = '<div class="toc">...</div>'
            mock_structure.return_value = '<html><body>...</body></html>'
            
            # Mock export service
            with patch.object(self.formatter.export_service, 'export_document') as mock_export:
                mock_export.return_value = '/exports/test.html'
                
                result = self.formatter.format_document(self.sample_content, options)
                
                assert result.success is True
                assert result.formatted_content == '<html><body>...</body></html>'
                assert result.table_of_contents == '<div class="toc">...</div>'
                assert result.metadata is not None
                assert result.export_urls is not None
    
    def test_format_document_template_failure(self):
        """Test document formatting with template failure."""
        options = FormattingOptions(template_id='nonexistent')
        
        with patch.object(self.formatter, '_apply_template') as mock_template:
            mock_template.return_value = type('TemplateResult', (), {
                'success': False,
                'processed_content': self.sample_content,
                'error_message': 'Template not found'
            })()
            
            result = self.formatter.format_document(self.sample_content, options)
            
            assert result.success is False
            assert result.error_message == 'Template not found'
    
    def test_validate_formatting_options(self):
        """Test formatting options validation."""
        options = FormattingOptions(
            template_id='technical',
            highlight_theme='github',
            export_formats=['html', 'pdf']
        )
        
        with patch.object(self.formatter.template_service, 'get_template') as mock_template, \
             patch.object(self.formatter.highlight_service, 'get_available_themes') as mock_themes, \
             patch.object(self.formatter.export_service, 'get_supported_formats') as mock_formats:
            
            mock_template.return_value = {'id': 'technical'}
            mock_themes.return_value = ['github', 'monokai']
            mock_formats.return_value = ['html', 'pdf', 'markdown']
            
            errors = self.formatter.validate_formatting_options(options)
            
            assert len(errors) == 0
    
    def test_validate_formatting_options_invalid_template(self):
        """Test formatting options validation with invalid template."""
        options = FormattingOptions(template_id='nonexistent')
        
        with patch.object(self.formatter.template_service, 'get_template') as mock_template:
            mock_template.return_value = None
            
            errors = self.formatter.validate_formatting_options(options)
            
            assert len(errors) > 0
            assert 'Template' in errors[0]
    
    def test_get_formatting_capabilities(self):
        """Test getting formatting capabilities."""
        with patch.object(self.formatter.template_service, 'get_available_templates') as mock_templates, \
             patch.object(self.formatter.highlight_service, 'get_available_themes') as mock_themes, \
             patch.object(self.formatter.export_service, 'get_supported_formats') as mock_formats:
            
            mock_templates.return_value = [{'id': 'technical'}, {'id': 'api'}]
            mock_themes.return_value = ['github', 'monokai']
            mock_formats.return_value = ['html', 'pdf']
            
            capabilities = self.formatter.get_formatting_capabilities()
            
            assert 'templates' in capabilities
            assert 'highlight_themes' in capabilities
            assert 'export_formats' in capabilities
            assert 'features' in capabilities
            assert capabilities['features']['table_of_contents'] is True
    
    def test_count_code_blocks(self):
        """Test counting code blocks in content."""
        content = """
# Test

```python
print("Hello")
```

Text here.

```javascript
console.log("Hello");
```
"""
        
        count = self.formatter._count_code_blocks(content)
        assert count == 2
    
    def test_extract_headings(self):
        """Test extracting headings from content."""
        content = """
# Main Title

## Section 1

### Subsection

## Section 2
"""
        
        headings = self.formatter._extract_headings(content)
        assert len(headings) == 4
        assert headings[0]['level'] == 1
        assert headings[0]['title'] == 'Main Title'
        assert headings[1]['level'] == 2
        assert headings[1]['title'] == 'Section 1'
    
    def test_generate_anchor(self):
        """Test anchor generation from titles."""
        anchor = self.formatter._generate_anchor("Test Title with Spaces")
        assert anchor == 'test-title-with-spaces'
        
        anchor = self.formatter._generate_anchor("Special@Characters#Here")
        assert anchor == 'specialcharactershere'


class TestFormattingOptions:
    """Test cases for FormattingOptions dataclass."""
    
    def test_default_options(self):
        """Test default formatting options."""
        options = FormattingOptions()
        
        assert options.template_id == 'technical'
        assert options.highlight_theme == 'github'
        assert options.include_toc is True
        assert options.include_line_numbers is True
        assert options.enable_code_copy is True
        assert options.custom_css is None
        assert options.custom_js is None
        assert options.export_formats == ['html', 'markdown']
    
    def test_custom_options(self):
        """Test custom formatting options."""
        options = FormattingOptions(
            template_id='api',
            highlight_theme='monokai',
            include_toc=False,
            export_formats=['pdf', 'html']
        )
        
        assert options.template_id == 'api'
        assert options.highlight_theme == 'monokai'
        assert options.include_toc is False
        assert options.export_formats == ['pdf', 'html']


class TestFormattingResult:
    """Test cases for FormattingResult dataclass."""
    
    def test_success_result(self):
        """Test successful formatting result."""
        result = FormattingResult(
            success=True,
            formatted_content='<html>...</html>',
            table_of_contents='<div class="toc">...</div>',
            metadata={'template_id': 'technical'},
            export_urls={'html': '/exports/test.html'}
        )
        
        assert result.success is True
        assert result.formatted_content == '<html>...</html>'
        assert result.table_of_contents == '<div class="toc">...</div>'
        assert result.metadata == {'template_id': 'technical'}
        assert result.export_urls == {'html': '/exports/test.html'}
        assert result.error_message is None
    
    def test_failure_result(self):
        """Test failed formatting result."""
        result = FormattingResult(
            success=False,
            formatted_content='',
            error_message='Template not found'
        )
        
        assert result.success is False
        assert result.formatted_content == ''
        assert result.error_message == 'Template not found'
        assert result.table_of_contents is None
        assert result.metadata is None
        assert result.export_urls is None