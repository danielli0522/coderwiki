"""
服务编排器
统一管理和协调各种服务的初始化、健康检查、依赖关系和资源管理
"""

import logging
import threading
import time
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass
from flask import current_app
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """服务状态枚举"""
    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    FAILED = "failed"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class ServiceInfo:
    """服务信息数据类"""
    name: str
    service_instance: Any
    status: ServiceStatus
    health_check_func: Optional[Callable] = None
    dependencies: List[str] = None
    last_health_check: Optional[datetime] = None
    initialization_time: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.metadata is None:
            self.metadata = {}


class ServiceOrchestrator:
    """服务编排器"""
    
    def __init__(self):
        """初始化服务编排器"""
        self.services: Dict[str, ServiceInfo] = {}
        self.health_check_interval = timedelta(minutes=5)
        self.max_error_count = 3
        self.initialization_timeout = timedelta(minutes=2)
        self._health_check_thread = None
        self._shutdown_event = threading.Event()
        self._lock = threading.RLock()
        
        # 注册默认服务
        self._register_core_services()
    
    def _register_core_services(self):
        """注册核心服务"""
        try:
            # 注册智能文档服务
            from .smart_doc_service import SmartDocumentService
            self.register_service(
                name='smart_document_service',
                service_class=SmartDocumentService,
                health_check_func=self._check_smart_doc_service_health,
                dependencies=['credential_validator', 'workflow_monitor']
            )
            
            # 注册工作流监控服务
            from .workflow_monitor import workflow_monitor
            self.register_service(
                name='workflow_monitor',
                service_instance=workflow_monitor,
                health_check_func=self._check_workflow_monitor_health
            )
            
            # 注册凭证验证服务
            from .credential_validator import credential_validator
            self.register_service(
                name='credential_validator',
                service_instance=credential_validator,
                health_check_func=self._check_credential_validator_health
            )
            
            logger.info("Core services registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to register core services: {e}")
    
    def register_service(self, name: str, service_class: type = None, service_instance: Any = None,
                        health_check_func: Optional[Callable] = None, dependencies: List[str] = None,
                        metadata: Dict[str, Any] = None) -> bool:
        """
        注册服务
        
        Args:
            name: 服务名称
            service_class: 服务类（如果需要创建实例）
            service_instance: 服务实例（如果已存在）
            health_check_func: 健康检查函数
            dependencies: 依赖的其他服务列表
            metadata: 服务元数据
            
        Returns:
            注册是否成功
        """
        try:
            with self._lock:
                if name in self.services:
                    logger.warning(f"Service {name} already registered, updating...")
                
                # 创建或使用现有服务实例
                if service_instance is None and service_class is not None:
                    service_instance = service_class()
                elif service_instance is None:
                    raise ValueError(f"Either service_class or service_instance must be provided for {name}")
                
                service_info = ServiceInfo(
                    name=name,
                    service_instance=service_instance,
                    status=ServiceStatus.UNINITIALIZED,
                    health_check_func=health_check_func,
                    dependencies=dependencies or [],
                    metadata=metadata or {}
                )
                
                self.services[name] = service_info
                logger.info(f"Service {name} registered successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to register service {name}: {e}")
            return False
    
    def initialize_services(self) -> Dict[str, bool]:
        """
        按依赖顺序初始化所有服务
        
        Returns:
            初始化结果字典
        """
        results = {}
        
        try:
            with self._lock:
                # 计算初始化顺序
                initialization_order = self._calculate_initialization_order()
                
                logger.info(f"Initializing services in order: {initialization_order}")
                
                for service_name in initialization_order:
                    if service_name in self.services:
                        results[service_name] = self._initialize_single_service(service_name)
                        
                        # 如果关键服务初始化失败，记录错误但继续
                        if not results[service_name]:
                            logger.error(f"Failed to initialize service: {service_name}")
                    else:
                        logger.warning(f"Service {service_name} not found in registry")
                        results[service_name] = False
                
                # 启动健康检查
                self._start_health_check_thread()
                
                logger.info(f"Service initialization completed. Results: {results}")
                return results
                
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            return {name: False for name in self.services.keys()}
    
    def _calculate_initialization_order(self) -> List[str]:
        """
        计算服务初始化顺序（拓扑排序）
        
        Returns:
            初始化顺序列表
        """
        try:
            # 简单的拓扑排序实现
            in_degree = {name: 0 for name in self.services.keys()}
            
            # 计算每个节点的入度
            for service_name, service_info in self.services.items():
                for dependency in service_info.dependencies:
                    if dependency in in_degree:
                        in_degree[service_name] += 1
            
            # 找到所有入度为0的节点
            queue = [name for name, degree in in_degree.items() if degree == 0]
            result = []
            
            while queue:
                current = queue.pop(0)
                result.append(current)
                
                # 减少依赖当前节点的其他节点的入度
                for service_name, service_info in self.services.items():
                    if current in service_info.dependencies:
                        in_degree[service_name] -= 1
                        if in_degree[service_name] == 0:
                            queue.append(service_name)
            
            # 检查是否存在循环依赖
            if len(result) != len(self.services):
                remaining = [name for name in self.services.keys() if name not in result]
                logger.warning(f"Possible circular dependencies detected: {remaining}")
                result.extend(remaining)  # 添加剩余的服务
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to calculate initialization order: {e}")
            return list(self.services.keys())
    
    def _initialize_single_service(self, service_name: str) -> bool:
        """
        初始化单个服务
        
        Args:
            service_name: 服务名称
            
        Returns:
            初始化是否成功
        """
        try:
            service_info = self.services[service_name]
            service_info.status = ServiceStatus.INITIALIZING
            service_info.initialization_time = datetime.utcnow()
            
            logger.info(f"Initializing service: {service_name}")
            
            # 检查依赖服务是否已初始化
            for dependency in service_info.dependencies:
                if dependency in self.services:
                    dep_service = self.services[dependency]
                    if dep_service.status not in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                        logger.warning(f"Dependency {dependency} for {service_name} is not healthy")
            
            # 如果服务有初始化方法，调用它
            service_instance = service_info.service_instance
            if hasattr(service_instance, 'initialize') and callable(getattr(service_instance, 'initialize')):
                service_instance.initialize()
            
            # 执行健康检查
            if self._perform_health_check(service_name):
                service_info.status = ServiceStatus.HEALTHY
                logger.info(f"Service {service_name} initialized successfully")
                return True
            else:
                service_info.status = ServiceStatus.UNHEALTHY
                logger.error(f"Service {service_name} failed health check after initialization")
                return False
                
        except Exception as e:
            service_info.status = ServiceStatus.FAILED
            service_info.last_error = str(e)
            service_info.error_count += 1
            logger.error(f"Failed to initialize service {service_name}: {e}")
            return False
    
    def get_service(self, name: str) -> Optional[Any]:
        """
        获取服务实例
        
        Args:
            name: 服务名称
            
        Returns:
            服务实例或None
        """
        try:
            with self._lock:
                if name in self.services:
                    service_info = self.services[name]
                    if service_info.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]:
                        return service_info.service_instance
                    else:
                        logger.warning(f"Service {name} is not healthy (status: {service_info.status.value})")
                        return None
                else:
                    logger.warning(f"Service {name} not found")
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get service {name}: {e}")
            return None
    
    @contextmanager
    def get_service_context(self, name: str):
        """
        获取服务的上下文管理器
        
        Args:
            name: 服务名称
            
        Yields:
            服务实例
        """
        service = self.get_service(name)
        if service is None:
            raise ValueError(f"Service {name} is not available")
        
        try:
            yield service
        finally:
            # 在这里可以添加清理逻辑
            pass
    
    def get_service_status(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取服务状态
        
        Args:
            name: 服务名称
            
        Returns:
            服务状态信息
        """
        try:
            with self._lock:
                if name in self.services:
                    service_info = self.services[name]
                    return {
                        'name': service_info.name,
                        'status': service_info.status.value,
                        'last_health_check': service_info.last_health_check.isoformat() if service_info.last_health_check else None,
                        'initialization_time': service_info.initialization_time.isoformat() if service_info.initialization_time else None,
                        'error_count': service_info.error_count,
                        'last_error': service_info.last_error,
                        'dependencies': service_info.dependencies,
                        'metadata': service_info.metadata
                    }
                else:
                    return None
                    
        except Exception as e:
            logger.error(f"Failed to get service status for {name}: {e}")
            return None
    
    def get_all_service_status(self) -> Dict[str, Dict[str, Any]]:
        """
        获取所有服务状态
        
        Returns:
            所有服务状态字典
        """
        try:
            with self._lock:
                return {
                    name: self.get_service_status(name)
                    for name in self.services.keys()
                }
                
        except Exception as e:
            logger.error(f"Failed to get all service status: {e}")
            return {}
    
    def _start_health_check_thread(self):
        """启动健康检查线程"""
        try:
            if self._health_check_thread is None or not self._health_check_thread.is_alive():
                self._health_check_thread = threading.Thread(
                    target=self._health_check_loop,
                    name="ServiceHealthCheck",
                    daemon=True
                )
                self._health_check_thread.start()
                logger.info("Health check thread started")
            
        except Exception as e:
            logger.error(f"Failed to start health check thread: {e}")
    
    def _health_check_loop(self):
        """健康检查循环"""
        while not self._shutdown_event.is_set():
            try:
                self._perform_all_health_checks()
                self._shutdown_event.wait(self.health_check_interval.total_seconds())
                
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                self._shutdown_event.wait(30)  # 出错时短暂等待
    
    def _perform_all_health_checks(self):
        """执行所有服务的健康检查"""
        try:
            with self._lock:
                for service_name in self.services.keys():
                    self._perform_health_check(service_name)
                    
        except Exception as e:
            logger.error(f"Failed to perform health checks: {e}")
    
    def _perform_health_check(self, service_name: str) -> bool:
        """
        执行单个服务的健康检查
        
        Args:
            service_name: 服务名称
            
        Returns:
            健康检查是否通过
        """
        try:
            service_info = self.services[service_name]
            service_info.last_health_check = datetime.utcnow()
            
            # 如果有自定义健康检查函数，使用它
            if service_info.health_check_func:
                health_result = service_info.health_check_func(service_info.service_instance)
                
                if health_result:
                    if service_info.status in [ServiceStatus.UNHEALTHY, ServiceStatus.DEGRADED]:
                        service_info.status = ServiceStatus.HEALTHY
                        service_info.error_count = 0
                        logger.info(f"Service {service_name} recovered")
                    return True
                else:
                    service_info.error_count += 1
                    if service_info.error_count >= self.max_error_count:
                        service_info.status = ServiceStatus.UNHEALTHY
                    else:
                        service_info.status = ServiceStatus.DEGRADED
                    return False
            else:
                # 默认健康检查：检查服务实例是否存在
                if service_info.service_instance is not None:
                    service_info.status = ServiceStatus.HEALTHY
                    return True
                else:
                    service_info.status = ServiceStatus.UNHEALTHY
                    return False
                    
        except Exception as e:
            service_info.last_error = str(e)
            service_info.error_count += 1
            if service_info.error_count >= self.max_error_count:
                service_info.status = ServiceStatus.UNHEALTHY
            else:
                service_info.status = ServiceStatus.DEGRADED
            logger.error(f"Health check failed for service {service_name}: {e}")
            return False
    
    def shutdown(self):
        """关闭服务编排器"""
        try:
            logger.info("Shutting down service orchestrator...")
            self._shutdown_event.set()
            
            with self._lock:
                # 更新所有服务状态
                for service_info in self.services.values():
                    service_info.status = ServiceStatus.SHUTTING_DOWN
                
                # 等待健康检查线程结束
                if self._health_check_thread and self._health_check_thread.is_alive():
                    self._health_check_thread.join(timeout=10)
                
                # 调用服务的关闭方法
                for service_name, service_info in self.services.items():
                    try:
                        if hasattr(service_info.service_instance, 'shutdown') and callable(getattr(service_info.service_instance, 'shutdown')):
                            service_info.service_instance.shutdown()
                    except Exception as e:
                        logger.error(f"Error shutting down service {service_name}: {e}")
            
            logger.info("Service orchestrator shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during service orchestrator shutdown: {e}")
    
    # 健康检查函数
    
    def _check_smart_doc_service_health(self, service_instance) -> bool:
        """检查智能文档服务健康状态"""
        try:
            # 检查初始化错误
            if hasattr(service_instance, 'initialization_error') and service_instance.initialization_error:
                return False
            
            # 检查客户端是否存在
            if hasattr(service_instance, 'claude_client') and hasattr(service_instance, 'bmad_orchestrator'):
                return service_instance.claude_client is not None and service_instance.bmad_orchestrator is not None
            
            return True
            
        except Exception as e:
            logger.error(f"Smart document service health check error: {e}")
            return False
    
    def _check_workflow_monitor_health(self, service_instance) -> bool:
        """检查工作流监控服务健康状态"""
        try:
            # 检查日志目录是否可写
            if hasattr(service_instance, 'log_directory') and service_instance.log_directory:
                return service_instance.log_directory.exists() and service_instance.log_directory.is_dir()
            
            return True
            
        except Exception as e:
            logger.error(f"Workflow monitor health check error: {e}")
            return False
    
    def _check_credential_validator_health(self, service_instance) -> bool:
        """检查凭证验证服务健康状态"""
        try:
            # 检查验证缓存是否正常
            if hasattr(service_instance, 'validation_cache'):
                return isinstance(service_instance.validation_cache, dict)
            
            return True
            
        except Exception as e:
            logger.error(f"Credential validator health check error: {e}")
            return False


# 全局服务编排器实例
service_orchestrator = ServiceOrchestrator()