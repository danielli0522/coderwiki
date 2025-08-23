"""
Security scanner for dependency and code analysis.
"""

import os
import json
import re
import hashlib
import base64
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class SecuritySeverity(Enum):
    """Security vulnerability severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityCategory(Enum):
    """Security vulnerability categories."""
    VULNERABILITY = "vulnerability"
    MALICIOUS_CODE = "malicious_code"
    DATA_LEAK = "data_leak"
    WEAK_CRYPTO = "weak_crypto"
    INSECURE_CONFIG = "insecure_config"
    DEPRECATED = "deprecated"
    LICENSE_VIOLATION = "license_violation"
    PERFORMANCE = "performance"


@dataclass
class SecurityIssue:
    """Security issue information."""
    id: str
    title: str
    description: str
    severity: SecuritySeverity
    category: SecurityCategory
    affected_package: str
    affected_version: str
    fixed_version: Optional[str]
    cve_id: Optional[str]
    cvss_score: Optional[float]
    references: List[str]
    remediation: str
    confidence: float
    source_file: Optional[str]
    
    def __post_init__(self):
        if self.references is None:
            self.references = []


@dataclass
class SecurityScanResult:
    """Security scan result."""
    issues: List[SecurityIssue]
    scan_summary: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    metadata: Dict[str, Any]


class SecurityScanner:
    """Security scanner for dependencies and code."""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.vulnerability_databases = [
            "https://api.osv.dev/v1/query",
            "https://pypi.org/pypi/{}/json",
            "https://registry.npmjs.org/{}"
        ]
        
        self.malicious_patterns = [
            (r'eval\s*\(', "Use of eval() can lead to code injection"),
            (r'document\.write\s*\(', "document.write() can lead to XSS"),
            (r'innerHTML\s*=', "innerHTML can lead to XSS"),
            (r'exec\s*\(', "exec() can lead to code injection"),
            (r'system\s*\(', "system() can lead to command injection"),
            (r'passthru\s*\(', "passthru() can lead to command injection"),
            (r'shell_exec\s*\(', "shell_exec() can lead to command injection"),
            (r'backticks\s*`', "Backticks can lead to command injection"),
            (r'\bpassword\s*=\s*[\'"][^\'"]{1,10}[\'"]', "Hardcoded password detected"),
            (r'\bapi_key\s*=\s*[\'"][^\'"]{10,}[\'"]', "Hardcoded API key detected"),
            (r'\bsecret\s*=\s*[\'"][^\'"]{10,}[\'"]', "Hardcoded secret detected"),
            (r'\btoken\s*=\s*[\'"][^\'"]{10,}[\'"]', "Hardcoded token detected")
        ]
        
        self.weak_crypto_patterns = [
            (r'md5\s*\(', "MD5 is cryptographically weak"),
            (r'sha1\s*\(', "SHA1 is cryptographically weak"),
            (r'des_\w*\s*\(', "DES is cryptographically weak"),
            (r'rc4\s*\(', "RC4 is cryptographically weak"),
            (r'base64_decode\s*\(', "Base64 decoding without validation"),
            (r'hash\s*\(\s*[\'"]md5[\'"]', "MD5 hash usage"),
            (r'hash\s*\(\s*[\'"]sha1[\'"]', "SHA1 hash usage")
        ]
        
        self.insecure_config_patterns = [
            (r'debug\s*=\s*true', "Debug mode enabled in production"),
            (r'DEBUG\s*=\s*True', "Debug mode enabled in production"),
            (r'allow_url_include\s*=\s*on', "PHP allow_url_include enabled"),
            (r'file_uploads\s*=\s*on', "File uploads enabled without restrictions"),
            (r'expose_php\s*=\s*on', "PHP expose_php enabled"),
            (r'display_errors\s*=\s*on', "PHP display_errors enabled")
        ]
        
        self.scan_config = {
            'max_workers': 4,
            'timeout': 30,
            'cache_results': True,
            'scan_secrets': True,
            'scan_vulnerabilities': True,
            'scan_code_patterns': True,
            'scan_configs': True
        }
    
    def scan_repository(self) -> SecurityScanResult:
        """Perform comprehensive security scan of the repository."""
        if not self.repository_path.exists():
            return SecurityScanResult(
                issues=[],
                scan_summary={'error': f'Repository path does not exist: {self.repository_path}'},
                risk_assessment={},
                recommendations=[],
                metadata={'error': 'Repository not found'}
            )
        
        issues = []
        scan_summary = {
            'total_files': 0,
            'scanned_files': 0,
            'scan_duration': 0,
            'vulnerabilities_found': 0,
            'malicious_patterns_found': 0,
            'secrets_found': 0,
            'weak_crypto_found': 0,
            'insecure_configs_found': 0
        }
        
        start_time = time.time()
        
        try:
            # Scan for secrets and sensitive data
            if self.scan_config['scan_secrets']:
                secret_issues = self._scan_for_secrets()
                issues.extend(secret_issues)
                scan_summary['secrets_found'] = len(secret_issues)
            
            # Scan for dependency vulnerabilities
            if self.scan_config['scan_vulnerabilities']:
                vuln_issues = self._scan_for_vulnerabilities()
                issues.extend(vuln_issues)
                scan_summary['vulnerabilities_found'] = len(vuln_issues)
            
            # Scan for malicious code patterns
            if self.scan_config['scan_code_patterns']:
                code_issues = self._scan_code_patterns()
                issues.extend(code_issues)
                scan_summary['malicious_patterns_found'] = len([i for i in code_issues if i.category == SecurityCategory.MALICIOUS_CODE])
                scan_summary['weak_crypto_found'] = len([i for i in code_issues if i.category == SecurityCategory.WEAK_CRYPTO])
            
            # Scan for insecure configurations
            if self.scan_config['scan_configs']:
                config_issues = self._scan_insecure_configs()
                issues.extend(config_issues)
                scan_summary['insecure_configs_found'] = len(config_issues)
            
            # Calculate scan duration
            scan_summary['scan_duration'] = time.time() - start_time
            
            # Generate risk assessment
            risk_assessment = self._assess_risks(issues)
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(issues, risk_assessment)
            
            # Create scan result
            result = SecurityScanResult(
                issues=issues,
                scan_summary=scan_summary,
                risk_assessment=risk_assessment,
                recommendations=recommendations,
                metadata={
                    'scan_timestamp': self._get_timestamp(),
                    'repository_path': str(self.repository_path),
                    'scanner_version': '1.0.0'
                }
            )
            
            return result
            
        except Exception as e:
            return SecurityScanResult(
                issues=[],
                scan_summary={'error': f'Scan failed: {str(e)}'},
                risk_assessment={},
                recommendations=[],
                metadata={'error': str(e)}
            )
    
    def _scan_for_secrets(self) -> List[SecurityIssue]:
        """Scan for hardcoded secrets and sensitive data."""
        issues = []
        
        # Common secret patterns
        secret_patterns = [
            (r'(?i)api[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']', "API key detected"),
            (r'(?i)secret[_-]?key\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']', "Secret key detected"),
            (r'(?i)password\s*[:=]\s*["\']([^"\']{4,})["\']', "Password detected"),
            (r'(?i)token\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']', "Token detected"),
            (r'(?i)private[_-]?key\s*[:=]\s*["\']([^"\']{20,})["\']', "Private key detected"),
            (r'(?i)aws[_-]?access[_-]?key[_-]?id\s*[:=]\s*["\']([A-Z0-9]{20})["\']', "AWS access key detected"),
            (r'(?i)aws[_-]?secret[_-]?access[_-]?key\s*[:=]\s*["\']([A-Za-z0-9/+=]{40})["\']', "AWS secret key detected"),
            (r'(?i)github[_-]?token\s*[:=]\s*["\']([a-zA-Z0-9]{20,})["\']', "GitHub token detected"),
            (r'(?i)database[_-]?url\s*[:=]\s*["\']([^"\']+)["\']', "Database URL detected"),
            (r'(?i)connection[_-]?string\s*[:=]\s*["\']([^"\']+)["\']', "Connection string detected")
        ]
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip binary files and common non-secret files
                if self._should_skip_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            for pattern, description in secret_patterns:
                                matches = re.finditer(pattern, line)
                                for match in matches:
                                    # Create hash of the secret for identification
                                    secret_hash = hashlib.sha256(match.group(1).encode()).hexdigest()[:16]
                                    
                                    issues.append(SecurityIssue(
                                        id=f"SECRET-{secret_hash}",
                                        title="Hardcoded secret detected",
                                        description=f"{description}: {match.group(1)[:20]}...",
                                        severity=SecuritySeverity.HIGH,
                                        category=SecurityCategory.DATA_LEAK,
                                        affected_package=file_path.name,
                                        affected_version="N/A",
                                        fixed_version=None,
                                        cve_id=None,
                                        cvss_score=7.5,
                                        references=[],
                                        remediation="Remove hardcoded secrets and use environment variables or secret management systems.",
                                        confidence=0.9,
                                        source_file=str(file_path)
                                    ))
                
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return issues
    
    def _scan_for_vulnerabilities(self) -> List[SecurityIssue]:
        """Scan for known vulnerabilities in dependencies."""
        issues = []
        
        # Try to find dependency files
        dependency_files = [
            'package.json', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'pipfile', 'pyproject.toml',
            'pom.xml', 'build.gradle', 'go.mod',
            'cargo.toml', 'composer.json', 'gemfile'
        ]
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.lower() in [f.lower() for f in dependency_files]:
                    file_path = Path(root) / file
                    try:
                        file_issues = self._scan_file_for_vulnerabilities(file_path)
                        issues.extend(file_issues)
                    except Exception as e:
                        # Log error but continue scanning
                        continue
        
        return issues
    
    def _scan_file_for_vulnerabilities(self, file_path: Path) -> List[SecurityIssue]:
        """Scan a specific file for vulnerabilities."""
        issues = []
        
        try:
            # Common vulnerable packages database (simplified)
            vulnerable_packages = {
                # JavaScript/Node.js
                'lodash': {'version': '<4.17.21', 'cve': 'CVE-2021-23337', 'severity': 'high'},
                'express': {'version': '<4.18.2', 'cve': 'CVE-2022-24999', 'severity': 'high'},
                'react': {'version': '<16.13.1', 'cve': 'CVE-2021-38645', 'severity': 'medium'},
                'moment': {'version': '<2.29.4', 'cve': 'CVE-2022-31129', 'severity': 'medium'},
                'axios': {'version': '<0.21.2', 'cve': 'CVE-2021-3749', 'severity': 'medium'},
                
                # Python
                'django': {'version': '<3.2.18', 'cve': 'CVE-2022-34265', 'severity': 'high'},
                'flask': {'version': '<2.0.3', 'cve': 'CVE-2022-26943', 'severity': 'medium'},
                'requests': {'version': '<2.25.1', 'cve': 'CVE-2021-33503', 'severity': 'medium'},
                'pillow': {'version': '<8.3.2', 'cve': 'CVE-2021-34552', 'severity': 'high'},
                
                # Java
                'log4j': {'version': '<2.17.0', 'cve': 'CVE-2021-44228', 'severity': 'critical'},
                'spring-boot': {'version': '<2.5.12', 'cve': 'CVE-2021-22096', 'severity': 'high'},
                
                # Go
                'gin': {'version': '<1.7.8', 'cve': 'CVE-2021-44716', 'severity': 'medium'},
            }
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
                for package, vuln_info in vulnerable_packages.items():
                    if package.lower() in content.lower():
                        # Try to extract version
                        version_match = re.search(rf'{re.escape(package)}[\'"\s]*(>=|==|<=|>|<)([0-9.]+)', content, re.IGNORECASE)
                        if version_match:
                            version = version_match.group(2)
                            
                            # Check if version is vulnerable
                            if self._is_version_vulnerable(version, vuln_info['version']):
                                issues.append(SecurityIssue(
                                    id=f"VULN-{package.replace('-', '_').upper()}-{version.replace('.', '_')}",
                                    title=f"Vulnerability in {package}",
                                    description=f"Package {package} version {version} is vulnerable to {vuln_info['cve']}",
                                    severity=self._string_to_severity(vuln_info['severity']),
                                    category=SecurityCategory.VULNERABILITY,
                                    affected_package=package,
                                    affected_version=version,
                                    fixed_version="N/A",  # Would need to be determined from database
                                    cve_id=vuln_info['cve'],
                                    cvss_score=self._severity_to_cvss(vuln_info['severity']),
                                    references=[f"https://cve.mitre.org/cgi-bin/cvename.cgi?name={vuln_info['cve']}"],
                                    remediation=f"Update {package} to a fixed version",
                                    confidence=0.8,
                                    source_file=str(file_path)
                                ))
        
        except Exception as e:
            pass
        
        return issues
    
    def _scan_code_patterns(self) -> List[SecurityIssue]:
        """Scan code for malicious patterns and weak cryptography."""
        issues = []
        
        # Combine all patterns
        all_patterns = []
        all_patterns.extend([(p, SecurityCategory.MALICIOUS_CODE) for p, _ in self.malicious_patterns])
        all_patterns.extend([(p, SecurityCategory.WEAK_CRYPTO) for p, _ in self.weak_crypto_patterns])
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                file_path = Path(root) / file
                
                # Skip binary files
                if self._should_skip_file(file_path):
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        
                        for line_num, line in enumerate(lines, 1):
                            for pattern, category in all_patterns:
                                matches = re.finditer(pattern, line, re.IGNORECASE)
                                for match in matches:
                                    # Find the description
                                    description = ""
                                    for p, desc in self.malicious_patterns:
                                        if p == pattern:
                                            description = desc
                                            break
                                    
                                    if not description:
                                        for p, desc in self.weak_crypto_patterns:
                                            if p == pattern:
                                                description = desc
                                                break
                                    
                                    # Determine severity based on pattern
                                    severity = SecuritySeverity.MEDIUM
                                    if 'password' in pattern.lower() or 'key' in pattern.lower():
                                        severity = SecuritySeverity.HIGH
                                    elif 'eval' in pattern.lower() or 'exec' in pattern.lower():
                                        severity = SecuritySeverity.HIGH
                                    
                                    issues.append(SecurityIssue(
                                        id=f"PATTERN-{category.value.upper()}-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                                        title=f"Potentially insecure code pattern: {description}",
                                        description=f"Found {description} at line {line_num}",
                                        severity=severity,
                                        category=category,
                                        affected_package=file_path.name,
                                        affected_version="N/A",
                                        fixed_version=None,
                                        cve_id=None,
                                        cvss_score=self._severity_to_cvss(severity.value),
                                        references=[],
                                        remediation=f"Review and refactor the code to avoid {description}",
                                        confidence=0.7,
                                        source_file=str(file_path)
                                    ))
                
                except (UnicodeDecodeError, PermissionError):
                    continue
        
        return issues
    
    def _scan_insecure_configs(self) -> List[SecurityIssue]:
        """Scan for insecure configuration files."""
        issues = []
        
        config_files = [
            'config.py', 'settings.py', 'app.config', 'web.config',
            '.env', 'php.ini', 'apache.conf', 'nginx.conf'
        ]
        
        for root, dirs, files in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for file in files:
                if file.lower() in [f.lower() for f in config_files]:
                    file_path = Path(root) / file
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            for line_num, line in enumerate(lines, 1):
                                for pattern, description in self.insecure_config_patterns:
                                    if re.search(pattern, line, re.IGNORECASE):
                                        issues.append(SecurityIssue(
                                            id=f"CONFIG-{hashlib.md5(pattern.encode()).hexdigest()[:8]}",
                                            title=f"Insecure configuration: {description}",
                                            description=f"Found {description} at line {line_num}",
                                            severity=SecuritySeverity.MEDIUM,
                                            category=SecurityCategory.INSECURE_CONFIG,
                                            affected_package=file_path.name,
                                            affected_version="N/A",
                                            fixed_version=None,
                                            cve_id=None,
                                            cvss_score=6.5,
                                            references=[],
                                            remediation="Review and update configuration settings",
                                            confidence=0.8,
                                            source_file=str(file_path)
                                        ))
                    
                    except (UnicodeDecodeError, PermissionError):
                        continue
        
        return issues
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Determine if a file should be skipped during scanning."""
        # Skip binary files
        binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.a', '.lib', '.o', '.obj',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar',
            '.mp3', '.mp4', 'avi', 'mov', 'wmv', 'flv',
            '.class', '.jar', '.war', '.ear'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return True
        
        # Skip large files (>1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except OSError:
            return True
        
        # Skip common non-secret files
        skip_patterns = [
            r'^package-lock\.json$',
            r'^yarn\.lock$',
            r'^\.git/',
            r'^node_modules/',
            r'^\.venv/',
            r'^venv/',
            r'^env/',
            r'^\.env\.',
            r'^\.log$',
            r'\.min\.js$',
            r'\.min\.css$'
        ]
        
        file_str = str(file_path)
        for pattern in skip_patterns:
            if re.search(pattern, file_str):
                return True
        
        return False
    
    def _is_version_vulnerable(self, version: str, vulnerable_range: str) -> bool:
        """Check if a version is within the vulnerable range."""
        # Simplified version comparison
        # In a real implementation, you'd use a proper version comparison library
        
        def version_tuple(v):
            return tuple(map(int, v.split('.')))
        
        try:
            if vulnerable_range.startswith('<'):
                max_version = vulnerable_range[1:]
                return version_tuple(version) < version_tuple(max_version)
            elif vulnerable_range.startswith('<='):
                max_version = vulnerable_range[2:]
                return version_tuple(version) <= version_tuple(max_version)
            elif vulnerable_range.startswith('>'):
                min_version = vulnerable_range[1:]
                return version_tuple(version) > version_tuple(min_version)
            elif vulnerable_range.startswith('>='):
                min_version = vulnerable_range[2:]
                return version_tuple(version) >= version_tuple(min_version)
        except (ValueError, IndexError):
            return False
        
        return False
    
    def _string_to_severity(self, severity_str: str) -> SecuritySeverity:
        """Convert string severity to enum."""
        severity_map = {
            'critical': SecuritySeverity.CRITICAL,
            'high': SecuritySeverity.HIGH,
            'medium': SecuritySeverity.MEDIUM,
            'low': SecuritySeverity.LOW,
            'info': SecuritySeverity.INFO
        }
        return severity_map.get(severity_str.lower(), SecuritySeverity.MEDIUM)
    
    def _severity_to_cvss(self, severity_str: str) -> float:
        """Convert severity to CVSS score."""
        cvss_map = {
            'critical': 9.0,
            'high': 7.5,
            'medium': 5.5,
            'low': 3.5,
            'info': 0.0
        }
        return cvss_map.get(severity_str.lower(), 5.0)
    
    def _assess_risks(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Assess overall security risks."""
        risk_assessment = {
            'overall_risk_level': 'low',
            'critical_issues': 0,
            'high_issues': 0,
            'medium_issues': 0,
            'low_issues': 0,
            'risk_by_category': {},
            'risk_by_file': {},
            'total_risk_score': 0.0
        }
        
        # Count issues by severity
        for issue in issues:
            if issue.severity == SecuritySeverity.CRITICAL:
                risk_assessment['critical_issues'] += 1
            elif issue.severity == SecuritySeverity.HIGH:
                risk_assessment['high_issues'] += 1
            elif issue.severity == SecuritySeverity.MEDIUM:
                risk_assessment['medium_issues'] += 1
            elif issue.severity == SecuritySeverity.LOW:
                risk_assessment['low_issues'] += 1
        
        # Count issues by category
        for issue in issues:
            category = issue.category.value
            if category not in risk_assessment['risk_by_category']:
                risk_assessment['risk_by_category'][category] = 0
            risk_assessment['risk_by_category'][category] += 1
        
        # Count issues by file
        for issue in issues:
            if issue.source_file:
                if issue.source_file not in risk_assessment['risk_by_file']:
                    risk_assessment['risk_by_file'][issue.source_file] = 0
                risk_assessment['risk_by_file'][issue.source_file] += 1
        
        # Calculate overall risk score
        risk_assessment['total_risk_score'] = (
            risk_assessment['critical_issues'] * 10 +
            risk_assessment['high_issues'] * 7 +
            risk_assessment['medium_issues'] * 4 +
            risk_assessment['low_issues'] * 1
        )
        
        # Determine overall risk level
        if risk_assessment['critical_issues'] > 0 or risk_assessment['total_risk_score'] > 50:
            risk_assessment['overall_risk_level'] = 'critical'
        elif risk_assessment['high_issues'] > 2 or risk_assessment['total_risk_score'] > 30:
            risk_assessment['overall_risk_level'] = 'high'
        elif risk_assessment['medium_issues'] > 5 or risk_assessment['total_risk_score'] > 15:
            risk_assessment['overall_risk_level'] = 'medium'
        elif risk_assessment['total_risk_score'] > 5:
            risk_assessment['overall_risk_level'] = 'low'
        else:
            risk_assessment['overall_risk_level'] = 'info'
        
        return risk_assessment
    
    def _generate_security_recommendations(self, issues: List[SecurityIssue], risk_assessment: Dict[str, Any]) -> List[str]:
        """Generate security recommendations based on findings."""
        recommendations = []
        
        # Overall risk recommendations
        if risk_assessment['overall_risk_level'] == 'critical':
            recommendations.append("CRITICAL: Immediate action required. Multiple critical security issues found.")
        elif risk_assessment['overall_risk_level'] == 'high':
            recommendations.append("HIGH: Address security issues as soon as possible.")
        
        # Critical issues recommendations
        if risk_assessment['critical_issues'] > 0:
            recommendations.append(f"Address {risk_assessment['critical_issues']} critical security issues immediately.")
        
        # High severity issues recommendations
        if risk_assessment['high_issues'] > 0:
            recommendations.append(f"Address {risk_assessment['high_issues']} high severity security issues.")
        
        # Category-specific recommendations
        category_recommendations = {
            'vulnerability': "Update vulnerable packages to their latest secure versions.",
            'malicious_code': "Review and refactor potentially insecure code patterns.",
            'data_leak': "Remove hardcoded secrets and use proper secret management.",
            'weak_crypto': "Replace weak cryptographic algorithms with secure alternatives.",
            'insecure_config': "Review and update configuration settings for security."
        }
        
        for category, count in risk_assessment['risk_by_category'].items():
            if category in category_recommendations and count > 0:
                recommendations.append(category_recommendations[category])
        
        # General recommendations
        recommendations.extend([
            "Implement regular security scanning in your CI/CD pipeline.",
            "Use automated dependency management tools.",
            "Implement secret management and avoid hardcoding credentials.",
            "Keep all dependencies up to date.",
            "Follow secure coding practices and perform code reviews."
        ])
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()