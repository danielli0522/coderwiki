"""
技术栈分析器测试
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from app.utils.tech_stack_analyzer import TechStackAnalyzer, TechStackInfo, FrameworkDetection

class TestTechStackAnalyzer:
    """技术栈分析器测试"""
    
    def setup_method(self):
        """设置测试环境"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.analyzer = TechStackAnalyzer(str(self.temp_dir))
    
    def teardown_method(self):
        """清理测试环境"""
        shutil.rmtree(self.temp_dir)
    
    def test_init_analyzer(self):
        """测试分析器初始化"""
        assert self.analyzer.repository_path == self.temp_dir
        assert isinstance(self.analyzer.tech_stack, TechStackInfo)
        assert len(self.analyzer.language_patterns) > 0
        assert len(self.analyzer.framework_patterns) > 0
    
    def test_analyze_empty_repository(self):
        """测试空仓库分析"""
        result = self.analyzer.analyze()
        
        assert isinstance(result, dict)
        assert 'languages' in result
        assert 'frameworks' in result
        assert 'databases' in result
        assert 'confidence_scores' in result
        assert 'analysis_metadata' in result
        
        # 空仓库应该返回空列表
        assert result['languages'] == []
        assert result['frameworks'] == []
        assert result['databases'] == []
    
    def test_analyze_python_project(self):
        """测试Python项目分析"""
        # 创建Python项目文件
        (self.temp_dir / 'main.py').write_text('print("Hello World")')
        (self.temp_dir / 'requirements.txt').write_text('flask==2.0.1\nrequests==2.25.1')
        (self.temp_dir / 'app.py').write_text('''
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello, World!"
''')
        
        result = self.analyzer.analyze()
        
        assert 'Python' in result['languages']
        assert 'Flask' in result['frameworks']
        assert 'pip' in result['package_managers']
        assert 'Python' in result['confidence_scores']
        assert result['confidence_scores']['Python'] >= 0.5
    
    def test_analyze_javascript_project(self):
        """测试JavaScript项目分析"""
        # 创建JavaScript项目文件
        (self.temp_dir / 'package.json').write_text('''
{
  "name": "test-project",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.17.1",
    "react": "^17.0.2"
  }
}
''')
        (self.temp_dir / 'index.js').write_text('''
const express = require('express');
const app = express();

app.get('/', (req, res) => {
    res.send('Hello World!');
});
''')
        (self.temp_dir / 'App.jsx').write_text('''
import React from 'react';

function App() {
    return <h1>Hello React!</h1>;
}
''')
        
        result = self.analyzer.analyze()
        
        assert 'JavaScript' in result['languages']
        assert 'Express' in result['frameworks']
        assert 'React' in result['frameworks']
        assert 'npm' in result['package_managers']
    
    def test_analyze_java_project(self):
        """测试Java项目分析"""
        # 创建Java项目文件
        java_dir = self.temp_dir / 'src' / 'main' / 'java' / 'com' / 'example'
        java_dir.mkdir(parents=True)
        
        (java_dir / 'Application.java').write_text('''
package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
''')
        
        (self.temp_dir / 'pom.xml').write_text('''
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>demo</artifactId>
    <version>0.0.1-SNAPSHOT</version>
    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>2.5.0</version>
    </parent>
</project>
''')
        
        result = self.analyzer.analyze()
        
        assert 'Java' in result['languages']
        assert 'Spring Boot' in result['frameworks']
        assert 'Maven' in result['build_tools']
    
    def test_analyze_go_project(self):
        """测试Go项目分析"""
        # 创建Go项目文件
        (self.temp_dir / 'go.mod').write_text('module example.com/myproject')
        
        go_dir = self.temp_dir / 'cmd' / 'server'
        go_dir.mkdir(parents=True)
        
        (go_dir / 'main.go').write_text('''
package main

import (
    "fmt"
    "net/http"
    
    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.Default()
    r.GET("/", func(c *gin.Context) {
        c.JSON(http.StatusOK, gin.H{"message": "Hello World"})
    })
    r.Run()
}
''')
        
        result = self.analyzer.analyze()
        
        assert 'Go' in result['languages']
        assert 'Gin' in result['frameworks']
        assert 'go mod' in result['package_managers']
    
    def test_analyze_docker_project(self):
        """测试Docker项目分析"""
        # 创建Docker项目文件
        (self.temp_dir / 'Dockerfile').write_text('''
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
''')
        
        (self.temp_dir / 'docker-compose.yml').write_text('''
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: myapp
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
''')
        
        result = self.analyzer.analyze()
        
        assert 'Docker' in result['deployment_tools']
        assert 'PostgreSQL' in result['databases']
    
    def test_analyze_database_project(self):
        """测试数据库项目分析"""
        # 创建数据库相关文件
        (self.temp_dir / 'requirements.txt').write_text('psycopg2-binary==2.8.6')
        (self.temp_dir / 'config.py').write_text('''
DATABASE_URL = "postgresql://user:password@localhost/mydb"
''')
        
        migrations_dir = self.temp_dir / 'migrations'
        migrations_dir.mkdir()
        
        (migrations_dir / '001_initial.sql').write_text('''
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);
''')
        
        result = self.analyzer.analyze()
        
        assert 'PostgreSQL' in result['databases']
    
    def test_analyze_testing_frameworks(self):
        """测试测试框架分析"""
        # 创建测试文件
        test_dir = self.temp_dir / 'tests'
        test_dir.mkdir()
        
        (test_dir / 'test_app.py').write_text('''
import pytest
from app import app

def test_home():
    response = app.test_client().get('/')
    assert response.status_code == 200
''')
        
        (self.temp_dir / 'requirements.txt').write_text('pytest==6.2.4')
        
        result = self.analyzer.analyze()
        
        assert 'pytest' in result['testing_tools']
    
    def test_analyze_ci_cd_tools(self):
        """测试CI/CD工具分析"""
        # 创建CI/CD文件
        github_workflows = self.temp_dir / '.github' / 'workflows'
        github_workflows.mkdir(parents=True)
        
        (github_workflows / 'test.yml').write_text('''
name: Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
''')
        
        result = self.analyzer.analyze()
        
        assert 'CI/CD Pipeline' in result['devops_tools']
    
    def test_calculate_framework_confidence(self):
        """测试框架置信度计算"""
        # 创建Flask项目
        (self.temp_dir / 'app.py').write_text('from flask import Flask')
        (self.temp_dir / 'requirements.txt').write_text('flask==2.0.1')
        
        confidence = self.analyzer._calculate_framework_confidence(['flask', 'app.py'])
        
        assert confidence > 0.3
        assert confidence <= 1.0
    
    def test_calculate_pattern_score(self):
        """测试模式匹配分数计算"""
        # 创建匹配文件
        (self.temp_dir / 'main.py').write_text('import requests')
        
        score = self.analyzer._calculate_pattern_score(['requests'])
        
        assert score > 0
        assert score <= 1.0
    
    def test_has_matching_patterns(self):
        """测试模式匹配检查"""
        # 创建匹配文件
        (self.temp_dir / 'package.json').write_text('{"name": "test"}')
        
        assert self.analyzer._has_matching_patterns(['package.json'])
        assert not self.analyzer._has_matching_patterns(['nonexistent'])
    
    def test_extract_version_info(self):
        """测试版本信息提取"""
        # 创建package.json
        (self.temp_dir / 'package.json').write_text('''
{
  "name": "test-project",
  "version": "1.2.3"
}
''')
        
        self.analyzer._extract_version_info()
        
        assert 'package.json' in self.analyzer.tech_stack.version_info
        assert self.analyzer.tech_stack.version_info['package.json'] == '1.2.3'
    
    def test_get_tech_stack_summary(self):
        """测试技术栈摘要生成"""
        # 创建一个完整的项目
        (self.temp_dir / 'main.py').write_text('print("Hello")')
        (self.temp_dir / 'requirements.txt').write_text('flask==2.0.1')
        (self.temp_dir / 'Dockerfile').write_text('FROM python:3.9')
        
        result = self.analyzer.analyze()
        summary = self.analyzer.get_tech_stack_summary()
        
        assert isinstance(summary, dict)
        assert 'primary_language' in summary
        assert 'primary_framework' in summary
        assert 'tech_categories' in summary
        assert 'complexity_score' in summary
        
        assert summary['primary_language'] == 'Python'
        assert summary['tech_categories']['languages'] > 0
        assert summary['complexity_score'] > 0
    
    def test_complexity_score_calculation(self):
        """测试复杂度分数计算"""
        # 创建复杂项目
        (self.temp_dir / 'main.py').write_text('print("Hello")')
        (self.temp_dir / 'requirements.txt').write_text('flask==2.0.1')
        (self.temp_dir / 'Dockerfile').write_text('FROM python:3.9')
        (self.temp_dir / 'package.json').write_text('{"name": "test"}')
        
        result = self.analyzer.analyze()
        complexity_score = self.analyzer._calculate_complexity_score()
        
        assert complexity_score > 0
        assert complexity_score <= 10.0
    
    def test_analysis_metadata(self):
        """测试分析元数据"""
        # 创建简单项目
        (self.temp_dir / 'main.py').write_text('print("Hello")')
        
        result = self.analyzer.analyze()
        
        assert 'analysis_metadata' in result
        assert 'repository_path' in result['analysis_metadata']
        assert 'analysis_timestamp' in result['analysis_metadata']
        assert 'total_files_analyzed' in result['analysis_metadata']
        
        assert result['analysis_metadata']['repository_path'] == str(self.temp_dir)
        assert result['analysis_metadata']['total_files_analyzed'] >= 1
    
    def test_multiple_languages_detection(self):
        """测试多语言检测"""
        # 创建多语言项目
        (self.temp_dir / 'main.py').write_text('print("Hello")')
        (self.temp_dir / 'script.js').write_text('console.log("Hello")')
        (self.temp_dir / 'style.css').write_text('body { color: red; }')
        
        result = self.analyzer.analyze()
        
        assert 'Python' in result['languages']
        assert 'JavaScript' in result['languages']
        # CSS可能不被识别为编程语言，但会被分析
    
    def test_confidence_scores(self):
        """测试置信度分数"""
        # 创建项目
        (self.temp_dir / 'main.py').write_text('from flask import Flask')
        
        result = self.analyzer.analyze()
        
        assert 'confidence_scores' in result
        assert isinstance(result['confidence_scores'], dict)
        
        # 检查主要技术栈的置信度
        for tech in result['languages'] + result['frameworks']:
            assert tech in result['confidence_scores']
            assert 0 <= result['confidence_scores'][tech] <= 1.0
    
    def test_error_handling(self):
        """测试错误处理"""
        # 创建一个会导致错误的文件（权限问题）
        error_file = self.temp_dir / 'error_file.txt'
        error_file.write_text('test')
        
        # 模拟权限错误
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = self.analyzer.analyze()
            
            # 即使有错误，分析也应该完成
            assert isinstance(result, dict)
            assert 'languages' in result
    
    def test_large_file_handling(self):
        """测试大文件处理"""
        # 创建大文件
        large_file = self.temp_dir / 'large_file.py'
        large_content = 'print("Hello")\n' * 10000  # 10万行
        large_file.write_text(large_content)
        
        result = self.analyzer.analyze()
        
        # 应该能够处理大文件而不崩溃
        assert isinstance(result, dict)
        assert 'Python' in result['languages']

class TestTechStackInfo:
    """技术栈信息测试"""
    
    def test_tech_stack_info_creation(self):
        """测试技术栈信息创建"""
        tech_info = TechStackInfo(
            languages=['Python', 'JavaScript'],
            frameworks=['Flask', 'React'],
            databases=['PostgreSQL'],
            build_tools=['Webpack'],
            testing_tools=['pytest'],
            deployment_tools=['Docker'],
            devops_tools=['CI/CD Pipeline'],
            package_managers=['npm', 'pip'],
            web_servers=['Nginx'],
            other_tools=['Other'],
            confidence_scores={'Python': 0.9},
            version_info={'package.json': '1.0.0'}
        )
        
        assert tech_info.languages == ['Python', 'JavaScript']
        assert tech_info.frameworks == ['Flask', 'React']
        assert tech_info.databases == ['PostgreSQL']
        assert tech_info.confidence_scores == {'Python': 0.9}
        assert tech_info.version_info == {'package.json': '1.0.0'}

class TestFrameworkDetection:
    """框架检测结果测试"""
    
    def test_framework_detection_creation(self):
        """测试框架检测结果创建"""
        detection = FrameworkDetection(
            name='Flask',
            category='Web Frameworks',
            version='2.0.1',
            confidence=0.9,
            evidence=['flask', 'app.py']
        )
        
        assert detection.name == 'Flask'
        assert detection.category == 'Web Frameworks'
        assert detection.version == '2.0.1'
        assert detection.confidence == 0.9
        assert detection.evidence == ['flask', 'app.py']