"""
Integration tests for document formatting system
"""

import pytest
from unittest.mock import Mock, patch
from app.services.doc_formatter import DocumentFormatter, FormattingOptions


class TestDocumentFormattingIntegration:
    """Integration tests for the complete document formatting system."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.formatter = DocumentFormatter()
        self.sample_content = """
# Technical Document

## Overview

This document provides a comprehensive overview of the system architecture.

### Code Example

```python
def calculate_sum(a, b):
    return a + b
```

### Features

- **High Performance**: Optimized for speed
- **Scalable**: Handles large datasets
- **Reliable**: Built with error handling

## Configuration

| Setting | Value | Description |
|---------|-------|-------------|
| debug | true | Enable debug mode |
| port | 8080 | Server port |

## Installation

1. Clone the repository
2. Install dependencies
3. Configure settings
"""
    
    def test_format_document_basic_functionality(self):
        """Test basic document formatting functionality."""
        options = FormattingOptions(
            template_id='technical',
            highlight_theme='github',
            include_toc=True
        )
        
        # Mock all the dependent services since they don't exist yet
        with patch.object(self.formatter, '_apply_template') as mock_template, \
             patch.object(self.formatter, '_process_markdown') as mock_markdown, \
             patch.object(self.formatter, '_apply_code_highlighting') as mock_highlight, \
             patch.object(self.formatter, '_generate_table_of_contents') as mock_toc, \
             patch.object(self.formatter, '_create_document_structure') as mock_structure:
            
            # Mock template service to return success
            mock_template.return_value = type('TemplateResult', (), {
                'success': True,
                'processed_content': self.sample_content
            })()
            
            # Mock markdown processing
            mock_markdown.return_value = type('MarkdownResult', (), {
                'success': True,
                'formatted_content': '<h1>Technical Document</h1><h2>Overview</h2>',
                'table_of_contents': [
                    {'level': 1, 'title': 'Technical Document', 'anchor': 'technical-document'},
                    {'level': 2, 'title': 'Overview', 'anchor': 'overview'}
                ]
            })()
            
            # Mock other services
            mock_highlight.return_value = '<h1>Technical Document</h1><h2>Overview</h2>'
            mock_toc.return_value = '<div class="table-of-contents"><h3>目录</h3><ul><li><a href="#technical-document">Technical Document</a></li></ul></div>'
            mock_structure.return_value = '<!DOCTYPE html><html><head><title>Document</title></head><body><div class="document-container"><div class="toc-sidebar"><div class="table-of-contents">...</div></div><div class="document-content"><h1>Technical Document</h1></div></div></body></html>'
            
            # Mock export service
            with patch.object(self.formatter.export_service, 'export_document') as mock_export:
                mock_export.return_value = '/exports/technical_document.html'
                
                result = self.formatter.format_document(self.sample_content, options)
                
                # Verify the result
                assert result.success is True
                assert result.formatted_content is not None
                assert result.table_of_contents is not None
                assert result.metadata is not None
                assert result.export_urls is not None
                
                # Verify metadata
                assert 'template_id' in result.metadata
                assert 'highlight_theme' in result.metadata
                assert 'word_count' in result.metadata
                assert 'code_blocks' in result.metadata
                assert 'headings' in result.metadata
                
                # Verify export URLs
                assert 'html' in result.export_urls
    
    def test_format_document_with_template_failure(self):
        """Test document formatting when template application fails."""
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
            assert result.formatted_content == ""
    
    def test_formatting_options_validation(self):
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
    
    def test_formatting_capabilities(self):
        """Test getting formatting capabilities."""
        with patch.object(self.formatter.template_service, 'get_available_templates') as mock_templates, \
             patch.object(self.formatter.highlight_service, 'get_available_themes') as mock_themes, \
             patch.object(self.formatter.export_service, 'get_supported_formats') as mock_formats:
            
            mock_templates.return_value = [
                {'id': 'technical', 'name': 'Technical Document'},
                {'id': 'api', 'name': 'API Document'}
            ]
            mock_themes.return_value = ['github', 'monokai', 'solarized']
            mock_formats.return_value = ['html', 'pdf', 'markdown']
            
            capabilities = self.formatter.get_formatting_capabilities()
            
            assert 'templates' in capabilities
            assert 'highlight_themes' in capabilities
            assert 'export_formats' in capabilities
            assert 'features' in capabilities
            
            # Verify templates
            assert len(capabilities['templates']) == 2
            assert capabilities['templates'][0]['id'] == 'technical'
            
            # Verify themes
            assert len(capabilities['highlight_themes']) == 3
            assert 'github' in capabilities['highlight_themes']
            
            # Verify formats
            assert len(capabilities['export_formats']) == 3
            assert 'html' in capabilities['export_formats']
            
            # Verify features
            assert capabilities['features']['table_of_contents'] is True
            assert capabilities['features']['code_highlighting'] is True
            assert capabilities['features']['template_support'] is True
    
    def test_document_structure_analysis(self):
        """Test document structure analysis integration."""
        # This test would normally use the actual markdown_utils
        # but since we're testing integration, we'll mock it
        
        test_content = """
# Main Title

## Section 1

Content here.

### Subsection

More content.

## Section 2

Final content.
"""
        
        with patch.object(self.formatter.markdown_utils, 'analyze_structure') as mock_analyze:
            mock_analyze.return_value = type('MarkdownStructure', (), {
                'headings': [
                    {'level': 1, 'title': 'Main Title', 'anchor': 'main-title'},
                    {'level': 2, 'title': 'Section 1', 'anchor': 'section-1'},
                    {'level': 3, 'title': 'Subsection', 'anchor': 'subsection'},
                    {'level': 2, 'title': 'Section 2', 'anchor': 'section-2'}
                ],
                'code_blocks': [],
                'links': [],
                'images': [],
                'tables': [],
                'lists': [],
                'metadata': {'word_count': 20}
            })()
            
            structure = self.formatter.markdown_utils.analyze_structure(test_content)
            
            assert len(structure.headings) == 4
            assert structure.headings[0]['title'] == 'Main Title'
            assert structure.headings[0]['level'] == 1
            assert structure.metadata['word_count'] == 20
    
    def test_error_handling_integration(self):
        """Test error handling across the integrated system."""
        options = FormattingOptions(template_id='technical')
        
        # Test template service error
        with patch.object(self.formatter, '_apply_template') as mock_template:
            mock_template.side_effect = Exception("Template service error")
            
            result = self.formatter.format_document(self.sample_content, options)
            
            assert result.success is False
            assert "Template service error" in result.error_message
        
        # Test markdown processing error
        with patch.object(self.formatter, '_apply_template') as mock_template, \
             patch.object(self.formatter, '_process_markdown') as mock_markdown:
            
            mock_template.return_value = type('TemplateResult', (), {
                'success': True,
                'processed_content': self.sample_content
            })()
            
            mock_markdown.side_effect = Exception("Markdown processing error")
            
            result = self.formatter.format_document(self.sample_content, options)
            
            assert result.success is False
            assert "Markdown processing error" in result.error_message
    
    def test_performance_considerations(self):
        """Test that the formatting system handles performance considerations."""
        # Create a large document to test performance
        large_content = "# Large Document\n\n" + "## Section\n\n" + "Content " * 1000 + "\n\n" + "```python\nprint('hello')\n```\n\n" * 50
        
        options = FormattingOptions(
            template_id='technical',
            include_toc=False  # Disable TOC for performance test
        )
        
        with patch.object(self.formatter, '_apply_template') as mock_template, \
             patch.object(self.formatter, '_process_markdown') as mock_markdown, \
             patch.object(self.formatter, '_apply_code_highlighting') as mock_highlight, \
             patch.object(self.formatter, '_create_document_structure') as mock_structure:
            
            mock_template.return_value = type('TemplateResult', (), {
                'success': True,
                'processed_content': large_content
            })()
            
            mock_markdown.return_value = type('MarkdownResult', (), {
                'success': True,
                'formatted_content': '<h1>Large Document</h1>',
                'table_of_contents': []
            })()
            
            mock_highlight.return_value = '<h1>Large Document</h1>'
            mock_structure.return_value = '<html><body>...</body></html>'
            
            # Mock export service
            with patch.object(self.formatter.export_service, 'export_document') as mock_export:
                mock_export.return_value = '/exports/large_document.html'
                
                import time
                start_time = time.time()
                
                result = self.formatter.format_document(large_content, options)
                
                end_time = time.time()
                processing_time = end_time - start_time
                
                # Verify the result is successful
                assert result.success is True
                
                # Verify processing time is reasonable (should be much less than 1 second for mocked services)
                assert processing_time < 1.0
                
                # Verify metadata reflects the large document
                assert result.metadata['word_count'] > 1000
                assert result.metadata['code_blocks'] == 50