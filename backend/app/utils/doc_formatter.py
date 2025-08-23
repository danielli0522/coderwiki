import os
import re
import json
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

@dataclass
class DocumentSection:
    """文档章节"""
    title: str
    content: str
    level: int = 1

@dataclass
class DocumentMetadata:
    """文档元数据"""
    title: str
    author: str
    version: str
    created_at: str
    updated_at: str
    tags: List[str]
    language: str = 'zh-CN'

class DocumentFormatter:
    """文档格式化工具"""
    
    def __init__(self):
        self.supported_formats = ['markdown', 'html', 'json', 'txt']
    
    def format_markdown(self, content: str, metadata: DocumentMetadata = None) -> str:
        """格式化Markdown文档"""
        if metadata:
            header = f"""# {metadata.title}

**作者**: {metadata.author}  
**版本**: {metadata.version}  
**创建时间**: {metadata.created_at}  
**更新时间**: {metadata.updated_at}  
**标签**: {', '.join(metadata.tags)}  

---

"""
        else:
            header = ""
        
        # 处理内容格式
        formatted_content = self._format_markdown_content(content)
        
        return header + formatted_content
    
    def _format_markdown_content(self, content: str) -> str:
        """格式化Markdown内容"""
        # 标准化标题格式
        content = re.sub(r'^#+\s*', lambda m: m.group(0).lower(), content, flags=re.MULTILINE)
        
        # 代码块格式化
        content = re.sub(r'```(\w+)?\n(.*?)\n```', 
                        lambda m: f"```{m.group(1) or ''}\n{m.group(2).strip()}\n```", 
                        content, flags=re.DOTALL)
        
        # 链接格式化
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'[\1](\2)', content)
        
        # 列表格式化
        content = re.sub(r'^\s*[-*+]\s+', r'- ', content, flags=re.MULTILINE)
        
        return content
    
    def format_html(self, content: str, metadata: DocumentMetadata = None) -> str:
        """格式化HTML文档"""
        html_content = f"""<!DOCTYPE html>
<html lang="{metadata.language if metadata else 'zh-CN'}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{metadata.title if metadata else 'Document'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0 auto; max-width: 800px; padding: 20px; }}
        h1, h2, h3, h4, h5, h6 {{ color: #333; }}
        code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        blockquote {{ border-left: 4px solid #ccc; margin-left: 0; padding-left: 20px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
"""
        
        if metadata:
            html_content += f"""
    <header>
        <h1>{metadata.title}</h1>
        <div class="metadata">
            <p><strong>作者:</strong> {metadata.author}</p>
            <p><strong>版本:</strong> {metadata.version}</p>
            <p><strong>创建时间:</strong> {metadata.created_at}</p>
            <p><strong>更新时间:</strong> {metadata.updated_at}</p>
            <p><strong>标签:</strong> {', '.join(metadata.tags)}</p>
        </div>
    </header>
    <hr>
"""
        
        # 转换Markdown内容为HTML
        html_content += self._markdown_to_html(content)
        
        html_content += """
</body>
</html>
"""
        
        return html_content
    
    def _markdown_to_html(self, content: str) -> str:
        """简单的Markdown转HTML"""
        html_lines = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line:
                html_lines.append('<br>')
                continue
            
            # 标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                html_lines.append(f'<h{level}>{title}</h{level}>')
                continue
            
            # 代码块
            if line.startswith('```'):
                html_lines.append('<pre><code>')
                continue
            
            # 引用
            if line.startswith('>'):
                quote_content = line[1:].strip()
                html_lines.append(f'<blockquote>{quote_content}</blockquote>')
                continue
            
            # 列表
            if line.startswith('- ') or line.startswith('* '):
                item_content = line[2:].strip()
                html_lines.append(f'<li>{item_content}</li>')
                continue
            
            # 普通段落
            html_lines.append(f'<p>{line}</p>')
        
        return '\n'.join(html_lines)
    
    def format_json(self, content: str, metadata: DocumentMetadata = None) -> str:
        """格式化JSON文档"""
        doc_data = {
            'metadata': asdict(metadata) if metadata else {},
            'content': content,
            'sections': self._extract_sections(content)
        }
        
        return json.dumps(doc_data, ensure_ascii=False, indent=2)
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """提取文档章节"""
        sections = []
        lines = content.split('\n')
        current_section = None
        
        for line in lines:
            # 检测标题
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                
                level = len(line) - len(line.lstrip('#'))
                title = line.lstrip('#').strip()
                current_section = {
                    'title': title,
                    'level': level,
                    'content': ''
                }
            elif current_section:
                current_section['content'] += line + '\n'
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def generate_api_documentation(self, api_specs: Dict[str, Any]) -> str:
        """生成API文档"""
        doc = f"""# API 文档

## 概述
{api_specs.get('description', 'API接口文档')}

## 基础信息
- **基础URL**: {api_specs.get('base_url', 'N/A')}
- **版本**: {api_specs.get('version', 'N/A')}
- **认证方式**: {api_specs.get('auth_type', 'N/A')}

"""
        
        # 接口列表
        for endpoint in api_specs.get('endpoints', []):
            doc += f"""
## {endpoint.get('method', 'GET').upper()} {endpoint.get('path', '/N/A')}

### 描述
{endpoint.get('description', '接口描述')}

### 请求参数
"""
            
            for param in endpoint.get('parameters', []):
                doc += f"- **{param.get('name', 'N/A')}** ({param.get('type', 'string')}): {param.get('description', '参数描述')}\n"
            
            doc += "\n### 响应格式\n"
            doc += f"```json\n{json.dumps(endpoint.get('response', {}), ensure_ascii=False, indent=2)}\n```\n\n"
        
        return doc
    
    def generate_readme(self, project_info: Dict[str, Any]) -> str:
        """生成README文档"""
        readme = f"""# {project_info.get('name', 'Project')}

{project_info.get('description', '项目描述')}

## 功能特性

"""
        
        for feature in project_info.get('features', []):
            readme += f"- {feature}\n"
        
        readme += f"""
## 安装说明

{project_info.get('installation', '安装说明')}

## 使用方法

{project_info.get('usage', '使用方法')}

## 配置

{project_info.get('configuration', '配置说明')}

## 贡献指南

{project_info.get('contributing', '贡献指南')}

## 许可证

{project_info.get('license', 'MIT')}

## 作者

{project_info.get('author', '作者信息')}
"""
        
        return readme
    
    def format_code_documentation(self, code: str, language: str = 'python', 
                                doc_type: str = 'function') -> str:
        """格式化代码文档"""
        if doc_type == 'function':
            return self._format_function_doc(code, language)
        elif doc_type == 'class':
            return self._format_class_doc(code, language)
        else:
            return self._format_module_doc(code, language)
    
    def _format_function_doc(self, code: str, language: str) -> str:
        """格式化函数文档"""
        return f"""
## 函数文档

```{language}
{code}
```

### 功能说明
[函数功能说明]

### 参数
- `param1`: 参数说明
- `param2`: 参数说明

### 返回值
[返回值说明]

### 异常
[异常说明]

### 示例
```{language}
# 使用示例
result = function_name(param1, param2)
```
"""
    
    def _format_class_doc(self, code: str, language: str) -> str:
        """格式化类文档"""
        return f"""
## 类文档

```{language}
{code}
```

### 类说明
[类功能说明]

### 属性
- `attr1`: 属性说明
- `attr2`: 属性说明

### 方法
- `method1()`: 方法说明
- `method2()`: 方法说明

### 示例
```{language}
# 使用示例
obj = ClassName()
obj.method1()
```
"""
    
    def _format_module_doc(self, code: str, language: str) -> str:
        """格式化模块文档"""
        return f"""
## 模块文档

```{language}
{code}
```

### 模块说明
[模块功能说明]

### 主要组件
- [组件1]: 说明
- [组件2]: 说明

### 使用方法
```{language}
# 导入模块
import module_name

# 使用模块
module_name.function()
```
"""