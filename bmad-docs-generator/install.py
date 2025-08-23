#!/usr/bin/env python3
"""
BMAD Documentation Generator 扩展包安装脚本
"""

import os
import shutil
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List

class BMADDocsGeneratorInstaller:
    """BMAD文档生成器扩展包安装器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.expansion_dir = self.project_root / ".bmad-docs-generator"
        self.source_dir = Path(__file__).parent
        self.config_file = self.source_dir / "expansion-pack.yaml"

    def load_config(self) -> Dict[str, Any]:
        """加载扩展包配置"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def install(self) -> bool:
        """安装扩展包"""
        try:
            print("🚀 开始安装BMAD文档生成器扩展包...")

            # 1. 加载配置
            config = self.load_config()
            expansion_config = config['expansion-pack']

            print(f"📦 扩展包: {expansion_config['name']} v{expansion_config['version']}")

            # 2. 创建安装目录
            self.expansion_dir.mkdir(exist_ok=True)
            print(f"📁 安装目录: {self.expansion_dir}")

            # 3. 复制文件和目录
            self._copy_files(expansion_config)

            # 4. 创建配置文件
            self._create_config_files(expansion_config)

            # 5. 配置IDE集成
            self._configure_ide_integration(expansion_config)

            print("✅ BMAD文档生成器扩展包安装完成!")
            return True

        except Exception as e:
            print(f"❌ 安装失败: {e}")
            return False

    def _copy_files(self, config: Dict[str, Any]):
        """复制文件到安装目录"""
        print("\n📋 复制文件...")

        copy_items = config['install']['copy']
        for item in copy_items:
            source = self.source_dir / item
            target = self.expansion_dir / item

            if source.exists():
                if source.is_dir():
                    shutil.copytree(source, target, dirs_exist_ok=True)
                    print(f"  📁 复制目录: {item}")
                else:
                    shutil.copy2(source, target)
                    print(f"  📄 复制文件: {item}")
            else:
                print(f"  ⚠️  跳过不存在的项目: {item}")

    def _create_config_files(self, config: Dict[str, Any]):
        """创建配置文件"""
        print("\n⚙️  创建配置文件...")

        # 创建config.yaml
        config_yaml = {
            'bmad_docs_generator': {
                'version': config['version'],
                'name': config['name'],
                'description': config['description'],
                'install_path': str(self.expansion_dir),
                'subagents': config['subagents'],
                'workflows': config['workflows'],
                'tasks': config['tasks']
            }
        }

        config_file = self.expansion_dir / "config.yaml"
        with open(config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config_yaml, f, default_flow_style=False, allow_unicode=True)

        print(f"  📄 创建: config.yaml")

    def _configure_ide_integration(self, config: Dict[str, Any]):
        """配置IDE集成"""
        print("\n🛠️  配置IDE集成...")

        ide_config = config['ide-integration']

        # Claude Code集成
        if ide_config.get('claude-code', {}).get('enabled', False):
            self._configure_claude_code(ide_config['claude-code'])

        # Cursor集成
        if ide_config.get('cursor', {}).get('enabled', False):
            self._configure_cursor(ide_config['cursor'])

    def _configure_claude_code(self, claude_config: Dict[str, Any]):
        """配置Claude Code集成"""
        print("  🔧 配置Claude Code...")

        # 创建.claude目录
        claude_dir = self.project_root / ".claude"
        claude_dir.mkdir(exist_ok=True)

        # 读取现有配置或创建新配置
        settings_file = claude_dir / "settings.json"
        if settings_file.exists():
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        else:
            settings = {}

        # 更新配置
        claude_settings = claude_config['config']

        # 更新add_dirs
        if 'add_dirs' not in settings:
            settings['add_dirs'] = []

        bmad_docs_path = str(self.expansion_dir.absolute())
        if bmad_docs_path not in settings['add_dirs']:
            settings['add_dirs'].append(bmad_docs_path)

        # 更新其他设置
        for key, value in claude_settings.items():
            if key != 'add_dirs':  # add_dirs已经处理过了
                settings[key] = value

        # 添加环境变量
        if 'env' not in settings:
            settings['env'] = {}

        settings['env'].update({
            'BMAD_DOCS_GENERATOR_PATH': str(self.expansion_dir.absolute()),
            'BMAD_DOCS_ENABLED': 'true'
        })

        # 写入配置
        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        print(f"    ✅ Claude Code配置已更新: {settings_file}")

    def _configure_cursor(self, cursor_config: Dict[str, Any]):
        """配置Cursor集成"""
        print("  🔧 配置Cursor...")
        # TODO: 实现Cursor配置
        print("    ⏳ Cursor配置待实现")

    def uninstall(self) -> bool:
        """卸载扩展包"""
        try:
            print("🗑️  开始卸载BMAD文档生成器扩展包...")

            if self.expansion_dir.exists():
                shutil.rmtree(self.expansion_dir)
                print(f"  ✅ 删除安装目录: {self.expansion_dir}")

            # 清理Claude Code配置
            claude_settings_file = self.project_root / ".claude" / "settings.json"
            if claude_settings_file.exists():
                with open(claude_settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # 移除add_dirs中的BMAD路径
                if 'add_dirs' in settings:
                    bmad_docs_path = str(self.expansion_dir.absolute())
                    if bmad_docs_path in settings['add_dirs']:
                        settings['add_dirs'].remove(bmad_docs_path)

                # 移除环境变量
                if 'env' in settings:
                    env_vars_to_remove = ['BMAD_DOCS_GENERATOR_PATH', 'BMAD_DOCS_ENABLED']
                    for var in env_vars_to_remove:
                        if var in settings['env']:
                            del settings['env'][var]

                with open(claude_settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                print(f"  ✅ 清理Claude Code配置: {claude_settings_file}")

            print("✅ BMAD文档生成器扩展包卸载完成!")
            return True

        except Exception as e:
            print(f"❌ 卸载失败: {e}")
            return False

    def status(self) -> Dict[str, Any]:
        """检查安装状态"""
        status = {
            'installed': self.expansion_dir.exists(),
            'expansion_dir': str(self.expansion_dir),
            'config_file': str(self.expansion_dir / "config.yaml") if self.expansion_dir.exists() else None,
            'claude_config': str(self.project_root / ".claude" / "settings.json")
        }

        if status['installed']:
            # 检查关键文件
            key_files = [
                "agents/",
                "agent-teams/",
                "workflows/",
                "tasks/",
                "config.yaml"
            ]

            status['files'] = {}
            for file_path in key_files:
                full_path = self.expansion_dir / file_path
                status['files'][file_path] = full_path.exists()

        return status

def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='BMAD文档生成器扩展包安装器')
    parser.add_argument('action', choices=['install', 'uninstall', 'status'],
                       help='执行的操作')
    parser.add_argument('--project-root', default='.',
                       help='项目根目录路径')

    args = parser.parse_args()

    installer = BMADDocsGeneratorInstaller(args.project_root)

    if args.action == 'install':
        success = installer.install()
        exit(0 if success else 1)

    elif args.action == 'uninstall':
        success = installer.uninstall()
        exit(0 if success else 1)

    elif args.action == 'status':
        status = installer.status()
        print("📊 BMAD文档生成器扩展包状态:")
        print(f"  安装状态: {'✅ 已安装' if status['installed'] else '❌ 未安装'}")
        print(f"  安装目录: {status['expansion_dir']}")
        print(f"  配置文件: {status['config_file']}")
        print(f"  Claude配置: {status['claude_config']}")

        if status['installed'] and 'files' in status:
            print("\n📋 文件状态:")
            for file_path, exists in status['files'].items():
                status_icon = "✅" if exists else "❌"
                print(f"  {status_icon} {file_path}")

if __name__ == "__main__":
    main()
