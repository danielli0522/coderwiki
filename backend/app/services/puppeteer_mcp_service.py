"""
Puppeteer MCP Service Integration for document generation.
"""

import json
import logging
import requests
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import base64

logger = logging.getLogger(__name__)

@dataclass
class PuppeteerMetrics:
    """Puppeteer调用指标数据类"""
    response_time: float = 0.0
    cost_estimate: float = 0.0
    method: str = ""
    url: str = ""

class PuppeteerMCPService:
    """Puppeteer MCP服务集成类"""

    def __init__(self, server_url: str = "http://localhost", server_port: int = 3001):
        """
        初始化Puppeteer MCP服务

        Args:
            server_url: 服务器URL
            server_port: 服务器端口
        """
        self.base_url = f"{server_url}:{server_port}"
        self.timeout = 60  # 60秒超时
        self.max_retries = 3
        self.retry_delay = 2

    def check_connection(self) -> Dict[str, Any]:
        """检查与puppeteer-mcp-server的连接"""
        try:
            logger.info(f"检查puppeteer-mcp-server连接: {self.base_url}")

            health_url = f"{self.base_url}/health"
            response = requests.get(health_url, timeout=self.timeout)

            if response.status_code == 200:
                logger.info("✅ puppeteer-mcp-server连接成功")
                return {
                    'success': True,
                    'status': 'connected',
                    'url': self.base_url
                }
            else:
                logger.warning(f"⚠️ puppeteer-mcp-server响应异常: {response.status_code}")
                return {
                    'success': False,
                    'status': 'error',
                    'url': self.base_url,
                    'error': f"HTTP {response.status_code}"
                }

        except requests.exceptions.ConnectionError:
            logger.error(f"❌ 无法连接到puppeteer-mcp-server: {self.base_url}")
            return {
                'success': False,
                'status': 'connection_error',
                'url': self.base_url,
                'error': 'Connection refused'
            }
        except Exception as e:
            logger.error(f"❌ puppeteer-mcp-server连接错误: {str(e)}")
            return {
                'success': False,
                'status': 'error',
                'url': self.base_url,
                'error': str(e)
            }

    def take_screenshot(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        截取网页截图

        Args:
            url: 要截图的网页URL
            options: 截图选项

        Returns:
            包含截图结果的字典
        """
        try:
            start_time = time.time()

            # 默认选项
            default_options = {
                "width": 1280,
                "height": 720,
                "fullPage": False,
                "quality": 80
            }

            if options:
                default_options.update(options)

            # 构建请求数据
            request_data = {
                "method": "screenshot",
                "params": {
                    "url": url,
                    "options": default_options
                }
            }

            logger.info(f"发送截图请求: {url}")

            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/mcp",
                json=request_data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time

                # 创建指标对象
                metrics = PuppeteerMetrics(
                    response_time=response_time,
                    method='screenshot',
                    url=url
                )

                return {
                    'success': True,
                    'screenshot_path': result.get('result', {}).get('screenshot_path'),
                    'url': url,
                    'options': default_options,
                    'metrics': metrics.__dict__,
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.error(f"截图请求失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            logger.error(f"截图处理错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_pdf(self, url: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        生成PDF文档

        Args:
            url: 要生成PDF的网页URL
            options: PDF生成选项

        Returns:
            包含PDF生成结果的字典
        """
        try:
            start_time = time.time()

            # 默认选项
            default_options = {
                "format": "A4",
                "printBackground": True,
                "margin": {
                    "top": "1cm",
                    "right": "1cm",
                    "bottom": "1cm",
                    "left": "1cm"
                }
            }

            if options:
                default_options.update(options)

            # 构建请求数据
            request_data = {
                "method": "pdf_generation",
                "params": {
                    "url": url,
                    "options": default_options
                }
            }

            logger.info(f"发送PDF生成请求: {url}")

            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/mcp",
                json=request_data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time

                # 创建指标对象
                metrics = PuppeteerMetrics(
                    response_time=response_time,
                    method='pdf_generation',
                    url=url
                )

                return {
                    'success': True,
                    'pdf_path': result.get('result', {}).get('pdf_path'),
                    'url': url,
                    'options': default_options,
                    'metrics': metrics.__dict__,
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.error(f"PDF生成请求失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            logger.error(f"PDF生成处理错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def scrape_content(self, url: str, selectors: List[str] = None) -> Dict[str, Any]:
        """
        抓取网页内容

        Args:
            url: 要抓取的网页URL
            selectors: CSS选择器列表

        Returns:
            包含抓取结果的字典
        """
        try:
            start_time = time.time()

            # 默认选择器
            default_selectors = ["body", "main", "article", ".content"]
            if selectors:
                default_selectors = selectors

            # 构建请求数据
            request_data = {
                "method": "web_scraping",
                "params": {
                    "url": url,
                    "selectors": default_selectors
                }
            }

            logger.info(f"发送内容抓取请求: {url}")

            # 发送请求
            response = requests.post(
                f"{self.base_url}/api/mcp",
                json=request_data,
                timeout=self.timeout
            )

            if response.status_code == 200:
                result = response.json()
                response_time = time.time() - start_time

                # 创建指标对象
                metrics = PuppeteerMetrics(
                    response_time=response_time,
                    method='web_scraping',
                    url=url
                )

                return {
                    'success': True,
                    'content': result.get('result', {}).get('content'),
                    'url': url,
                    'selectors': default_selectors,
                    'metrics': metrics.__dict__,
                    'metadata': result.get('metadata', {})
                }
            else:
                logger.error(f"内容抓取请求失败: {response.status_code}")
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}"
                }

        except Exception as e:
            logger.error(f"内容抓取处理错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def enhance_document_with_screenshots(self, document_content: str, urls: List[str]) -> Dict[str, Any]:
        """
        使用截图增强文档内容

        Args:
            document_content: 原始文档内容
            urls: 要截图的URL列表

        Returns:
            包含增强结果的字典
        """
        try:
            logger.info(f"使用截图增强文档，URL数量: {len(urls)}")

            enhanced_content = document_content
            screenshots = []

            for i, url in enumerate(urls):
                logger.info(f"处理URL {i+1}/{len(urls)}: {url}")

                # 截取截图
                screenshot_result = self.take_screenshot(url, {
                    "width": 1200,
                    "height": 800,
                    "fullPage": False
                })

                if screenshot_result['success']:
                    screenshot_path = screenshot_result['screenshot_path']
                    screenshots.append({
                        'url': url,
                        'path': screenshot_path,
                        'index': i
                    })

                    # 在文档中添加截图引用
                    screenshot_markdown = f"\n\n![截图 {i+1}]({screenshot_path})\n*图 {i+1}: {url}*\n"
                    enhanced_content += screenshot_markdown
                else:
                    logger.warning(f"截图失败: {url} - {screenshot_result['error']}")

            return {
                'success': True,
                'enhanced_content': enhanced_content,
                'screenshots': screenshots,
                'original_length': len(document_content),
                'enhanced_length': len(enhanced_content)
            }

        except Exception as e:
            logger.error(f"文档增强处理错误: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_server_info(self) -> Dict[str, Any]:
        """获取服务器信息"""
        try:
            info_url = f"{self.base_url}/info"
            response = requests.get(info_url, timeout=self.timeout)

            if response.status_code == 200:
                return {
                    'success': True,
                    'info': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_available_tools(self) -> Dict[str, Any]:
        """获取可用工具列表"""
        try:
            tools_url = f"{self.base_url}/tools"
            response = requests.get(tools_url, timeout=self.timeout)

            if response.status_code == 200:
                return {
                    'success': True,
                    'tools': response.json()
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
