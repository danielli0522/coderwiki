"""
MkDocs Service - Static documentation site generation service
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import yaml
import logging

from app.models.repository import Repository
from app.models.document import Document
from app.services.directory_service import DirectoryService
from app.utils.logger import get_logger
from app.utils.file_utils import FileUtils

logger = get_logger(__name__)


class MkDocsService:
    """MkDocs static site generation service"""
    
    def __init__(self):
        """Initialize MkDocs service with unified directory structure"""
        # Use the centralized directory service
        self.directory_service = DirectoryService()
        
        # Use unified paths for consistency
        self.base_docs_dir = self.directory_service.ai_generate_doc_dir
        self.base_mkdocs_dir = self.directory_service.mkdocs_site_dir
        
        # Ensure directories exist
        self.base_mkdocs_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"MkDocsService initialized with unified structure: docs_dir={self.base_docs_dir}, mkdocs_dir={self.base_mkdocs_dir}")

    def build_site_for_repository(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        Build MkDocs site for a specific repository.
        
        Args:
            repository_id: Repository ID
            user_id: User ID for permission validation
            
        Returns:
            Dictionary with build result and site information
        """
        try:
            # 验证仓库权限
            from app.services.repository_service import RepositoryService
            repo_service = RepositoryService()
            repository = repo_service.get_repository_by_id(repository_id, user_id)
            
            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found or access denied'
                }
            
            logger.info(f"Building MkDocs site for repository {repository_id}: {repository.name}")
            
            # 1. 使用统一的目录结构
            site_dir = self.directory_service.get_mkdocs_site_path(repository.name, repository_id)
            docs_dir = self.directory_service.get_mkdocs_docs_path(repository.name, repository_id)
            
            # 清理并重新创建目录
            if site_dir.exists():
                shutil.rmtree(site_dir)
            site_dir.mkdir(parents=True, exist_ok=True)
            docs_dir.mkdir(parents=True, exist_ok=True)
            
            # 2. 收集文档内容
            docs_content = self._collect_repository_documents(repository_id)
            
            # 检查是否只有基础文档（没有AI生成的文档）
            has_ai_docs = any(doc.get('document_type') == 'ai_generated' for doc in docs_content) if docs_content else False
            
            if not docs_content or not has_ai_docs:
                # 尝试触发AI文档生成
                logger.info(f"No AI-generated docs found for repository {repository_id}, triggering automatic generation")
                
                try:
                    # 触发AI文档生成
                    ai_generation_result = self._trigger_ai_document_generation(repository_id, user_id)
                    
                    if ai_generation_result and ai_generation_result.get('success'):
                        logger.info(f"AI document generation completed for repository {repository_id}")
                        # 重新收集文档（包括新生成的）
                        docs_content = self._collect_repository_documents(repository_id)
                    else:
                        logger.warning(f"AI document generation failed or not available: {ai_generation_result}")
                except Exception as e:
                    logger.error(f"Error triggering AI document generation: {e}")
                
                # 如果仍然没有文档，创建基础文档结构
                if not docs_content:
                    docs_content = self._create_basic_docs_structure(repository)
            
            # 3. 写入文档文件并构建导航结构
            nav_config = []
            
            # 按文档类型排序：readme优先，然后是AI生成的文档
            sorted_docs = sorted(docs_content, key=lambda x: (
                0 if x['document_type'] == 'readme' else 
                1 if x['document_type'] == 'ai_generated' else 2,
                x['title']
            ))
            
            for doc_info in sorted_docs:
                doc_path = docs_dir / doc_info['filename']
                with open(doc_path, 'w', encoding='utf-8') as f:
                    f.write(doc_info['content'])
                nav_config.append({doc_info['title']: doc_info['filename']})
                
                logger.info(f"Created document file: {doc_path} ({doc_info['document_type']})")
            
            # 4. 生成 mkdocs.yml 配置文件
            mkdocs_config = self._generate_mkdocs_config(repository, nav_config)
            config_path = site_dir / "mkdocs.yml"
            
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(mkdocs_config, f, default_flow_style=False, allow_unicode=True)
            
            logger.debug(f"Created mkdocs.yml: {config_path}")
            
            # 4.1 创建 Mermaid 初始化 JavaScript 文件
            self._create_mermaid_init_script(docs_dir)
            
            # 5. 构建静态站点
            build_result = self._build_mkdocs_site(site_dir)
            
            if not build_result['success']:
                return build_result
            
            # 6. 返回成功结果
            safe_repo_name = self.directory_service._sanitize_name(repository.name)
            site_url = f"/sites/{safe_repo_name}_{repository_id}/"
            
            result = {
                'success': True,
                'repository_id': repository_id,
                'repository_name': repository.name,
                'site_url': site_url,
                'site_path': str(site_dir / "site"),
                'docs_count': len(docs_content),
                'build_time': datetime.utcnow().isoformat(),
                'message': 'MkDocs site built successfully'
            }
            
            logger.info(f"MkDocs site built successfully for repository {repository_id}: {site_url}")
            return result
            
        except Exception as e:
            logger.error(f"Error building MkDocs site for repository {repository_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to build MkDocs site: {str(e)}'
            }

    def _collect_repository_documents(self, repository_id: int) -> List[Dict[str, Any]]:
        """
        Collect all documents for a repository.
        
        Args:
            repository_id: Repository ID
            
        Returns:
            List of document information dictionaries
        """
        logger.info(f"Starting document collection for repository {repository_id}")
        print(f"DEBUG: Starting document collection for repository {repository_id}", flush=True)
        try:
            docs_content = []
            
            # 优先从数据库获取已生成的文档
            try:
                documents = Document.query.filter_by(
                    repository_id=repository_id,
                    status='completed'
                ).order_by(Document.created_at.asc()).all()
                
                for doc in documents:
                    if doc.content:
                        # 生成文件名
                        filename = self._sanitize_filename(f"{doc.document_type}_{doc.title}.md")
                        
                        docs_content.append({
                            'title': doc.title,
                            'filename': filename,
                            'content': doc.content,
                            'document_type': doc.document_type,
                            'created_at': doc.created_at
                        })
                logger.info(f"Found {len(docs_content)} database documents")
            except Exception as db_error:
                logger.warning(f"Database query failed: {db_error}, continuing with filesystem only")
            
            # 也检查文件系统中的文档 - 支持dp-bi-server特殊路径结构
            try:
                # Get repository info directly from database for directory path
                try:
                    repository = Repository.query.get(repository_id)
                    if repository:
                        logger.info(f"Found repository: {repository.name} (ID: {repository_id})")
                        
                        # 特殊处理dp-bi-server项目 - 直接读取ai-generate-doc中的文档
                        if 'dp' in repository.name.lower() and 'bi' in repository.name.lower() and 'server' in repository.name.lower():
                            logger.info(f"Detected dp-bi-server project, using direct ai-generate-doc path")
                            # 查找dp-bi-server相关的目录
                            dp_bi_dirs = list(self.base_docs_dir.glob("*dp-bi-server*"))
                            if dp_bi_dirs:
                                # 选择最新的dp-bi-server目录
                                dp_bi_dir = max(dp_bi_dirs, key=lambda p: p.stat().st_mtime)
                                logger.info(f"Found dp-bi-server directory: {dp_bi_dir}")
                                
                                # 检查是否有子目录结构
                                subdirs = [d for d in dp_bi_dir.iterdir() if d.is_dir()]
                                if subdirs:
                                    # 使用第一个子目录（通常是datacloud-public-server等）
                                    repo_docs_dir = subdirs[0]
                                    logger.info(f"Using dp-bi-server subdirectory: {repo_docs_dir}")
                                else:
                                    repo_docs_dir = dp_bi_dir
                                    logger.info(f"Using dp-bi-server root directory: {repo_docs_dir}")
                            else:
                                logger.warning(f"No dp-bi-server directories found, using standard fallback")
                                repo_docs_dir = self.directory_service.get_ai_docs_path(repository.name, repository_id)
                        else:
                            # 标准路径处理
                            repo_docs_dir = self.directory_service.get_ai_docs_path(repository.name, repository_id)
                            logger.info(f"Generated AI docs path: {repo_docs_dir}")
                    else:
                        logger.warning(f"Repository {repository_id} not found in database, using fallback")
                        repo_docs_dir = self.base_docs_dir / f"repo_{repository_id}"
                except Exception as repo_error:
                    logger.warning(f"Repository query failed: {repo_error}, trying fallback paths")
                    # Try different fallback patterns including dp-bi-server
                    possible_paths = [
                        self.base_docs_dir / f"dp-bi-server-{repository_id}",  # dp-bi-server specific
                        self.base_docs_dir / f"agents_{repository_id}",       # Current actual pattern
                        self.base_docs_dir / f"repo_{repository_id}",         # Original fallback
                    ]
                    
                    # Also check for existing dp-bi-server directories
                    dp_bi_dirs = list(self.base_docs_dir.glob("*dp-bi-server*"))
                    possible_paths.extend(dp_bi_dirs)
                    
                    repo_docs_dir = None
                    logger.info(f"Testing fallback paths: {[str(p) for p in possible_paths]}")
                    for path in possible_paths:
                        logger.info(f"Checking fallback path: {path} (exists: {path.exists()})")
                        if path.exists():
                            # For dp-bi-server directories, check for subdirectories
                            if 'dp-bi-server' in str(path):
                                subdirs = [d for d in path.iterdir() if d.is_dir()]
                                if subdirs:
                                    repo_docs_dir = subdirs[0]
                                    logger.info(f"✓ Found dp-bi-server docs at: {repo_docs_dir}")
                                else:
                                    repo_docs_dir = path
                                    logger.info(f"✓ Found dp-bi-server docs at root: {path}")
                            else:
                                repo_docs_dir = path
                                logger.info(f"✓ Found AI docs at fallback path: {path}")
                            break
                    
                    if not repo_docs_dir:
                        repo_docs_dir = possible_paths[1]  # Use agents pattern as default
                        logger.info(f"No existing paths found, using default: {repo_docs_dir}")
                        
            except Exception as e:
                logger.error(f"Error getting unified AI docs path: {str(e)}, using final fallback")
                repo_docs_dir = self.base_docs_dir / f"agents_{repository_id}"  # Try the actual pattern
            
            logger.info(f"Checking for AI docs in: {repo_docs_dir}")
            print(f"DEBUG: Checking for AI docs in: {repo_docs_dir}", flush=True)
            if repo_docs_dir.exists():
                logger.info(f"AI docs directory exists, scanning for *.md files...")
                md_files = list(repo_docs_dir.glob("*.md"))
                logger.info(f"Found {len(md_files)} MD files: {[f.name for f in md_files]}")
                
                for doc_file in md_files:
                    if doc_file.is_file():
                        logger.info(f"Processing AI doc file: {doc_file.name}")
                        with open(doc_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # 避免重复
                        existing_files = [d['filename'] for d in docs_content]
                        if doc_file.name not in existing_files:
                            # Improve title generation for AI documents
                            title = doc_file.stem
                            # Remove common prefixes and make readable
                            title = title.replace('datacloud-public-server-', '')
                            title = title.replace('-', ' ').replace('_', ' ')
                            # Capitalize properly
                            title = ' '.join(word.capitalize() for word in title.split())
                            
                            logger.info(f"Adding AI doc: {title} -> {doc_file.name}")
                            docs_content.append({
                                'title': title,
                                'filename': doc_file.name,
                                'content': content,
                                'document_type': 'ai_generated',
                                'created_at': datetime.fromtimestamp(doc_file.stat().st_mtime)
                            })
                        else:
                            logger.info(f"Skipping duplicate file: {doc_file.name}")
            else:
                logger.warning(f"AI docs directory does not exist: {repo_docs_dir}")
            
            logger.info(f"Collected {len(docs_content)} documents for repository {repository_id}")
            return docs_content
            
        except Exception as e:
            logger.error(f"Error collecting documents for repository {repository_id}: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []

    def _create_basic_docs_structure(self, repository: Repository) -> List[Dict[str, Any]]:
        """
        Create basic documentation structure when no documents exist.
        
        Args:
            repository: Repository model instance
            
        Returns:
            List of basic document structures
        """
        basic_docs = [
            {
                'title': 'README',
                'filename': 'index.md',
                'content': f"""# {repository.name}

## Project Overview

This is the documentation for **{repository.name}**.

{repository.description or 'No description provided.'}

## Repository Information

- **Repository**: {repository.name}
- **URL**: {getattr(repository, 'url', 'N/A')}
- **Language**: {repository.language or 'Not specified'}
- **Created**: {repository.created_at.strftime('%Y-%m-%d') if repository.created_at else 'Unknown'}

## Getting Started

This documentation is automatically generated by CoderWiki. 

To view more detailed documentation, please generate documents through the CoderWiki interface.

## Navigation

Use the navigation menu to explore different sections of this documentation.
""",
                'document_type': 'readme',
                'created_at': datetime.utcnow()
            }
        ]
        
        # 如果有仓库元数据，添加更多信息
        if repository.repo_metadata:
            metadata = repository.repo_metadata
            if isinstance(metadata, dict):
                tech_info = []
                if metadata.get('languages'):
                    tech_info.append(f"- **Languages**: {', '.join(metadata['languages'])}")
                if metadata.get('frameworks'):
                    tech_info.append(f"- **Frameworks**: {', '.join(metadata['frameworks'])}")
                if metadata.get('dependencies'):
                    tech_info.append(f"- **Dependencies**: {len(metadata['dependencies'])} packages")
                
                if tech_info:
                    basic_docs.append({
                        'title': 'Technical Information',
                        'filename': 'technical-info.md',
                        'content': f"""# Technical Information

## Technology Stack

{chr(10).join(tech_info)}

## Repository Statistics

- **Size**: {FileUtils._format_size(repository.repo_size) if repository.repo_size else 'Unknown'}
- **Files**: {repository.file_count or 'Unknown'}
- **Commits**: {repository.commit_count or 'Unknown'}
- **Stars**: {repository.star_count or 0}
- **Forks**: {repository.fork_count or 0}

## Last Update

- **Last Commit**: {repository.last_commit or 'Unknown'}
- **Last Analysis**: {repository.last_analysis.strftime('%Y-%m-%d %H:%M:%S') if repository.last_analysis else 'Never'}
""",
                        'document_type': 'technical',
                        'created_at': datetime.utcnow()
                    })
        
        return basic_docs

    def _trigger_ai_document_generation(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        触发AI文档生成（简化版本）
        
        Args:
            repository_id: 仓库ID
            user_id: 用户ID
            
        Returns:
            生成结果字典
        """
        try:
            from app.models.repository import Repository
            from app.utils.repository_analyzer import RepositoryAnalyzer
            import os
            
            # 获取仓库信息
            repository = Repository.query.filter_by(id=repository_id, user_id=user_id).first()
            if not repository:
                logger.error(f"Repository {repository_id} not found for user {user_id}")
                return {'success': False, 'error': 'Repository not found'}
            
            # 检查环境变量是否启用Claude Code
            claude_enabled = os.environ.get('CLAUDE_CODE_ENABLED', 'false').lower() == 'true'
            
            if not claude_enabled:
                logger.info("Claude Code is not enabled, generating basic documentation instead")
                # 生成基础文档而不是跳过
                return self._generate_basic_ai_documentation(repository)
            
            # 尝试使用完整的AI服务
            try:
                from app.services.claude_code_service import ClaudeCodeService
                claude_service = ClaudeCodeService()
                
                # 创建文档记录
                document = claude_service.create_document(
                    user_id=user_id,
                    title=f'{repository.name} - AI Generated Documentation',
                    repository_id=repository_id,
                    document_type='overview',
                    description=f'AI-generated overview documentation for {repository.name}'
                )
                
                if document and document.get('id'):
                    # 触发文档生成
                    logger.info(f"Starting AI document generation for repository {repository_id}")
                    success = claude_service.generate_document_content(
                        document['id'], 
                        user_id
                    )
                    
                    if success:
                        logger.info(f"AI document generation completed successfully for repository {repository_id}")
                        return {'success': True, 'document_id': document['id']}
            except Exception as e:
                logger.warning(f"Full AI service failed: {e}, falling back to basic generation")
            
            # 如果AI服务失败，生成基础AI文档
            return self._generate_basic_ai_documentation(repository)
                
        except Exception as e:
            logger.error(f"Error in AI document generation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_basic_ai_documentation(self, repository) -> Dict[str, Any]:
        """
        生成基础的AI文档（不依赖Claude API）
        """
        try:
            from app.utils.repository_analyzer import RepositoryAnalyzer
            
            # 使用仓库分析器生成文档内容
            analyzer = RepositoryAnalyzer(repository.local_path)
            analysis = analyzer.analyze_repository()
            
            # 创建AI文档目录
            ai_docs_dir = self.docs_base_dir / f"{repository.name}_{repository.id}"
            ai_docs_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成概览文档
            overview_content = f"""# {repository.name} - Project Overview

## Repository Information
- **Name**: {repository.name}
- **URL**: {repository.url}
- **Description**: {repository.description or 'No description provided'}
- **Primary Language**: {repository.language or 'Unknown'}

## Code Statistics
- **Total Files**: {analysis.get('file_count', 0)}
- **Lines of Code**: {analysis.get('lines_of_code', 0)}
- **File Types**: {', '.join(analysis.get('file_types', []))}

## Project Structure
{self._format_directory_tree(analysis.get('structure', {}))}

## Technology Stack
{self._format_tech_stack(analysis.get('languages', {}))}

## Key Features
Based on the repository analysis:
- Repository contains {analysis.get('file_count', 0)} files
- Primary language is {repository.language or 'not detected'}
- Code complexity: {analysis.get('complexity', 'Medium')}

## Documentation Status
This is an automatically generated documentation based on static code analysis.
For more detailed documentation, please enable Claude Code integration.

---
*Generated at {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC*
"""
            
            # 保存文档
            overview_file = ai_docs_dir / "overview.md"
            with open(overview_file, 'w', encoding='utf-8') as f:
                f.write(overview_content)
            
            logger.info(f"Generated basic AI documentation for repository {repository.id}")
            return {'success': True, 'basic_doc': True}
            
        except Exception as e:
            logger.error(f"Error generating basic AI documentation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _format_directory_tree(self, structure: Dict) -> str:
        """格式化目录树"""
        if not structure:
            return "Directory structure not available"
        
        lines = []
        def format_tree(items, prefix=""):
            for i, (name, value) in enumerate(items.items()):
                is_last = i == len(items) - 1
                lines.append(f"{prefix}{'└── ' if is_last else '├── '}{name}")
                if isinstance(value, dict) and value:
                    extension = "    " if is_last else "│   "
                    format_tree(value, prefix + extension)
        
        format_tree(structure)
        return "```\n" + "\n".join(lines) + "\n```"
    
    def _format_tech_stack(self, languages: Dict) -> str:
        """格式化技术栈信息"""
        if not languages:
            return "- No language statistics available"
        
        lines = []
        total = sum(languages.values())
        for lang, count in sorted(languages.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"- **{lang}**: {percentage:.1f}% ({count} files)")
        
        return "\n".join(lines)

    def _generate_mkdocs_config(self, repository, nav_config: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Generate MkDocs configuration.
        
        Args:
            repository: Repository model instance or string name
            nav_config: Navigation configuration
            
        Returns:
            MkDocs configuration dictionary
        """
        # Handle both Repository objects and string names for testing
        if isinstance(repository, str):
            repo_name = repository
            repo_description = f"Documentation for {repository}"
        else:
            repo_name = repository.name
            repo_description = repository.description or f"Documentation for {repository.name}"
            
        config = {
            'site_name': f"{repo_name} Documentation",
            'site_description': repo_description,
            'theme': {
                'name': 'material',
                'features': [
                    'navigation.tabs',
                    'navigation.sections',
                    'navigation.expand',
                    'navigation.indexes',
                    'toc.integrate',
                    'search.suggest',
                    'search.highlight'
                ],
                'palette': [
                    {
                        'scheme': 'default',
                        'primary': 'blue',
                        'accent': 'blue',
                        'toggle': {
                            'icon': 'material/brightness-7',
                            'name': 'Switch to dark mode'
                        }
                    },
                    {
                        'scheme': 'slate',
                        'primary': 'blue',
                        'accent': 'blue',
                        'toggle': {
                            'icon': 'material/brightness-4',
                            'name': 'Switch to light mode'
                        }
                    }
                ]
            },
            'nav': nav_config,
            'plugins': [
                'search',
                'awesome-pages'
            ],
            'markdown_extensions': [
                'admonition',
                'codehilite',
                'toc',
                'tables',
                'fenced_code',
                'def_list',
                'footnotes',
                'md_in_html',
                'pymdownx.arithmatex',
                'pymdownx.betterem',
                'pymdownx.caret',
                'pymdownx.mark',
                'pymdownx.tilde',
                'pymdownx.details',
                'pymdownx.emoji',
                'pymdownx.highlight',
                'pymdownx.inlinehilite',
                'pymdownx.keys',
                'pymdownx.magiclink',
                'pymdownx.smartsymbols',
                {
                    'pymdownx.superfences': {
                        'custom_fences': [
                            {
                                'name': 'mermaid',
                                'class': 'mermaid',
                                'format': '!!python/name:pymdownx.superfences.fence_code_format'
                            }
                        ]
                    }
                },
                'pymdownx.tabbed',
                'pymdownx.tasklist'
            ],
            'extra_javascript': [
                'https://unpkg.com/mermaid/dist/mermaid.min.js',
                'javascripts/mermaid-init.js'
            ]
        }
        
        # 添加仓库信息
        if hasattr(repository, 'url') and repository.url:
            config['repo_url'] = repository.url
            config['repo_name'] = repository.name
        
        return config

    def _create_mermaid_init_script(self, docs_dir: Path) -> None:
        """
        Create Mermaid initialization JavaScript file for better diagram rendering.
        
        Args:
            docs_dir: Documentation directory path
        """
        try:
            # Create javascripts directory
            js_dir = docs_dir / "javascripts"
            js_dir.mkdir(exist_ok=True)
            
            # Mermaid initialization script content
            init_script = '''document.addEventListener('DOMContentLoaded', function() {
    // 初始化 Mermaid
    if (typeof mermaid !== 'undefined') {
        mermaid.initialize({
            startOnLoad: true,
            theme: 'default',
            securityLevel: 'loose',
            flowchart: {
                useMaxWidth: true,
                htmlLabels: true
            },
            sequence: {
                useMaxWidth: true,
                diagramMarginX: 50,
                diagramMarginY: 10,
                actorMargin: 50,
                width: 150,
                height: 65,
                boxMargin: 10,
                boxTextMargin: 5,
                noteMargin: 10,
                messageMargin: 35,
                mirrorActors: true,
                bottomMarginAdj: 1,
                useMaxWidth: true
            }
        });

        // 手动渲染所有 mermaid 图表
        setTimeout(function() {
            const mermaidElements = document.querySelectorAll('pre.mermaid');
            mermaidElements.forEach(function(element, index) {
                const graphDefinition = element.textContent || element.innerText;
                const graphId = 'mermaid-' + index;
                
                // 创建一个新的 div 来放置渲染的图表
                const mermaidDiv = document.createElement('div');
                mermaidDiv.className = 'mermaid';
                mermaidDiv.id = graphId;
                mermaidDiv.textContent = graphDefinition;
                
                // 替换原来的 pre 元素
                element.parentNode.replaceChild(mermaidDiv, element);
            });
            
            // 重新渲染
            mermaid.init(undefined, '.mermaid');
        }, 100);
    }
});'''
            
            # Write the initialization script
            init_script_path = js_dir / "mermaid-init.js"
            with open(init_script_path, 'w', encoding='utf-8') as f:
                f.write(init_script)
            
            logger.debug(f"Created mermaid initialization script: {init_script_path}")
            
        except Exception as e:
            logger.warning(f"Failed to create mermaid init script: {str(e)}")

    def _build_mkdocs_site(self, site_dir: Path) -> Dict[str, Any]:
        """
        Build MkDocs static site.
        
        Args:
            site_dir: Site directory path
            
        Returns:
            Build result dictionary
        """
        try:
            # 检查mkdocs命令是否可用
            mkdocs_cmd = self._get_mkdocs_command()
            
            if not mkdocs_cmd:
                return {
                    'success': False,
                    'error': 'MkDocs command not found. Please ensure MkDocs is installed.'
                }
            
            # 执行构建命令
            cmd = [mkdocs_cmd, 'build', '--clean']
            
            logger.info(f"Building MkDocs site in {site_dir} with command: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=site_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                logger.info(f"MkDocs build successful for {site_dir}")
                return {
                    'success': True,
                    'stdout': result.stdout,
                    'stderr': result.stderr
                }
            else:
                logger.error(f"MkDocs build failed for {site_dir}: {result.stderr}")
                return {
                    'success': False,
                    'error': f'MkDocs build failed: {result.stderr}',
                    'stdout': result.stdout
                }
                
        except subprocess.TimeoutExpired:
            logger.error(f"MkDocs build timeout for {site_dir}")
            return {
                'success': False,
                'error': 'MkDocs build timed out after 5 minutes'
            }
        except Exception as e:
            logger.error(f"Error building MkDocs site: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to build site: {str(e)}'
            }

    def _get_mkdocs_command(self) -> Optional[str]:
        """
        Get MkDocs command path.
        
        Returns:
            MkDocs command path or None if not found
        """
        try:
            # First try system path mkdocs (most reliable)
            result = subprocess.run(['which', 'mkdocs'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                mkdocs_path = result.stdout.strip()
                logger.info(f"Found system MkDocs at: {mkdocs_path}")
                return mkdocs_path
                
            # Try virtual environment if exists
            venv_mkdocs = Path(__file__).parent.parent.parent / 'venv' / 'bin' / 'mkdocs'
            if venv_mkdocs.exists():
                logger.info(f"Found venv MkDocs at: {venv_mkdocs}")
                return str(venv_mkdocs)
            
            # Try common Python module execution
            try:
                result = subprocess.run(['python', '-m', 'mkdocs', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Found Python module MkDocs")
                    return 'python -m mkdocs'
            except Exception:
                pass
            
            # Last resort - try help command
            try:
                result = subprocess.run(['python', '-m', 'mkdocs', '--help'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    logger.info("Found Python module MkDocs via help")
                    return 'python -m mkdocs'
            except Exception:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding mkdocs command: {str(e)}")
            return None

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename for filesystem compatibility and security.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename safe for filesystem use
        """
        import re
        import urllib.parse
        
        if not filename or not isinstance(filename, str):
            return '.md'
            
        # URL decode to handle encoded path traversal attempts
        try:
            filename = urllib.parse.unquote(filename)
        except Exception:
            pass
            
        # Remove any path traversal attempts
        filename = filename.replace('..', '')
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')
        
        # Remove dangerous characters and sequences
        dangerous_chars = r'[<>:"/\\|?*\x00-\x1f\x7f-\x9f]'
        filename = re.sub(dangerous_chars, '_', filename)
        
        # Remove script tags and SQL injection attempts
        filename = re.sub(r'<script[^>]*>.*?</script>', '', filename, flags=re.IGNORECASE | re.DOTALL)
        filename = re.sub(r'drop\s+table', '', filename, flags=re.IGNORECASE)
        filename = re.sub(r'select\s+.*\s+from', '', filename, flags=re.IGNORECASE)
        filename = re.sub(r'{{.*?}}', '', filename)  # Template injection
        filename = re.sub(r'\${.*?}', '', filename)  # Expression injection
        
        # Normalize whitespace
        filename = re.sub(r'\s+', '_', filename)
        
        # Remove leading/trailing dots and underscores
        filename = filename.strip('._')
        
        # Ensure it's not empty and has proper extension
        if not filename:
            filename = 'document'
        
        # Add .md extension if not present
        if not filename.endswith('.md'):
            filename += '.md'
        
        return filename

    def _get_existing_site_build_path(self, repository_name: str, repository_id: int) -> Optional[Path]:
        """
        Find existing MkDocs site build path, checking both new and legacy patterns.
        
        Args:
            repository_name: Repository name
            repository_id: Repository ID
            
        Returns:
            Path to existing site build directory or None if not found
        """
        try:
            safe_name = self.directory_service._sanitize_name(repository_name)
            
            # Pattern 1: New pattern with ID suffix: {name}_{id}/site
            new_pattern_site_dir = self.base_mkdocs_dir / f"{safe_name}_{repository_id}" / "site"
            if new_pattern_site_dir.exists():
                logger.debug(f"Found site at new pattern: {new_pattern_site_dir}")
                return new_pattern_site_dir
            
            # Pattern 2: Legacy pattern without ID: {name}/site
            legacy_pattern_site_dir = self.base_mkdocs_dir / safe_name / "site"
            if legacy_pattern_site_dir.exists():
                logger.debug(f"Found site at legacy pattern: {legacy_pattern_site_dir}")
                return legacy_pattern_site_dir
            
            # Pattern 3: Try exact repository name match
            exact_name_site_dir = self.base_mkdocs_dir / repository_name / "site"
            if exact_name_site_dir.exists():
                logger.debug(f"Found site at exact name pattern: {exact_name_site_dir}")
                return exact_name_site_dir
            
            logger.debug(f"No existing site found for {repository_name} (ID: {repository_id})")
            return None
            
        except Exception as e:
            logger.error(f"Error finding existing site build path: {str(e)}")
            return None

    def check_site_exists(self, repository_id: int) -> bool:
        """
        Check if MkDocs site exists for a repository.
        
        Args:
            repository_id: Repository ID
            
        Returns:
            True if site exists and is built, False otherwise
        """
        try:
            repository = Repository.query.get(repository_id)
            if not repository:
                return False
                
            # Check both new and legacy directory patterns
            site_build_dir = self._get_existing_site_build_path(repository.name, repository_id)
            
            if site_build_dir:
                # Check if index.html exists
                index_file = site_build_dir / "index.html"
                exists = index_file.exists()
                logger.debug(f"Site exists check for repository {repository_id}: {exists} at {site_build_dir}")
                return exists
            
            logger.debug(f"No site directory found for repository {repository_id}")
            return False
            
        except Exception as e:
            logger.error(f"Failed to check site existence for repository {repository_id}: {e}")
            return False

    def get_site_url(self, repository_id: int) -> Optional[str]:
        """
        Get MkDocs site URL for a repository.
        
        Args:
            repository_id: Repository ID
            
        Returns:
            Site URL if exists, None otherwise
        """
        try:
            if self.check_site_exists(repository_id):
                repository = Repository.query.get(repository_id)
                if repository:
                    import re
                    sanitized_name = re.sub(r'[^\w\-_]', '_', repository.name)
                    return f"/sites/{sanitized_name}_{repository_id}/"
            return None
            
        except Exception as e:
            logger.error(f"Failed to get site URL for repository {repository_id}: {e}")
            return None

    def get_site_status(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        Get MkDocs site build status for a repository.
        
        Args:
            repository_id: Repository ID
            user_id: User ID for permission validation
            
        Returns:
            Site status information
        """
        try:
            # 验证仓库权限
            from app.services.repository_service import RepositoryService
            repo_service = RepositoryService()
            repository = repo_service.get_repository_by_id(repository_id, user_id)
            
            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found or access denied'
                }
            
            # Use the flexible pattern matching method
            site_path = self._get_existing_site_build_path(repository.name, repository_id)
            
            if not site_path:
                return {
                    'success': True,
                    'built': False,
                    'message': 'MkDocs site not built yet'
                }
            
            # 获取站点信息
            try:
                stat = site_path.stat()
                build_time = datetime.fromtimestamp(stat.st_mtime)
            except:
                build_time = None
            
            # 计算站点大小和文件数
            total_size = 0
            file_count = 0
            
            for root, dirs, files in os.walk(site_path):
                file_count += len(files)
                for file in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, file))
                    except:
                        pass
            
            # Generate appropriate site URL based on which pattern was found
            safe_name = self.directory_service._sanitize_name(repository.name)
            site_url = f"/sites/{safe_name}_{repository_id}/"
            
            return {
                'success': True,
                'built': True,
                'repository_id': repository_id,
                'repository_name': repository.name,
                'site_url': site_url,
                'build_time': build_time.isoformat() if build_time else None,
                'file_count': file_count,
                'total_size': total_size,
                'total_size_human': FileUtils._format_size(total_size) if total_size > 0 else '0 B'
            }
            
        except Exception as e:
            logger.error(f"Error getting site status for repository {repository_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to get site status: {str(e)}'
            }

    def delete_site(self, repository_id: int, user_id: int) -> Dict[str, Any]:
        """
        Delete MkDocs site for a repository.
        
        Args:
            repository_id: Repository ID
            user_id: User ID for permission validation
            
        Returns:
            Deletion result
        """
        try:
            # 验证仓库权限
            from app.services.repository_service import RepositoryService
            repo_service = RepositoryService()
            repository = repo_service.get_repository_by_id(repository_id, user_id)
            
            if not repository:
                return {
                    'success': False,
                    'error': 'Repository not found or access denied'
                }
            
            site_dir = self.directory_service.get_mkdocs_site_path(repository.name, repository_id)
            
            if not site_dir.exists():
                return {
                    'success': True,
                    'message': 'Site directory does not exist'
                }
            
            # 删除站点目录
            shutil.rmtree(site_dir)
            
            logger.info(f"Deleted MkDocs site for repository {repository_id}: {site_dir}")
            
            return {
                'success': True,
                'message': 'MkDocs site deleted successfully'
            }
            
        except Exception as e:
            logger.error(f"Error deleting site for repository {repository_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to delete site: {str(e)}'
            }

    def list_all_sites(self, user_id: int) -> Dict[str, Any]:
        """
        List all MkDocs sites for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of user's sites
        """
        try:
            # 获取用户的所有仓库
            from app.services.repository_service import RepositoryService
            repo_service = RepositoryService()
            repositories = repo_service.get_user_repositories(user_id)
            
            sites = []
            
            for repo in repositories:
                # Use flexible directory resolution
                site_path = self._get_existing_site_build_path(repo.name, repo.id)
                
                safe_name = self.directory_service._sanitize_name(repo.name)
                site_info = {
                    'repository_id': repo.id,
                    'repository_name': repo.name,
                    'built': site_path is not None and site_path.exists(),
                    'site_url': f"/sites/{safe_name}_{repo.id}/" if site_path and site_path.exists() else None,
                }
                
                if site_path and site_path.exists():
                    try:
                        stat = site_path.stat()
                        site_info['build_time'] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                        
                        # 计算大小
                        total_size = sum(
                            os.path.getsize(os.path.join(root, file))
                            for root, dirs, files in os.walk(site_path)
                            for file in files
                        )
                        site_info['total_size'] = total_size
                        site_info['total_size_human'] = FileUtils._format_size(total_size)
                    except:
                        site_info['build_time'] = None
                        site_info['total_size'] = 0
                        site_info['total_size_human'] = '0 B'
                
                sites.append(site_info)
            
            return {
                'success': True,
                'sites': sites,
                'total_sites': len(sites),
                'built_sites': len([s for s in sites if s['built']])
            }
            
        except Exception as e:
            logger.error(f"Error listing sites for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': f'Failed to list sites: {str(e)}'
            }