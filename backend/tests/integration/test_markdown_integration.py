"""
Integration tests for document formatting system
"""

import pytest
from unittest.mock import Mock, patch
from app.utils.markdown_utils import MarkdownUtils


class TestMarkdownUtilsIntegration:
    """Integration tests for MarkdownUtils that don't require external services."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utils = MarkdownUtils()
        self.complex_markdown = """
# Technical Documentation

## Overview

This is a comprehensive technical document with multiple sections.

### System Architecture

The system consists of the following components:

1. **Frontend**: User interface and interaction
2. **Backend**: Business logic and data processing
3. **Database**: Data storage and retrieval

### Code Examples

Here's a Python example:

```python
def process_data(data):
    result = []
    for item in data:
        if item is not None:
            result.append(item * 2)
    return result
```

And a JavaScript example:

```javascript
function validateForm(form) {
    if (form.username.value === '') {
        alert('Username is required');
        return false;
    }
    return true;
}
```

### Configuration

| Parameter | Type | Default | Description |
|------------|------|---------|-------------|
| timeout | int | 30 | Request timeout in seconds |
| retries | int | 3 | Number of retry attempts |
| debug | bool | false | Enable debug logging |

### API Endpoints

The following API endpoints are available:

- `GET /api/users` - List all users
- `POST /api/users` - Create a new user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

## Implementation Details

### Database Schema

The users table has the following structure:

```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Security Considerations

- All passwords are hashed using bcrypt
- API endpoints require authentication
- Input validation is performed on all requests
- SQL injection prevention is implemented

## Deployment

### Prerequisites

- Python 3.8+
- MySQL 8.0+
- Redis 6.0+

### Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables
4. Run migrations: `flask db upgrade`
5. Start the application: `flask run`

## Troubleshooting

### Common Issues

**Database Connection Failed**
- Check database credentials
- Ensure database server is running
- Verify network connectivity

**Import Errors**
- Verify all dependencies are installed
- Check Python version compatibility
- Review import statements

### Performance Optimization

To improve performance:

1. Enable database connection pooling
2. Implement caching strategies
3. Optimize database queries
4. Use async processing for long-running tasks

## Conclusion

This document provides a comprehensive overview of the system architecture, implementation details, and deployment instructions.
"""
    
    def test_complete_markdown_processing(self):
        """Test complete markdown processing workflow."""
        # Test conversion to HTML
        html = self.utils.convert_to_html(self.complex_markdown)
        
        # Verify basic HTML structure
        assert '<h1' in html
        assert '<h2' in html
        assert '<h3' in html
        assert '<strong>' in html
        assert '<code>' in html
        assert '<table>' in html
        assert '<pre>' in html
        assert '<ul>' in html
        assert '<ol>' in html
    
    def test_table_of_contents_extraction(self):
        """Test table of contents extraction from complex document."""
        toc = self.utils.extract_table_of_contents(self.complex_markdown)
        
        # Verify all major sections are extracted
        assert len(toc) >= 8  # Should have at least 8 major sections
        assert toc[0]['title'] == 'Technical Documentation'
        assert toc[0]['level'] == 1
        assert toc[0]['anchor'] == 'technical-documentation'
        
        # Verify major sections are found
        major_sections = ['Overview', 'System Architecture', 'Code Examples', 'Configuration', 'API Endpoints', 'Implementation Details', 'Security Considerations', 'Deployment', 'Troubleshooting', 'Performance Optimization', 'Conclusion']
        found_sections = 0
        for item in toc:
            if item['title'] in major_sections:
                found_sections += 1
        
        assert found_sections >= 8, f"Should find at least 8 major sections, found {found_sections}"
    
    def test_markdown_optimization(self):
        """Test markdown optimization functionality."""
        messy_markdown = """
#   Messy   Document  




This    has    irregular    spacing.


**Bold    text**    here.

```python
def    messy_function(    x    ):
    return    x    *    2
```

|  Column 1  |  Column 2  |
|-------------|-------------|
|  Data 1     |  Data 2     |


"""
        
        optimized = self.utils.optimize_markdown(messy_markdown)
        
        # Verify excessive blank lines are removed
        blank_line_count = optimized.count('\n\n')
        assert blank_line_count < messy_markdown.count('\n\n')
        
        # Verify heading spacing is fixed
        assert '# Messy Document' in optimized
        
        # Verify code blocks are preserved
        assert '```python' in optimized
        assert 'def messy_function' in optimized
        
        # Verify tables are preserved
        assert '|' in optimized
    
    def test_front_matter_handling(self):
        """Test front matter extraction and addition."""
        content_with_front_matter = """---
title: Technical Documentation
author: Development Team
version: 1.0.0
date: 2024-01-15
tags: [documentation, technical, api]
---

# Main Content

This is the main content of the document.
"""
        
        # Test front matter extraction
        front_matter = self.utils.extract_front_matter(content_with_front_matter)
        
        assert front_matter['title'] == 'Technical Documentation'
        assert front_matter['author'] == 'Development Team'
        assert front_matter['version'] == '1.0.0'
        assert front_matter['date'] == '2024-01-15'
        assert 'tags' in front_matter
        
        # Test adding front matter to content without front matter
        plain_content = "# Plain Content\n\nThis content has no front matter."
        metadata = {
            'title': 'New Document',
            'author': 'John Doe',
            'version': '2.0.0'
        }
        
        content_with_front_matter = self.utils.add_front_matter(plain_content, metadata)
        
        assert '---' in content_with_front_matter
        assert 'title: "New Document"' in content_with_front_matter
        assert 'author: "John Doe"' in content_with_front_matter
        assert '# Plain Content' in content_with_front_matter
    
    def test_summary_generation(self):
        """Test document summary generation."""
        summary = self.utils.generate_summary(self.complex_markdown, max_length=200)
        
        assert len(summary) <= 200
        assert 'Technical Documentation' in summary
        # Summary should capture the essence of the document
    
    def test_markdown_validation(self):
        """Test markdown validation functionality."""
        # Test valid markdown
        valid_result = self.utils.validate_markdown(self.complex_markdown)
        assert valid_result['valid'] is True
        assert len(valid_result['issues']) == 0
        
        # Test invalid markdown with unbalanced brackets
        invalid_markdown = "This has [unbalanced brackets."
        invalid_result = self.utils.validate_markdown(invalid_markdown)
        assert invalid_result['valid'] is False
        assert len(invalid_result['issues']) > 0
        assert 'brackets' in invalid_result['issues'][0]
        
        # Test markdown with long lines
        long_line_markdown = self.complex_markdown + "\n" + "This is a very long line that exceeds the typical line length limit and should be flagged by the validation system as potentially problematic for readability and maintainability."
        long_line_result = self.utils.validate_markdown(long_line_markdown)
        assert len(long_line_result['suggestions']) > 0
        assert 'long lines' in long_line_result['suggestions'][0]
    
    def test_anchor_generation_consistency(self):
        """Test anchor generation consistency."""
        test_cases = [
            "Simple Title",
            "Title with Spaces",
            "Title-with-Hyphens",
            "Title_with_Underscores",
            "Title with @Special#Characters",
            "Multiple    Spaces    Here",
            "Mixed CASE Title",
            "Title ending with punctuation!",
            "123 Numbers in Title"
        ]
        
        for title in test_cases:
            anchor = self.utils._generate_anchor(title)
            
            # Verify anchor is URL-friendly
            assert anchor.islower()
            assert ' ' not in anchor
            assert '@' not in anchor
            assert '#' not in anchor
            assert '!' not in anchor
            
            # Verify anchor is not empty
            assert len(anchor) > 0
            
            # Verify anchor starts and ends with alphanumeric
            assert anchor[0].isalnum()
            assert anchor[-1].isalnum()
    
    def test_structure_analysis_integration(self):
        """Test integrated structure analysis."""
        structure = self.utils.analyze_structure(self.complex_markdown)
        
        # Verify structure object
        assert hasattr(structure, 'headings')
        assert hasattr(structure, 'code_blocks')
        assert hasattr(structure, 'links')
        assert hasattr(structure, 'images')
        assert hasattr(structure, 'tables')
        assert hasattr(structure, 'lists')
        assert hasattr(structure, 'metadata')
        
        # Verify headings
        assert len(structure.headings) > 0
        assert structure.headings[0]['level'] == 1
        assert structure.headings[0]['title'] == 'Technical Documentation'
        
        # Verify code blocks
        assert len(structure.code_blocks) >= 2  # Python and JavaScript examples
        python_block = next((block for block in structure.code_blocks if block['language'] == 'python'), None)
        assert python_block is not None
        assert 'def process_data' in python_block['content']
        
        # Verify tables
        assert len(structure.tables) >= 1
        table = structure.tables[0]
        assert 'Parameter' in table['headers']
        assert len(table['rows']) > 0
        
        # Verify metadata
        assert 'word_count' in structure.metadata
        assert structure.metadata['word_count'] > 100
        assert 'character_count' in structure.metadata
        assert 'heading_count' in structure.metadata
        assert structure.metadata['heading_count'] == len(structure.headings)
    
    def test_performance_with_large_document(self):
        """Test performance handling with large documents."""
        # Create a large document
        large_content = "# Large Document\n\n"
        
        # Add many sections
        for i in range(100):
            large_content += f"## Section {i}\n\n"
            large_content += f"This is section {i} with some content.\n\n"
            
            # Add code blocks to some sections
            if i % 10 == 0:
                large_content += f"```python\ndef function_{i}():\n    return {i}\n```\n\n"
        
        # Add tables
        for i in range(20):
            large_content += f"| Col1 | Col2 |\n|------|------|\n| Data{i} | Value{i} |\n\n"
        
        import time
        start_time = time.time()
        
        # Test various operations
        toc = self.utils.extract_table_of_contents(large_content)
        structure = self.utils.analyze_structure(large_content)
        optimized = self.utils.optimize_markdown(large_content)
        validation = self.utils.validate_markdown(large_content)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Verify results
        assert len(toc) == 101  # 1 main title + 100 sections
        assert structure.metadata['word_count'] > 1000
        assert structure.metadata['heading_count'] == 101
        assert validation['valid'] is True
        
        # Verify performance (should be fast for this size document)
        assert processing_time < 2.0  # Should process in under 2 seconds
        
        print(f"Large document processing time: {processing_time:.2f} seconds")
        print(f"Document stats: {structure.metadata['word_count']} words, {len(toc)} headings")