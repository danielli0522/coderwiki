"""
Unit tests for markdown utilities
"""

import pytest
from app.utils.markdown_utils import MarkdownUtils, MarkdownStructure


class TestMarkdownUtils:
    """Test cases for MarkdownUtils class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.utils = MarkdownUtils()
        self.sample_markdown = """
# Main Document Title

This is a sample markdown document with **bold text** and *italic text*.

## Section 1

Here's some content with a [link](https://example.com).

### Subsection 1.1

- List item 1
- List item 2
- List item 3

## Section 2

Here's a code block:

```python
def hello_world():
    print("Hello, World!")
```

And a table:

| Column 1 | Column 2 |
|----------|----------|
| Data 1   | Data 2   |
| Data 3   | Data 4   |

![Image](image.png)
"""
    
    def test_init(self):
        """Test MarkdownUtils initialization."""
        utils = MarkdownUtils()
        assert utils.md is not None
        assert hasattr(utils, 'convert_to_html')
    
    def test_convert_to_html(self):
        """Test markdown to HTML conversion."""
        markdown_text = "# Heading\n\nThis is **bold** text."
        html = self.utils.convert_to_html(markdown_text)
        
        assert '<h1' in html and 'Heading' in html
        assert '<strong>bold</strong>' in html
    
    def test_extract_table_of_contents(self):
        """Test table of contents extraction."""
        toc = self.utils.extract_table_of_contents(self.sample_markdown)
        
        assert len(toc) == 4
        assert toc[0]['level'] == 1
        assert toc[0]['title'] == 'Main Document Title'
        assert toc[0]['anchor'] == 'main-document-title'
        assert toc[1]['level'] == 2
        assert toc[1]['title'] == 'Section 1'
    
    def test_optimize_markdown(self):
        """Test markdown optimization."""
        messy_markdown = """
#   Heading  



This has    extra    spaces.

**bold**

```python
code
```
"""
        optimized = self.utils.optimize_markdown(messy_markdown)
        
        # Should remove excessive blank lines
        assert optimized.count('\n\n') < messy_markdown.count('\n\n')
        # Should fix heading spacing
        assert '# Heading' in optimized
        # Should preserve code blocks
        assert '```python' in optimized
    
    def test_extract_front_matter(self):
        """Test front matter extraction."""
        content_with_front_matter = """---
title: Test Document
author: John Doe
date: 2023-01-01
---

# Main Content

This is the main content.
"""
        front_matter = self.utils.extract_front_matter(content_with_front_matter)
        
        assert front_matter['title'] == 'Test Document'
        assert front_matter['author'] == 'John Doe'
        assert front_matter['date'] == '2023-01-01'
    
    def test_add_front_matter(self):
        """Test adding front matter to content."""
        content = "# Main Content\n\nThis is the main content."
        metadata = {
            'title': 'Test Document',
            'author': 'John Doe'
        }
        
        content_with_front_matter = self.utils.add_front_matter(content, metadata)
        
        assert '---' in content_with_front_matter
        assert 'title: "Test Document"' in content_with_front_matter
        assert 'author: "John Doe"' in content_with_front_matter
        assert '# Main Content' in content_with_front_matter
    
    def test_generate_summary(self):
        """Test summary generation."""
        content = """---
title: Test
---

# Main Title

This is the first paragraph of the document. It contains multiple sentences that should be included in the summary.

## Section 1

This is another paragraph with more content.
"""
        summary = self.utils.generate_summary(content, max_length=100)
        
        assert len(summary) <= 100
        assert 'Main Title' in summary
    
    def test_generate_anchor(self):
        """Test anchor generation from titles."""
        anchor = self.utils._generate_anchor("Test Title with Spaces")
        assert anchor == 'test-title-with-spaces'
        
        anchor = self.utils._generate_anchor("Special@Characters#Here")
        assert anchor == 'specialcharactershere'
        
        anchor = self.utils._generate_anchor("Multiple  Spaces")
        assert anchor == 'multiple-spaces'
    
    def test_find_long_lines(self):
        """Test finding long lines."""
        content = "This is a normal line.\n" + "This is a very long line that exceeds the maximum length limit and should be detected.\n" + "Another normal line."
        
        long_lines = self.utils._find_long_lines(content, max_length=50)
        
        assert len(long_lines) == 1
        assert 'Line 2' in long_lines[0]
    
    def test_find_missing_alt_text(self):
        """Test finding missing alt text."""
        content = "![Image with alt](image.png)\n![](no-alt.png)\n![Another image](image2.png)"
        
        missing_alt = self.utils._find_missing_alt_text(content)
        
        assert len(missing_alt) == 1
        assert 'no-alt.png' in missing_alt
    
    def test_is_valid_markdown(self):
        """Test markdown validation."""
        valid_markdown = "# Heading\n\nThis is valid content."
        assert self.utils.is_valid_markdown(valid_markdown) is True
        
        # Test with obviously invalid content (this should still pass basic markdown parsing)
        invalid_markdown = "This is just plain text"
        assert self.utils.is_valid_markdown(invalid_markdown) is True
    
    def test_get_markdown_extensions(self):
        """Test getting supported markdown extensions."""
        extensions = self.utils.get_markdown_extensions()
        
        assert isinstance(extensions, list)
        assert len(extensions) > 0
        assert 'tables' in extensions
        assert 'toc' in extensions
        assert 'fenced_code' in extensions


class TestMarkdownStructure:
    """Test cases for MarkdownStructure dataclass."""
    
    def test_structure_creation(self):
        """Test creating markdown structure."""
        structure = MarkdownStructure(
            headings=[{'level': 1, 'title': 'Test'}],
            code_blocks=[{'language': 'python', 'content': 'print("hello")'}],
            links=[{'text': 'link', 'url': 'https://example.com'}],
            images=[{'alt_text': 'image', 'url': 'image.png'}],
            tables=[{'headers': ['Col1'], 'rows': [['Data']]}],
            lists=[{'type': 'unordered', 'items': ['item1']}],
            metadata={'word_count': 100}
        )
        
        assert len(structure.headings) == 1
        assert len(structure.code_blocks) == 1
        assert len(structure.links) == 1
        assert len(structure.images) == 1
        assert len(structure.tables) == 1
        assert len(structure.lists) == 1
        assert structure.metadata['word_count'] == 100
    
    def test_empty_structure(self):
        """Test creating empty markdown structure."""
        structure = MarkdownStructure(
            headings=[],
            code_blocks=[],
            links=[],
            images=[],
            tables=[],
            lists=[],
            metadata={}
        )
        
        assert len(structure.headings) == 0
        assert len(structure.code_blocks) == 0
        assert len(structure.links) == 0
        assert len(structure.images) == 0
        assert len(structure.tables) == 0
        assert len(structure.lists) == 0
        assert structure.metadata == {}