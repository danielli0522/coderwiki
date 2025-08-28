"""
Project pattern recognition service.
"""

import os
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import json
import re


class ArchitecturePattern(Enum):
    """Architecture pattern types."""
    MONOLITH = "monolith"
    MICROSERVICE = "microservice"
    SERVERLESS = "serverless"
    EVENT_DRIVEN = "event_driven"
    LAYERED = "layered"
    HEXAGONAL = "hexagonal"
    CLEAN = "clean"
    MVC = "mvc"
    MVVM = "mvvm"
    REPOSITORY = "repository"
    CQRS = "cqrs"
    UNKNOWN = "unknown"


@dataclass
class PatternEvidence:
    """Evidence for architecture pattern detection."""
    pattern: ArchitecturePattern
    score: float
    evidence: List[str]
    confidence: float


class ProjectPatternRecognizer:
    """Service for recognizing project architecture patterns."""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.pattern_indicators = {
            ArchitecturePattern.MONOLITH: {
                'files': ['app.py', 'main.py', 'index.js', 'server.js', 'application.py'],
                'dirs': ['app', 'src', 'lib'],
                'patterns': [r'^app\.', r'^main\.', r'^server\.'],
                'weight': 1.0
            },
            ArchitecturePattern.MICROSERVICE: {
                'files': ['docker-compose.yml', 'docker-compose.yaml'],
                'dirs': ['services', 'microservices', 'apis'],
                'patterns': [r'.*service.*', r'.*api.*', r'.*microservice.*'],
                'weight': 1.0
            },
            ArchitecturePattern.SERVERLESS: {
                'files': ['serverless.yml', 'serverless.yaml', 'template.yaml'],
                'dirs': ['functions', 'lambdas', 'handlers'],
                'patterns': [r'^handler', r'^lambda', r'^function'],
                'weight': 1.0
            },
            ArchitecturePattern.EVENT_DRIVEN: {
                'files': ['events.py', 'eventbus.py', 'message_queue.py'],
                'dirs': ['events', 'handlers', 'subscribers'],
                'patterns': [r'.*event.*', r'.*handler.*', r'.*subscriber.*'],
                'weight': 0.8
            },
            ArchitecturePattern.LAYERED: {
                'dirs': ['controllers', 'services', 'repositories', 'domain'],
                'patterns': [r'controller$', r'service$', r'repository$', r'domain$'],
                'weight': 0.9
            },
            ArchitecturePattern.HEXAGONAL: {
                'dirs': ['domain', 'application', 'infrastructure', 'interfaces'],
                'patterns': [r'domain$', r'application$', r'infrastructure$', r'interface$'],
                'weight': 0.8
            },
            ArchitecturePattern.CLEAN: {
                'dirs': ['entities', 'use_cases', 'interface_adapters', 'frameworks_drivers'],
                'patterns': [r'entity$', r'use_case$', r'adapter$', r'framework$'],
                'weight': 0.8
            },
            ArchitecturePattern.MVC: {
                'dirs': ['models', 'views', 'controllers'],
                'patterns': [r'model$', r'view$', r'controller$'],
                'weight': 0.9
            },
            ArchitecturePattern.MVVM: {
                'dirs': ['models', 'views', 'viewmodels'],
                'patterns': [r'model$', r'view$', r'viewmodel$'],
                'weight': 0.8
            },
            ArchitecturePattern.REPOSITORY: {
                'dirs': ['repositories', 'domain', 'infrastructure'],
                'patterns': [r'repository$', r'domain$', r'infrastructure$'],
                'weight': 0.7
            },
            ArchitecturePattern.CQRS: {
                'dirs': ['commands', 'queries', 'handlers'],
                'patterns': [r'command$', r'query$', r'handler$'],
                'weight': 0.7
            }
        }
    
    def analyze_patterns(self) -> Dict[str, Any]:
        """Analyze method compatible with CodeAnalysisEngine interface."""
        return self.recognize_patterns()
    
    def recognize_patterns(self) -> Dict[str, Any]:
        """Recognize architecture patterns in the project."""
        if not self.repository_path.exists():
            return {'error': f'Repository path does not exist: {self.repository_path}'}
        
        # Collect all evidence
        all_evidence = []
        file_structure = self._analyze_file_structure()
        directory_structure = self._analyze_directory_structure()
        
        # Score each pattern
        pattern_scores = {}
        for pattern, indicators in self.pattern_indicators.items():
            evidence = self._collect_pattern_evidence(pattern, indicators, file_structure, directory_structure)
            if evidence:
                all_evidence.append(evidence)
                pattern_scores[pattern] = evidence
        
        # Determine dominant pattern
        dominant_pattern = self._determine_dominant_pattern(pattern_scores)
        
        # Analyze organization quality
        organization_analysis = self._analyze_organization_quality(file_structure, directory_structure)
        
        return {
            'dominant_pattern': dominant_pattern.pattern.value if dominant_pattern else 'unknown',
            'dominant_confidence': dominant_pattern.confidence if dominant_pattern else 0,
            'all_patterns': [e.pattern.value for e in all_evidence],
            'pattern_scores': {e.pattern.value: e.score for e in all_evidence},
            'pattern_evidence': {e.pattern.value: e.evidence for e in all_evidence},
            'organization_analysis': organization_analysis,
            'recommendations': self._generate_recommendations(dominant_pattern, organization_analysis),
            'metadata': {
                'total_files': file_structure['total_files'],
                'total_directories': directory_structure['total_directories'],
                'analysis_timestamp': self._get_timestamp()
            }
        }
    
    def _analyze_file_structure(self) -> Dict[str, Any]:
        """Analyze file structure for pattern recognition."""
        files = []
        total_files = 0
        
        for root, dirs, filenames in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for filename in filenames:
                if not filename.startswith('.'):
                    file_path = Path(root) / filename
                    files.append({
                        'name': filename,
                        'path': str(file_path),
                        'extension': file_path.suffix.lower(),
                        'relative_path': str(file_path.relative_to(self.repository_path))
                    })
                    total_files += 1
        
        return {
            'files': files,
            'total_files': total_files,
            'file_names': [f['name'] for f in files]
        }
    
    def _analyze_directory_structure(self) -> Dict[str, Any]:
        """Analyze directory structure for pattern recognition."""
        directories = []
        total_directories = 0
        
        for root, dirs, _ in os.walk(self.repository_path):
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            
            for dirname in dirs:
                dir_path = Path(root) / dirname
                directories.append({
                    'name': dirname,
                    'path': str(dir_path),
                    'relative_path': str(dir_path.relative_to(self.repository_path))
                })
                total_directories += 1
        
        return {
            'directories': directories,
            'total_directories': total_directories,
            'directory_names': [d['name'] for d in directories]
        }
    
    def _collect_pattern_evidence(self, pattern: ArchitecturePattern, indicators: Dict[str, Any], 
                                 file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> Optional[PatternEvidence]:
        """Collect evidence for a specific pattern."""
        evidence = []
        score = 0.0
        
        # Check for specific files
        if 'files' in indicators:
            for file_pattern in indicators['files']:
                if file_pattern in file_structure['file_names']:
                    evidence.append(f'file_found:{file_pattern}')
                    score += 0.3
        
        # Check for specific directories
        if 'dirs' in indicators:
            for dir_pattern in indicators['dirs']:
                if dir_pattern in directory_structure['directory_names']:
                    evidence.append(f'directory_found:{dir_pattern}')
                    score += 0.4
        
        # Check for pattern matches in file names
        if 'patterns' in indicators:
            for pattern_regex in indicators['patterns']:
                regex = re.compile(pattern_regex, re.IGNORECASE)
                
                # Check files
                for file_info in file_structure['files']:
                    if regex.search(file_info['name']) or regex.search(file_info['relative_path']):
                        evidence.append(f'file_pattern_match:{file_info["name"]}')
                        score += 0.2
                
                # Check directories
                for dir_info in directory_structure['directories']:
                    if regex.search(dir_info['name']) or regex.search(dir_info['relative_path']):
                        evidence.append(f'directory_pattern_match:{dir_info["name"]}')
                        score += 0.3
        
        # Apply weight
        score *= indicators.get('weight', 1.0)
        
        # Calculate confidence based on evidence strength
        confidence = min(score, 1.0)
        
        if score > 0.1:  # Only return if there's some evidence
            return PatternEvidence(
                pattern=pattern,
                score=score,
                evidence=evidence,
                confidence=confidence
            )
        
        return None
    
    def _determine_dominant_pattern(self, pattern_scores: Dict[ArchitecturePattern, PatternEvidence]) -> Optional[PatternEvidence]:
        """Determine the dominant architecture pattern."""
        if not pattern_scores:
            return None
        
        # Find pattern with highest score
        dominant = max(pattern_scores.values(), key=lambda x: x.score)
        
        # Check if it's significantly better than others
        second_best = None
        for pattern, evidence in pattern_scores.items():
            if pattern != dominant.pattern:
                if second_best is None or evidence.score > second_best.score:
                    second_best = evidence
        
        # If there's a tie or close call, reduce confidence
        if second_best and dominant.score - second_best.score < 0.2:
            dominant.confidence *= 0.7
        
        return dominant
    
    def _analyze_organization_quality(self, file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the organization quality of the project."""
        quality_metrics = {
            'structure_score': 0.0,
            'naming_consistency': 0.0,
            'separation_of_concerns': 0.0,
            'documentation_level': 0.0,
            'overall_grade': 'unknown'
        }
        
        # Analyze structure score
        structure_score = self._calculate_structure_score(file_structure, directory_structure)
        quality_metrics['structure_score'] = structure_score
        
        # Analyze naming consistency
        naming_score = self._analyze_naming_consistency(file_structure, directory_structure)
        quality_metrics['naming_consistency'] = naming_score
        
        # Analyze separation of concerns
        separation_score = self._analyze_separation_of_concerns(file_structure, directory_structure)
        quality_metrics['separation_of_concerns'] = separation_score
        
        # Analyze documentation level
        doc_score = self._analyze_documentation_level(file_structure)
        quality_metrics['documentation_level'] = doc_score
        
        # Calculate overall grade
        overall_score = (structure_score + naming_score + separation_score + doc_score) / 4
        quality_metrics['overall_score'] = overall_score
        quality_metrics['overall_grade'] = self._score_to_grade(overall_score)
        
        return quality_metrics
    
    def _calculate_structure_score(self, file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> float:
        """Calculate structure organization score."""
        score = 0.0
        
        # Check for logical organization
        top_level_dirs = [d['name'] for d in directory_structure['directories'] if '/' not in d['relative_path']]
        
        # Good organization indicators
        good_indicators = ['src', 'app', 'lib', 'test', 'docs', 'config']
        bad_indicators = ['temp', 'tmp', 'backup', 'old']
        
        good_count = sum(1 for indicator in good_indicators if indicator in top_level_dirs)
        bad_count = sum(1 for indicator in bad_indicators if indicator in top_level_dirs)
        
        score += min(good_count * 0.2, 0.6)
        score -= min(bad_count * 0.3, 0.3)
        
        # Check for reasonable directory depth
        max_depth = max(len(d['relative_path'].split('/')) for d in directory_structure['directories'])
        if max_depth <= 4:
            score += 0.2
        elif max_depth <= 6:
            score += 0.1
        else:
            score -= 0.1
        
        return max(0, min(1, score))
    
    def _analyze_naming_conventions(self, file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> float:
        """Analyze naming convention consistency."""
        # This is a simplified version - in practice, you'd want more sophisticated analysis
        score = 0.5  # Base score
        
        # Check for consistent casing
        file_names = [f['name'] for f in file_structure['files']]
        dir_names = [d['name'] for d in directory_structure['directories']]
        
        # Check if most names follow consistent patterns
        snake_case_count = sum(1 for name in file_names + dir_names if '_' in name and name.islower())
        camel_case_count = sum(1 for name in file_names + dir_names if re.match(r'^[a-z][a-zA-Z0-9]*$', name))
        
        total_names = len(file_names) + len(dir_names)
        if total_names > 0:
            consistency = max(snake_case_count, camel_case_count) / total_names
            score += consistency * 0.3
        
        return min(1, score)
    
    def _analyze_naming_consistency(self, file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> float:
        """Analyze naming consistency (alias for naming_conventions)."""
        return self._analyze_naming_conventions(file_structure, directory_structure)
    
    def _analyze_separation_of_concerns(self, file_structure: Dict[str, Any], directory_structure: Dict[str, Any]) -> float:
        """Analyze separation of concerns."""
        score = 0.0
        
        # Check for clear separation of concerns
        separation_indicators = [
            ('models', 'views', 'controllers'),  # MVC
            ('domain', 'application', 'infrastructure'),  # Layered
            ('controllers', 'services', 'repositories'),  # Service layer
            ('entities', 'use_cases', 'interface_adapters'),  # Clean
            ('commands', 'queries', 'handlers')  # CQRS
        ]
        
        for indicator_set in separation_indicators:
            found_count = sum(1 for indicator in indicator_set if indicator in [d['name'] for d in directory_structure['directories']])
            if found_count >= 2:
                score += 0.3
        
        return min(1, score)
    
    def _analyze_documentation_level(self, file_structure: Dict[str, Any]) -> float:
        """Analyze documentation level."""
        score = 0.0
        
        # Check for documentation files
        doc_files = [f for f in file_structure['files'] if f['name'].lower().endswith(('.md', '.txt', '.rst'))]
        readme_files = [f for f in file_structure['files'] if f['name'].lower() in ['readme.md', 'readme.txt', 'readme']]
        
        if readme_files:
            score += 0.4
        
        if len(doc_files) > 1:
            score += 0.3
        
        # Check for doc directories
        doc_dirs = [d for d in directory_structure['directories'] if d['name'].lower() in ['docs', 'documentation', 'doc']]
        if doc_dirs:
            score += 0.3
        
        return min(1, score)
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to grade."""
        if score >= 0.9:
            return 'excellent'
        elif score >= 0.8:
            return 'good'
        elif score >= 0.7:
            return 'fair'
        elif score >= 0.6:
            return 'poor'
        else:
            return 'very_poor'
    
    def _generate_recommendations(self, dominant_pattern: Optional[PatternEvidence], 
                                 organization_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []
        
        if not dominant_pattern:
            recommendations.append("Consider adopting a clear architecture pattern to improve code organization.")
            return recommendations
        
        # Pattern-specific recommendations
        if dominant_pattern.pattern == ArchitecturePattern.MONOLITH:
            if organization_analysis['overall_score'] < 0.7:
                recommendations.append("Consider refactoring monolith into modules or services.")
        
        elif dominant_pattern.pattern == ArchitecturePattern.MICROSERVICE:
            recommendations.append("Ensure proper service boundaries and communication patterns.")
            recommendations.append("Implement service discovery and configuration management.")
        
        elif dominant_pattern.pattern == ArchitecturePattern.MVC:
            recommendations.append("Keep models thin and business logic in service layer.")
            recommendations.append("Consider using view models for data transfer between layers.")
        
        elif dominant_pattern.pattern == ArchitecturePattern.LAYERED:
            recommendations.append("Maintain strict dependency direction between layers.")
            recommendations.append("Consider using dependency injection for better testability.")
        
        # General recommendations based on organization quality
        if organization_analysis['naming_consistency'] < 0.7:
            recommendations.append("Establish and enforce consistent naming conventions.")
        
        if organization_analysis['separation_of_concerns'] < 0.7:
            recommendations.append("Improve separation of concerns by better organizing code modules.")
        
        if organization_analysis['documentation_level'] < 0.5:
            recommendations.append("Add more documentation to improve code maintainability.")
        
        return recommendations
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat()