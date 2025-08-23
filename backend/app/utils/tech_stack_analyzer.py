"""
技术栈分析器
用于识别和分析项目的技术栈、框架、工具和部署环境
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class TechStackInfo:
    """技术栈信息"""
    languages: List[str]
    frameworks: List[str]
    databases: List[str]
    build_tools: List[str]
    testing_tools: List[str]
    deployment_tools: List[str]
    devops_tools: List[str]
    package_managers: List[str]
    web_servers: List[str]
    other_tools: List[str]
    confidence_scores: Dict[str, float]
    version_info: Dict[str, str]

@dataclass
class FrameworkDetection:
    """框架检测结果"""
    name: str
    category: str
    version: Optional[str]
    confidence: float
    evidence: List[str]

class TechStackAnalyzer:
    """技术栈分析器"""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.tech_stack = TechStackInfo(
            languages=[],
            frameworks=[],
            databases=[],
            build_tools=[],
            testing_tools=[],
            deployment_tools=[],
            devops_tools=[],
            package_managers=[],
            web_servers=[],
            other_tools=[],
            confidence_scores={},
            version_info={}
        )
        
        # 技术栈检测规则
        self.language_patterns = {
            'Python': ['.py', '.pyw', 'requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile'],
            'JavaScript': ['.js', '.jsx', 'package.json', 'yarn.lock', 'pnpm-lock.yaml'],
            'TypeScript': ['.ts', '.tsx', 'tsconfig.json'],
            'Java': ['.java', 'pom.xml', 'build.gradle', 'gradle.properties'],
            'Go': ['.go', 'go.mod', 'go.sum'],
            'Rust': ['.rs', 'Cargo.toml', 'Cargo.lock'],
            'C': ['.c', '.h', 'Makefile'],
            'C++': ['.cpp', '.cxx', '.cc', '.hpp', '.hxx', 'CMakeLists.txt'],
            'PHP': ['.php', 'composer.json', 'composer.lock'],
            'Ruby': ['.rb', 'Gemfile', 'Gemfile.lock'],
            'C#': ['.cs', '.csproj', 'sln'],
            'Swift': ['.swift', 'Package.swift'],
            'Kotlin': ['.kt', '.kts', 'build.gradle'],
            'Scala': ['.scala', 'build.sbt'],
            'Elixir': ['.ex', '.exs', 'mix.exs'],
            'Dart': ['.dart', 'pubspec.yaml'],
            'R': ['.r', '.R', 'Rprofile'],
            'Shell': ['.sh', '.bash', '.zsh', '.fish'],
            'SQL': ['.sql', '.ddl', '.dml']
        }
        
        self.framework_patterns = {
            'Web Frameworks': {
                'Flask': ['from flask import Flask', 'Flask', 'app.route', 'gunicorn'],
                'Django': ['from django', 'django', 'settings.py', 'manage.py', 'urls.py'],
                'FastAPI': ['from fastapi import', 'FastAPI', 'pydantic', 'uvicorn'],
                'Express': ['const express = require', 'express()', 'app.get', 'app.post'],
                'React': ['import React', 'React', 'useState', 'useEffect', 'Component', 'ReactDOM', 'react'],
                'Vue': ['import Vue', 'Vue', 'vue.js', 'vue.config.js'],
                'Angular': ['import { Component }', '@angular', 'NgModule', 'Component'],
                'Spring Boot': ['@SpringBootApplication', 'spring-boot', 'application.properties', 'SpringApplication'],
                'ASP.NET Core': ['Microsoft.AspNetCore', 'Startup', 'Program.cs'],
                'Rails': ['Rails.application', 'config/routes.rb', 'app/controllers'],
                'Laravel': ['Laravel', 'artisan', 'config/app.php'],
                'Symfony': ['Symfony', 'kernel.php', 'bundle.php'],
                'Gin': ['github.com/gin-gonic', 'gin.Default', 'gin.Engine', 'gin-gonic/gin'],
                'Echo': ['echo', 'echo.Echo'],
                'Svelte': ['svelte', '<script>'],
                'Next.js': ['next/', 'next.config.js', 'pages/'],
                'Nuxt.js': ['nuxt/', 'nuxt.config.js', 'pages/']
            },
            'Database Frameworks': {
                'SQLAlchemy': ['sqlalchemy', 'Base', 'Column', 'Integer'],
                'Django ORM': ['django.db', 'models.Model', 'objects.all()'],
                'Prisma': ['@prisma', 'schema.prisma'],
                'Sequelize': ['sequelize', 'Model', 'belongsTo'],
                'Mongoose': ['mongoose', 'Schema', 'ObjectId'],
                'Hibernate': ['@Entity', '@Table', 'javax.persistence'],
                'JPA': ['javax.persistence', 'PersistenceContext'],
                'Active Record': ['ActiveRecord::Base', 'belongs_to'],
                'GORM': ['gorm.io', 'gorm.Model'],
                'Diesel': ['diesel', 'table!', 'Queryable']
            },
            'Testing Frameworks': {
                'pytest': ['pytest', 'conftest.py', '@pytest'],
                'unittest': ['unittest', 'TestCase', 'setUp'],
                'Jest': ['jest', '@testing-library', 'it(', 'describe('],
                'Mocha': ['mocha', 'describe(', 'it('],
                'JUnit': ['@Test', '@RunWith', 'Assert'],
                'RSpec': ['rspec', 'describe', 'it', 'expect'],
                'TestNG': ['@Test', '@BeforeMethod', 'Assert'],
                'Cypress': ['cypress', 'cy.', 'describe('],
                'Selenium': ['selenium', 'webdriver', 'By.xpath']
            },
            'Build Tools': {
                'Webpack': ['webpack', 'webpack.config.js', 'webpack.prod.js'],
                'Vite': ['vite', 'vite.config.js'],
                'Gradle': ['gradle', 'build.gradle', 'settings.gradle'],
                'Maven': ['maven', 'pom.xml', 'mvn'],
                'Make': ['make', 'Makefile', 'makefile'],
                'CMake': ['cmake', 'CMakeLists.txt'],
                'Bazel': ['bazel', 'BUILD', 'WORKSPACE'],
                'Gulp': ['gulp', 'gulpfile.js'],
                'Grunt': ['grunt', 'Gruntfile.js']
            },
            'Package Managers': {
                'npm': ['package.json', 'node_modules/'],
                'pip': ['requirements.txt', 'setup.py', 'pyproject.toml'],
                'pipenv': ['Pipfile', 'Pipfile.lock'],
                'poetry': ['pyproject.toml', 'poetry.lock'],
                'yarn': ['yarn.lock', 'package.json'],
                'pnpm': ['pnpm-lock.yaml', 'package.json'],
                'composer': ['composer.json', 'composer.lock'],
                'cargo': ['Cargo.toml', 'Cargo.lock'],
                'go mod': ['go.mod', 'go.sum'],
                'gem': ['Gemfile', 'Gemfile.lock'],
                'nuget': ['.csproj', 'packages.config'],
                'brew': ['Brewfile'],
                'apt': ['apt-get', 'apt'],
                'yum': ['yum']
            }
        }
        
        self.database_patterns = {
            'PostgreSQL': ['postgresql', 'psycopg2', 'pg_dump', 'postgres'],
            'MySQL': ['mysql', 'pymysql', 'mysqldump', 'mysql-connector'],
            'SQLite': ['sqlite3', 'sqlite', '.db', '.sqlite'],
            'MongoDB': ['mongodb', 'mongo', 'mongoose', 'pymongo'],
            'Redis': ['redis', 'redis-cli', 'redis-server'],
            'Elasticsearch': ['elasticsearch', 'elasticsearch-py'],
            'Cassandra': ['cassandra', 'cqlsh'],
            'DynamoDB': ['dynamodb', 'boto3'],
            'CouchDB': ['couchdb', 'pouchdb'],
            'Oracle': ['oracle', 'cx_Oracle'],
            'SQL Server': ['sql server', 'pyodbc', 'mssql'],
            'MariaDB': ['mariadb', 'mysql']
        }
        
        self.deployment_patterns = {
            'Docker': ['Dockerfile', 'docker-compose.yml', 'docker-compose.yaml'],
            'Kubernetes': ['k8s', 'kubernetes', '.yaml', '.yml', 'Deployment'],
            'Helm': ['helm', 'Chart.yaml', 'values.yaml'],
            'Terraform': ['terraform', '.tf', 'tfstate'],
            'Ansible': ['ansible', '.yml', 'playbook'],
            'Vagrant': ['vagrant', 'Vagrantfile'],
            'Serverless': ['serverless', 'serverless.yml'],
            'Netlify': ['netlify.toml', 'netlify.yml'],
            'Vercel': ['vercel.json'],
            'Heroku': ['Procfile', 'heroku.yml'],
            'AWS': ['aws', 's3', 'lambda', 'ec2'],
            'GCP': ['gcp', 'gcloud', 'compute'],
            'Azure': ['azure', 'az', 'app-service']
        }
        
        self.web_server_patterns = {
            'Nginx': ['nginx', 'nginx.conf', '.conf'],
            'Apache': ['apache', 'httpd.conf', '.htaccess'],
            'IIS': ['iis', 'web.config'],
            'Tomcat': ['tomcat', 'server.xml', 'web.xml'],
            'Node.js': ['node', 'npm start', 'pm2'],
            'Gunicorn': ['gunicorn', 'gunicorn.conf.py'],
            'uWSGI': ['uwsgi', 'uwsgi.ini'],
            'Caddy': ['caddy', 'Caddyfile']
        }
        
    def analyze(self) -> Dict[str, Any]:
        """执行技术栈分析"""
        logger.info(f"Starting tech stack analysis for {self.repository_path}")
        
        try:
            # 分析语言
            self._analyze_languages()
            
            # 分析框架
            self._analyze_frameworks()
            
            # 分析数据库
            self._analyze_databases()
            
            # 分析构建工具
            self._analyze_build_tools()
            
            # 分析测试工具
            self._analyze_testing_tools()
            
            # 分析部署工具
            self._analyze_deployment_tools()
            
            # 分析DevOps工具
            self._analyze_devops_tools()
            
            # 分析包管理器
            self._analyze_package_managers()
            
            # 分析Web服务器
            self._analyze_web_servers()
            
            # 分析配置文件
            self._analyze_config_files()
            
            # 计算置信度分数
            self._calculate_confidence_scores()
            
            # 生成版本信息
            self._extract_version_info()
            
            result = {
                'languages': self.tech_stack.languages,
                'frameworks': self.tech_stack.frameworks,
                'databases': self.tech_stack.databases,
                'build_tools': self.tech_stack.build_tools,
                'testing_tools': self.tech_stack.testing_tools,
                'deployment_tools': self.tech_stack.deployment_tools,
                'devops_tools': self.tech_stack.devops_tools,
                'package_managers': self.tech_stack.package_managers,
                'web_servers': self.tech_stack.web_servers,
                'other_tools': self.tech_stack.other_tools,
                'confidence_scores': self.tech_stack.confidence_scores,
                'version_info': self.tech_stack.version_info,
                'analysis_metadata': {
                    'repository_path': str(self.repository_path),
                    'analysis_timestamp': self._get_timestamp(),
                    'total_files_analyzed': self._count_files_analyzed()
                }
            }
            
            logger.info(f"Tech stack analysis completed successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error during tech stack analysis: {str(e)}")
            raise
    
    def _analyze_languages(self):
        """分析编程语言"""
        logger.info("Analyzing programming languages")
        
        language_counts = {}
        
        # 扫描文件扩展名
        for file_path in self.repository_path.rglob('*'):
            if file_path.is_file():
                file_ext = file_path.suffix.lower()
                
                # 检查每个语言模式
                for lang, patterns in self.language_patterns.items():
                    for pattern in patterns:
                        if pattern.startswith('.') and file_ext == pattern:
                            language_counts[lang] = language_counts.get(lang, 0) + 1
                            break
                        elif not pattern.startswith('.') and pattern in file_path.name:
                            language_counts[lang] = language_counts.get(lang, 0) + 1
                            break
        
        # 按文件数量排序
        sorted_languages = sorted(language_counts.items(), key=lambda x: x[1], reverse=True)
        self.tech_stack.languages = [lang for lang, count in sorted_languages if count > 0]
        
        logger.info(f"Detected languages: {self.tech_stack.languages}")
    
    def _analyze_frameworks(self):
        """分析框架"""
        logger.info("Analyzing frameworks")
        
        all_frameworks = []
        
        for category, frameworks in self.framework_patterns.items():
            if category != 'Package Managers':  # 不将包管理器作为框架
                for framework_name, patterns in frameworks.items():
                    confidence = self._calculate_framework_confidence(patterns)
                    threshold = 0.1 if framework_name in ['React', 'Vue', 'Angular', 'Spring Boot'] else 0.2  # 为特定框架设置更低阈值
                    if confidence > threshold:  # 置信度阈值
                        all_frameworks.append(framework_name)
                        self.tech_stack.confidence_scores[framework_name] = confidence
        
        self.tech_stack.frameworks = sorted(list(set(all_frameworks)))
        logger.info(f"Detected frameworks: {self.tech_stack.frameworks}")
    
    def _analyze_databases(self):
        """分析数据库"""
        logger.info("Analyzing databases")
        
        db_scores = {}
        
        # 检查数据库模式
        for db_name, patterns in self.database_patterns.items():
            score = self._calculate_pattern_score(patterns)
            if score > 0.2:
                db_scores[db_name] = score
        
        # 检查数据库迁移文件
        migration_files = list(self.repository_path.rglob('*migration*')) + \
                         list(self.repository_path.rglob('*migrate*')) + \
                         list(self.repository_path.rglob('schema.*'))
        
        if migration_files:
            for db_name in ['PostgreSQL', 'MySQL', 'SQLite']:
                if db_name in db_scores:
                    db_scores[db_name] += 0.3
        
        self.tech_stack.databases = sorted(db_scores.keys(), key=lambda x: db_scores[x], reverse=True)
        logger.info(f"Detected databases: {self.tech_stack.databases}")
    
    def _analyze_build_tools(self):
        """分析构建工具"""
        logger.info("Analyzing build tools")
        
        build_tools = []
        
        # 检查构建工具模式
        for category, tools in self.framework_patterns.items():
            if category == 'Build Tools':
                for tool_name, patterns in tools.items():
                    if self._has_matching_patterns(patterns):
                        build_tools.append(tool_name)
        
        self.tech_stack.build_tools = sorted(list(set(build_tools)))
        logger.info(f"Detected build tools: {self.tech_stack.build_tools}")
    
    def _analyze_testing_tools(self):
        """分析测试工具"""
        logger.info("Analyzing testing tools")
        
        testing_tools = []
        
        # 检查测试工具模式
        for category, tools in self.framework_patterns.items():
            if category == 'Testing Frameworks':
                for tool_name, patterns in tools.items():
                    if self._has_matching_patterns(patterns):
                        testing_tools.append(tool_name)
        
        # 检查测试目录结构
        test_dirs = ['tests/', 'test/', 'spec/', '__tests__/']
        for test_dir in test_dirs:
            if (self.repository_path / test_dir).exists():
                testing_tools.append('Custom Test Framework')
                break
        
        self.tech_stack.testing_tools = sorted(list(set(testing_tools)))
        logger.info(f"Detected testing tools: {self.tech_stack.testing_tools}")
    
    def _analyze_deployment_tools(self):
        """分析部署工具"""
        logger.info("Analyzing deployment tools")
        
        deployment_tools = []
        
        # 检查部署模式
        for tool_name, patterns in self.deployment_patterns.items():
            if self._has_matching_patterns(patterns):
                deployment_tools.append(tool_name)
        
        self.tech_stack.deployment_tools = sorted(list(set(deployment_tools)))
        logger.info(f"Detected deployment tools: {self.tech_stack.deployment_tools}")
    
    def _analyze_devops_tools(self):
        """分析DevOps工具"""
        logger.info("Analyzing DevOps tools")
        
        devops_tools = []
        
        # 检查CI/CD文件
        ci_files = ['.github/workflows/', '.gitlab-ci.yml', '.travis.yml', 'jenkins/', 'circle.yml']
        for ci_file in ci_files:
            if (self.repository_path / ci_file).exists():
                devops_tools.append('CI/CD Pipeline')
                break
        
        # 检查监控工具
        monitoring_files = ['prometheus/', 'grafana/', 'monitoring/']
        for monitor_file in monitoring_files:
            if (self.repository_path / monitor_file).exists():
                devops_tools.append('Monitoring')
                break
        
        self.tech_stack.devops_tools = sorted(list(set(devops_tools)))
        logger.info(f"Detected DevOps tools: {self.tech_stack.devops_tools}")
    
    def _analyze_package_managers(self):
        """分析包管理器"""
        logger.info("Analyzing package managers")
        
        package_managers = []
        
        # 检查包管理器模式
        for category, tools in self.framework_patterns.items():
            if category == 'Package Managers':
                for tool_name, patterns in tools.items():
                    if self._has_matching_patterns(patterns):
                        package_managers.append(tool_name)
        
        self.tech_stack.package_managers = sorted(list(set(package_managers)))
        logger.info(f"Detected package managers: {self.tech_stack.package_managers}")
    
    def _analyze_web_servers(self):
        """分析Web服务器"""
        logger.info("Analyzing web servers")
        
        web_servers = []
        
        # 检查Web服务器模式
        for server_name, patterns in self.web_server_patterns.items():
            if self._has_matching_patterns(patterns):
                web_servers.append(server_name)
        
        self.tech_stack.web_servers = sorted(list(set(web_servers)))
        logger.info(f"Detected web servers: {self.tech_stack.web_servers}")
    
    def _analyze_config_files(self):
        """分析配置文件"""
        logger.info("Analyzing configuration files")
        
        config_files = [
            'config/', 'conf/', '.env', '.env.example', 'settings.py',
            'application.properties', 'app.config', 'config.yaml', 'config.yml'
        ]
        
        for config_file in config_files:
            if (self.repository_path / config_file).exists():
                self.tech_stack.other_tools.append('Configuration Management')
                break
    
    def _calculate_framework_confidence(self, patterns: List[str]) -> float:
        """计算框架检测的置信度"""
        confidence = 0.0
        total_checks = 0
        
        for pattern in patterns:
            total_checks += 1
            pattern_found = False
            
            # 检查文件名匹配
            for file_path in self.repository_path.rglob('*'):
                if file_path.is_file():
                    if pattern in file_path.name or pattern in str(file_path):
                        confidence += 0.5
                        pattern_found = True
                        break
            
            # 检查文件内容
            if not pattern_found:
                for file_path in self.repository_path.rglob('*'):
                    if file_path.is_file() and file_path.suffix in ['.py', '.js', '.ts', '.java', '.go', '.rs', '.jsx', '.tsx']:
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if pattern in content:
                                    confidence += 0.3
                                    pattern_found = True
                                    break
                        except Exception:
                            continue
        
        return min(confidence / total_checks, 1.0) if total_checks > 0 else 0.0
    
    def _calculate_pattern_score(self, patterns: List[str]) -> float:
        """计算模式匹配分数"""
        score = 0.0
        
        for pattern in patterns:
            # 检查文件名匹配
            for file_path in self.repository_path.rglob('*'):
                if file_path.is_file():
                    if pattern in file_path.name or pattern in str(file_path):
                        score += 0.5
                        break
            
            # 检查文件内容
            for file_path in self.repository_path.rglob('*'):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern in content:
                                score += 0.3
                                break
                    except Exception:
                        continue
        
        return min(score, 1.0)
    
    def _has_matching_patterns(self, patterns: List[str]) -> bool:
        """检查是否有匹配的模式"""
        for pattern in patterns:
            for file_path in self.repository_path.rglob('*'):
                if file_path.is_file():
                    if pattern in file_path.name or pattern in str(file_path):
                        return True
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if pattern in content:
                                return True
                    except Exception:
                        continue
        
        return False
    
    def _calculate_confidence_scores(self):
        """计算置信度分数"""
        all_items = (
            self.tech_stack.languages +
            self.tech_stack.frameworks +
            self.tech_stack.databases +
            self.tech_stack.build_tools +
            self.tech_stack.testing_tools +
            self.tech_stack.deployment_tools +
            self.tech_stack.devops_tools +
            self.tech_stack.package_managers +
            self.tech_stack.web_servers
        )
        
        for item in all_items:
            if item not in self.tech_stack.confidence_scores:
                self.tech_stack.confidence_scores[item] = 0.5  # 默认置信度
    
    def _extract_version_info(self):
        """提取版本信息"""
        # 检查常见的版本文件
        version_files = [
            'package.json', 'pom.xml', 'build.gradle', 'Cargo.toml',
            'pyproject.toml', 'setup.py', 'composer.json', 'Gemfile'
        ]
        
        for version_file in version_files:
            file_path = self.repository_path / version_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        # 提取版本信息
                        version_patterns = [
                            r'"version":\s*"([^"]+)"',
                            r'version\s*=\s*"([^"]+)"',
                            r'version\s*=\s*([^\s]+)',
                            r'<version>([^<]+)</version>'
                        ]
                        
                        for pattern in version_patterns:
                            match = re.search(pattern, content)
                            if match:
                                self.tech_stack.version_info[version_file] = match.group(1)
                                break
                except Exception:
                    continue
    
    def _get_timestamp(self) -> str:
        """获取时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def _count_files_analyzed(self) -> int:
        """统计分析的文件数量"""
        count = 0
        for file_path in self.repository_path.rglob('*'):
            if file_path.is_file():
                count += 1
        return count
    
    def get_tech_stack_summary(self) -> Dict[str, Any]:
        """获取技术栈摘要"""
        return {
            'primary_language': self.tech_stack.languages[0] if self.tech_stack.languages else 'Unknown',
            'primary_framework': self.tech_stack.frameworks[0] if self.tech_stack.frameworks else 'None',
            'database': self.tech_stack.databases[0] if self.tech_stack.databases else 'None',
            'deployment': self.tech_stack.deployment_tools[0] if self.tech_stack.deployment_tools else 'None',
            'tech_categories': {
                'languages': len(self.tech_stack.languages),
                'frameworks': len(self.tech_stack.frameworks),
                'databases': len(self.tech_stack.databases),
                'build_tools': len(self.tech_stack.build_tools),
                'testing_tools': len(self.tech_stack.testing_tools),
                'deployment_tools': len(self.tech_stack.deployment_tools)
            },
            'complexity_score': self._calculate_complexity_score()
        }
    
    def _calculate_complexity_score(self) -> float:
        """计算技术栈复杂度分数"""
        weights = {
            'languages': 1.0,
            'frameworks': 1.5,
            'databases': 1.2,
            'build_tools': 0.8,
            'testing_tools': 0.6,
            'deployment_tools': 1.0,
            'devops_tools': 0.8,
            'package_managers': 0.4,
            'web_servers': 0.6
        }
        
        total_score = 0
        for category, weight in weights.items():
            count = len(getattr(self.tech_stack, category, []))
            total_score += count * weight
        
        return min(total_score, 10.0)  # 最大复杂度分数为10