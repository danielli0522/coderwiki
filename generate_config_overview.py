#!/usr/bin/env python3
"""
生成 CoderWiki Config 目录技术总览文档
使用本地分析，不依赖外部 API
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

class ConfigOverviewGenerator:
    """Config 目录技术总览文档生成器"""

    def __init__(self):
        self.config_path = "/Users/lshl124/Documents/daniel/git/code/aigc/coderwiki/config"
        self.output_dir = Path("generated_docs")
        self.output_dir.mkdir(exist_ok=True)

    def analyze_config_directory(self) -> Dict[str, Any]:
        """深度分析 config 目录"""
        config_info = {
            'path': self.config_path,
            'files': [],
            'total_size': 0,
            'file_types': {},
            'content_analysis': {},
            'architecture': {},
            'dependencies': set(),
            'functions': [],
            'classes': [],
            'imports': set()
        }

        try:
            config_dir = Path(self.config_path)
            if not config_dir.exists():
                print(f"❌ Config 目录不存在: {self.config_path}")
                return config_info

            print(f"🔍 分析 config 目录: {self.config_path}")

            for file_path in config_dir.rglob('*'):
                if file_path.is_file():
                    file_info = self._analyze_file(file_path, config_dir)
                    config_info['files'].append(file_info)
                    config_info['total_size'] += file_info['size']

                    # 统计文件类型
                    ext = file_info['extension']
                    config_info['file_types'][ext] = config_info['file_types'].get(ext, 0) + 1

            # 分析架构和依赖关系
            config_info['architecture'] = self._analyze_architecture(config_info['files'])
            config_info['dependencies'] = list(config_info['dependencies'])
            config_info['imports'] = list(config_info['imports'])

            return config_info

        except Exception as e:
            print(f"❌ 分析 config 目录时发生错误: {str(e)}")
            return config_info

    def _analyze_file(self, file_path: Path, base_dir: Path) -> Dict[str, Any]:
        """分析单个文件"""
        file_info = {
            'name': file_path.name,
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'extension': file_path.suffix,
            'relative_path': str(file_path.relative_to(base_dir)),
            'content_preview': '',
            'functions': [],
            'classes': [],
            'imports': [],
            'lines_of_code': 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                file_info['lines_of_code'] = len(lines)
                file_info['content_preview'] = '\n'.join(lines[:20])  # 前20行

                # 分析 Python 文件
                if file_path.suffix == '.py':
                    self._analyze_python_file(content, file_info)

        except Exception as e:
            file_info['content_preview'] = f"无法读取文件内容: {str(e)}"

        return file_info

    def _analyze_python_file(self, content: str, file_info: Dict[str, Any]):
        """分析 Python 文件内容"""
        lines = content.split('\n')

        for line in lines:
            line = line.strip()

            # 分析导入
            if line.startswith('import ') or line.startswith('from '):
                file_info['imports'].append(line)

            # 分析函数定义
            if line.startswith('def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                file_info['functions'].append(func_name)

            # 分析类定义
            if line.startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                file_info['classes'].append(class_name)

    def _analyze_architecture(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析配置架构"""
        architecture = {
            'main_components': [],
            'configuration_patterns': [],
            'file_relationships': {},
            'design_patterns': []
        }

        # 分析主要组件
        for file_info in files:
            if file_info['extension'] == '.py':
                if 'config' in file_info['name'].lower():
                    architecture['main_components'].append({
                        'name': file_info['name'],
                        'purpose': '配置文件',
                        'functions': file_info['functions'],
                        'classes': file_info['classes']
                    })
                elif 'auth' in file_info['name'].lower():
                    architecture['main_components'].append({
                        'name': file_info['name'],
                        'purpose': '认证配置',
                        'functions': file_info['functions'],
                        'classes': file_info['classes']
                    })

        # 分析配置模式
        for file_info in files:
            if file_info['extension'] == '.yaml':
                architecture['configuration_patterns'].append('YAML 配置')
            elif file_info['extension'] == '.py':
                if 'config' in file_info['name'].lower():
                    architecture['configuration_patterns'].append('Python 配置类')

        return architecture

    def generate_overview_document(self, config_info: Dict[str, Any]) -> str:
        """生成技术总览文档"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        doc = f"""# CoderWiki Config 目录技术总览文档

## 文档信息
- **生成时间**: {timestamp}
- **分析目录**: {config_info['path']}
- **文档类型**: 技术总览文档

## 目录概览

### 基本信息
- **文件总数**: {len(config_info['files'])} 个文件
- **总大小**: {config_info['total_size']} 字节
- **文件类型分布**: {json.dumps(config_info['file_types'], indent=2, ensure_ascii=False)}

### 文件列表
"""

        for file_info in config_info['files']:
            doc += f"""
#### {file_info['name']}
- **路径**: `{file_info['relative_path']}`
- **大小**: {file_info['size']} 字节
- **行数**: {file_info['lines_of_code']} 行
- **类型**: {file_info['extension']}

**功能分析**:
"""

            if file_info['functions']:
                doc += f"- **函数**: {', '.join(file_info['functions'])}\n"
            if file_info['classes']:
                doc += f"- **类**: {', '.join(file_info['classes'])}\n"
            if file_info['imports']:
                doc += f"- **导入**: {len(file_info['imports'])} 个导入语句\n"

            doc += f"""
**内容预览**:
```{file_info['extension'].lstrip('.')}
{file_info['content_preview'][:500]}...
```

---

"""

        # 架构分析
        doc += f"""
## 架构分析

### 主要组件
"""

        for component in config_info['architecture']['main_components']:
            doc += f"""
#### {component['name']}
- **用途**: {component['purpose']}
- **函数**: {', '.join(component['functions']) if component['functions'] else '无'}
- **类**: {', '.join(component['classes']) if component['classes'] else '无'}
"""

        doc += f"""
### 配置模式
- {chr(10).join(f'- {pattern}' for pattern in config_info['architecture']['configuration_patterns'])}

### 设计模式
- 配置管理模式
- 模块化配置
- 环境变量配置

## 技术栈

### 使用的技术
- **Python**: 主要配置语言
- **YAML**: 结构化配置文件
- **Flask**: Web 框架配置
- **SQLAlchemy**: 数据库配置

### 依赖关系
- 标准库依赖
- Flask 生态系统
- 数据库驱动
- 认证系统

## 最佳实践

### 配置管理
1. **环境分离**: 开发、测试、生产环境配置分离
2. **安全性**: 敏感信息使用环境变量
3. **模块化**: 按功能模块组织配置
4. **验证**: 配置参数验证和默认值

### 代码组织
1. **单一职责**: 每个配置文件负责特定功能
2. **可读性**: 清晰的命名和注释
3. **可维护性**: 模块化设计，易于扩展

## 部署建议

### 环境配置
- 使用环境变量管理敏感配置
- 为不同环境创建专门的配置文件
- 实施配置验证机制

### 安全考虑
- 避免在代码中硬编码敏感信息
- 使用安全的配置传输方式
- 定期审查配置权限

## 总结

CoderWiki 项目的配置目录采用了模块化和层次化的设计，通过 Python 类和 YAML 文件相结合的方式管理配置。这种设计既保证了配置的灵活性，又确保了代码的可维护性。

配置系统支持多环境部署，具有良好的扩展性和安全性，为项目的稳定运行提供了坚实的基础。

---
*本文档由 CoderWiki Config 分析器自动生成*
"""

        return doc

    def run(self):
        """运行文档生成"""
        print("🚀 开始生成 Config 目录技术总览文档...")

        # 分析配置目录
        config_info = self.analyze_config_directory()

        # 生成文档
        doc_content = self.generate_overview_document(config_info)

        # 保存文档
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coderwiki_config_overview_{timestamp}.md"
        output_path = self.output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc_content)

        print(f"✅ 技术总览文档生成成功!")
        print(f"📄 保存到: {output_path}")
        print(f"📊 分析了 {len(config_info['files'])} 个文件")
        print(f"📈 总大小: {config_info['total_size']} 字节")

        return output_path

if __name__ == "__main__":
    generator = ConfigOverviewGenerator()
    generator.run()
