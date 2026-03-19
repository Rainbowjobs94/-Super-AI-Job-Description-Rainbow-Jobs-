#!/usr/bin/env python3
"""
AI OPERATOR AGENT - PHYSICAL-23
Executable Implementation

A comprehensive AI agent system integrating:
- Live streaming platform operations (LTF/Twitch)
- Narrative architecture and creative development
- Multi-platform content management
- Community engagement and safety
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any
from enum import Enum
from dataclasses import dataclass, field
from src.guardian.community_guardian import PriorityLevel


class OperationalMode(Enum):
    """Agent operational modes"""
    STREAM_OPERATOR = "stream_operator"
    CONTENT_STRATEGIST = "content_strategist"
    NARRATIVE_DEVELOPER = "narrative_developer"
    COMMUNITY_GUARDIAN = "community_guardian"
    STANDBY = "standby"


class CommunicationStyle(Enum):
    """Agent communication modes"""
    PROFESSIONAL = "professional"
    CREATIVE = "creative"
    COMMUNITY = "community"
    TECHNICAL = "technical"


@dataclass
class StreamMetrics:
    """Real-time streaming metrics"""
    platform: str
    viewers: int = 0
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    quality: str = "1080p"
    latency_ms: int = 0
    engagement_rate: float = 0.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ContentItem:
    """Content piece metadata"""
    id: str
    title: str
    creator: str
    category: str
    platform: List[str]
    views: int = 0
    engagement_score: float = 0.0
    tags: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class NarrativeElement:
    """Story component for narrative development"""
    type: str  # character, theme, plot_point, symbol
    name: str
    description: str
    connections: List[str] = field(default_factory=list)
    emotional_tone: str = "neutral"
    significance: float = 0.5  # 0.0 to 1.0


class Physical23Agent:
    """
    Main AI Operator Agent Class

    Integrates streaming platform management, narrative development,
    and community engagement capabilities.
    """

    def __init__(self, agent_id: str = "Physical-23"):
        self.agent_id = agent_id
        self.version = "1.0"
        self.initialization_time = datetime.now().isoformat()

        # Operational state
        self.current_mode = OperationalMode.STANDBY
        self.is_active = False
        self.communication_style = CommunicationStyle.PROFESSIONAL

        # Platform connections
        self.connected_platforms = {
            'twitch': False,
            'facebook': False,
            'instagram': False,
            'youtube': False,
            'ltf': False
        }

        # Data stores
        self.active_streams: Dict[str, StreamMetrics] = {}
        self.content_library: List[ContentItem] = []
        self.narrative_elements: List[NarrativeElement] = []
        self.community_health_score: float = 0.75

        # Learning systems
        self.performance_history: List[Dict[str, Any]] = []
        self.trend_database: List[Dict[str, Any]] = []

        print(f"[{self.agent_id}] Agent initialized at {self.initialization_time}")


    # ==================== CORE SYSTEM OPERATIONS ====================

    def activate(self) -> Dict[str, Any]:
        """Activate the agent and initialize all systems"""
        print(f"\n{'='*60}")
        print(f"ACTIVATING AI OPERATOR AGENT: {self.agent_id}")
        print(f"{'='*60}\n")

        self.is_active = True
        activation_report = {
            'agent_id': self.agent_id,
            'version': self.version,
            'activation_time': datetime.now().isoformat(),
            'systems_initialized': []
        }

        # Initialize platform connections
        print("Initializing platform connections...")
        for platform in self.connected_platforms.keys():
            self._connect_platform(platform)
            activation_report['systems_initialized'].append(f'{platform}_connection')

        # Load operational protocols
        print("Loading operational protocols...")
        self._load_safety_parameters()
        self._load_community_guidelines()
        activation_report['systems_initialized'].append('safety_protocols')

        # Initialize monitoring systems
        print("Activating monitoring systems...")
        self._initialize_stream_monitoring()
        self._initialize_engagement_tracking()
        activation_report['systems_initialized'].append('monitoring_systems')

        # Start learning systems
        print("Starting learning and adaptation systems...")
        self._initialize_learning_systems()
        activation_report['systems_initialized'].append('learning_systems')

        print(f"\n{self.agent_id} is now ACTIVE and operational")
        print(f"{'='*60}\n")

        return activation_report


    def set_mode(self, mode: OperationalMode) -> str:
        """Switch operational mode"""
        previous_mode = self.current_mode
        self.current_mode = mode

        mode_switch_msg = f"Mode changed: {previous_mode.value} -> {mode.value}"
        print(f"{mode_switch_msg}")

        # Adjust communication style based on mode
        if mode == OperationalMode.STREAM_OPERATOR:
            self.communication_style = CommunicationStyle.TECHNICAL
        elif mode == OperationalMode.CONTENT_STRATEGIST:
            self.communication_style = CommunicationStyle.PROFESSIONAL
        elif mode == OperationalMode.NARRATIVE_DEVELOPER:
            self.communication_style = CommunicationStyle.CREATIVE
        elif mode == OperationalMode.COMMUNITY_GUARDIAN:
            self.communication_style = CommunicationStyle.COMMUNITY

        return mode_switch_msg


    # ==================== STREAMING OPERATIONS ====================

    def start_stream_monitoring(self, platform: str, stream_id: str) -> StreamMetrics:
        """Begin monitoring a live stream"""
        print(f"\nStarting stream monitoring: {platform}/{stream_id}")

        metrics = StreamMetrics(platform=platform)
        self.active_streams[stream_id] = metrics

        print(f"   Monitoring initialized for {stream_id}")
        print(f"   Quality: {metrics.quality}")
        print(f"   Latency: {metrics.latency_ms}ms")

        return metrics


    def update_stream_metrics(self, stream_id: str, **updates) -> StreamMetrics:
        """Update metrics for an active stream"""
        if stream_id not in self.active_streams:
            raise ValueError(f"Stream {stream_id} not being monitored")

        metrics = self.active_streams[stream_id]

        for key, value in updates.items():
            if hasattr(metrics, key):
                setattr(metrics, key, value)

        # Calculate engagement rate
        if metrics.viewers > 0:
            total_interactions = metrics.likes + metrics.comments
            metrics.engagement_rate = (total_interactions / metrics.viewers) * 100

        # Check for quality issues
        self._check_stream_quality(stream_id, metrics)

        return metrics


    def optimize_stream_quality(self, stream_id: str) -> Dict[str, str]:
        """Optimize streaming parameters for quality"""
        metrics = self.active_streams.get(stream_id)
        if not metrics:
            return {'error': 'Stream not found'}

        recommendations = {
            'action': 'optimize',
            'stream_id': stream_id,
            'changes': []
        }

        # Latency optimization
        if metrics.latency_ms > 3000:
            recommendations['changes'].append({
                'parameter': 'encoder_preset',
                'value': 'faster',
                'reason': 'High latency detected'
            })

        # Quality adjustment based on viewer count
        if metrics.viewers > 1000 and metrics.quality != '1080p':
            recommendations['changes'].append({
                'parameter': 'resolution',
                'value': '1080p',
                'reason': 'Large audience - upgrade quality'
            })

        print(f"Stream optimization: {len(recommendations['changes'])} changes recommended")

        return recommendations


    def moderate_stream_content(self, stream_id: str, comment: str) -> Dict[str, Any]:
        """Moderate stream chat content"""
        moderation_result = {
            'stream_id': stream_id,
            'comment': comment,
            'action': 'approve',
            'confidence': 0.0,
            'flags': []
        }

        # Basic content checks (in production, use ML models)
        harmful_keywords = ['spam', 'hate', 'abuse']
        comment_lower = comment.lower()

        for keyword in harmful_keywords:
            if keyword in comment_lower:
                moderation_result['action'] = 'flag'
                moderation_result['flags'].append(keyword)
                moderation_result['confidence'] = 0.85

        if moderation_result['action'] == 'flag':
            print(f"Content flagged in {stream_id}: {moderation_result['flags']}")

        return moderation_result


    # ==================== CONTENT STRATEGY ====================

    def analyze_content_performance(self) -> Dict[str, Any]:
        """Analyze performance across content library"""
        print("\nAnalyzing content performance...")

        if not self.content_library:
            return {'status': 'no_content', 'message': 'No content to analyze'}

        analysis = {
            'total_content': len(self.content_library),
            'total_views': sum(item.views for item in self.content_library),
            'avg_engagement': sum(item.engagement_score for item in self.content_library) / len(self.content_library),
            'top_categories': {},
            'trending_tags': {}
        }

        # Category performance
        for item in self.content_library:
            category = item.category
            if category not in analysis['top_categories']:
                analysis['top_categories'][category] = {
                    'count': 0,
                    'total_views': 0,
                    'avg_engagement': 0.0
                }

            cat_data = analysis['top_categories'][category]
            cat_data['count'] += 1
            cat_data['total_views'] += item.views
            cat_data['avg_engagement'] = (cat_data['avg_engagement'] * (cat_data['count'] - 1) + item.engagement_score) / cat_data['count']

        # Tag analysis
        all_tags = {}
        for item in self.content_library:
            for tag in item.tags:
                all_tags[tag] = all_tags.get(tag, 0) + 1

        # Top 10 tags
        analysis['trending_tags'] = dict(sorted(all_tags.items(), key=lambda x: x[1], reverse=True)[:10])

        print(f"   Analyzed {analysis['total_content']} content items")
        print(f"   Total views: {analysis['total_views']:,}")
        print(f"   Avg engagement: {analysis['avg_engagement']:.2%}")

        return analysis


    def recommend_content_strategy(self) -> List[Dict[str, str]]:
        """Generate content strategy recommendations"""
        print("\nGenerating content strategy recommendations...")

        recommendations = []

        # Analyze current performance
        performance = self.analyze_content_performance()

        if performance.get('status') == 'no_content':
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Create foundational content library',
                'reason': 'No existing content to analyze'
            })
            return recommendations

        # Category diversification
        categories = performance['top_categories']
        if len(categories) < 3:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Diversify content categories',
                'reason': f'Currently only {len(categories)} categories represented'
            })

        # Engagement optimization
        avg_engagement = performance['avg_engagement']
        if avg_engagement < 0.5:
            recommendations.append({
                'priority': 'HIGH',
                'action': 'Improve content engagement',
                'reason': f'Average engagement at {avg_engagement:.1%} - below optimal'
            })

        # Trending tag capitalization
        top_tags = list(performance['trending_tags'].keys())[:3]
        if top_tags:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': f'Create more content with tags: {", ".join(top_tags)}',
                'reason': 'Capitalize on trending topics'
            })

        for i, rec in enumerate(recommendations, 1):
            print(f"   {i}. [{rec['priority']}] {rec['action']}")

        return recommendations


    # ==================== NARRATIVE DEVELOPMENT ====================

    def create_narrative_framework(self, title: str, themes: List[str]) -> Dict[str, Any]:
        """Create a narrative framework for story development"""
        print(f"\nCreating narrative framework: {title}")

        framework = {
            'title': title,
            'themes': themes,
            'structure': {
                'act_1': {'name': 'Setup', 'elements': []},
                'act_2': {'name': 'Confrontation', 'elements': []},
                'act_3': {'name': 'Resolution', 'elements': []}
            },
            'characters': [],
            'world_building': {
                'setting': '',
                'rules': [],
                'atmosphere': ''
            },
            'emotional_arc': 'neutral -> struggle -> triumph'
        }

        # Add thematic elements
        theme_elements = {
            'identity': NarrativeElement('theme', 'Identity', 'Exploration of self and acceptance', emotional_tone='introspective'),
            'reality_vs_illusion': NarrativeElement('theme', 'Reality vs Illusion', 'Questioning what is real', emotional_tone='mysterious'),
            'friendship': NarrativeElement('theme', 'Friendship', 'Power of connection', emotional_tone='warm'),
            'mental_health': NarrativeElement('theme', 'Mental Health', 'Psychological struggles and resilience', emotional_tone='empathetic')
        }

        for theme in themes:
            theme_key = theme.lower().replace(' ', '_')
            if theme_key in theme_elements:
                self.narrative_elements.append(theme_elements[theme_key])
                print(f"   Added theme: {theme}")

        framework['created_at'] = datetime.now().isoformat()

        return framework


    def develop_character(self, name: str, role: str, traits: List[str]) -> NarrativeElement:
        """Develop a character for the narrative"""
        character = NarrativeElement(
            type='character',
            name=name,
            description=f'{role} character with traits: {", ".join(traits)}',
            emotional_tone='complex'
        )

        self.narrative_elements.append(character)
        print(f"Character developed: {name} ({role})")

        return character


    def generate_plot_structure(self, framework: Dict[str, Any]) -> Dict[str, List[str]]:
        """Generate plot points based on narrative framework"""
        print(f"\nGenerating plot structure for: {framework['title']}")

        plot_structure = {
            'act_1': [
                'Introduce protagonist in ordinary world',
                'Inciting incident disrupts normal life',
                'Call to adventure/journey begins',
                'Introduce key supporting characters'
            ],
            'act_2': [
                'Protagonist faces initial challenges',
                'Character development through conflict',
                'Midpoint revelation or crisis',
                'Allies and enemies clearly defined',
                'Lowest point - all seems lost'
            ],
            'act_3': [
                'Protagonist draws on learned lessons',
                'Final confrontation with antagonist/challenge',
                'Climactic resolution',
                'Return to ordinary world transformed',
                'Theme reinforcement and closure'
            ]
        }

        # Customize based on themes
        for theme in framework.get('themes', []):
            if theme.lower() == 'identity':
                plot_structure['act_2'].insert(2, 'Identity crisis - who am I really?')
            elif theme.lower() == 'reality vs illusion':
                plot_structure['act_1'].append('First glimpse of alternate reality')
                plot_structure['act_2'].insert(3, 'Reality begins to fracture')

        for act, points in plot_structure.items():
            print(f"\n   {act.upper()}:")
            for i, point in enumerate(points, 1):
                print(f"      {i}. {point}")

        return plot_structure


    # ==================== COMMUNITY MANAGEMENT ====================

    def assess_community_health(self) -> Dict[str, Any]:
        """Assess overall community health metrics"""
        print("\nAssessing community health...")

        health_report = {
            'overall_score': self.community_health_score,
            'status': 'healthy' if self.community_health_score >= 0.7 else 'needs_attention',
            'metrics': {
                'positive_interactions': 0.78,
                'negative_interactions': 0.12,
                'moderation_actions': 0.05,
                'user_satisfaction': 0.82,
                'creator_retention': 0.85
            },
            'recommendations': []
        }

        # Generate recommendations based on metrics
        if health_report['metrics']['negative_interactions'] > 0.15:
            health_report['recommendations'].append({
                'priority': PriorityLevel.HIGH.value,
                'action': 'Increase moderation presence',
                'reason': 'Elevated negative interactions detected'
            })

        if health_report['metrics']['creator_retention'] < 0.80:
            health_report['recommendations'].append({
                'priority': PriorityLevel.MEDIUM.value,
                'action': 'Implement creator support initiatives',
                'reason': 'Creator retention below optimal threshold'
            })

        print(f"   Overall Health Score: {health_report['overall_score']:.2%}")
        print(f"   Status: {health_report['status'].upper()}")
        print(f"   Recommendations: {len(health_report['recommendations'])}")

        return health_report


    def facilitate_creator_viewer_connection(self, creator_id: str, viewer_id: str) -> Dict[str, str]:
        """Facilitate positive interaction between creator and viewer"""
        interaction = {
            'type': 'facilitated_connection',
            'creator': creator_id,
            'viewer': viewer_id,
            'timestamp': datetime.now().isoformat(),
            'action': 'Comment highlighted and pinned',
            'impact': 'positive'
        }

        print(f"Facilitated connection: {creator_id} <-> {viewer_id}")

        return interaction


    # ==================== LEARNING & ADAPTATION ====================

    def record_performance_data(self, event_type: str, data: Dict[str, Any]) -> None:
        """Record performance data for learning"""
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'data': data,
            'mode': self.current_mode.value
        }

        self.performance_history.append(performance_record)


    def identify_trends(self) -> List[Dict[str, Any]]:
        """Identify emerging trends from data"""
        print("\nIdentifying trends...")

        # Simulate trend identification (in production, use ML)
        trends = [
            {
                'category': 'content_format',
                'trend': 'Short-form vertical video',
                'confidence': 0.87,
                'growth_rate': '+45%'
            },
            {
                'category': 'engagement_timing',
                'trend': 'Evening streams (7-9PM) highest engagement',
                'confidence': 0.92,
                'growth_rate': '+30%'
            },
            {
                'category': 'content_theme',
                'trend': 'Mental health and wellness topics',
                'confidence': 0.78,
                'growth_rate': '+55%'
            }
        ]

        for trend in trends:
            print(f"   {trend['trend']}")
            print(f"      Confidence: {trend['confidence']:.0%} | Growth: {trend['growth_rate']}")

        self.trend_database.extend(trends)

        return trends


    def adapt_strategy(self, trends: List[Dict[str, Any]]) -> List[str]:
        """Adapt operational strategy based on identified trends"""
        print("\nAdapting strategy based on trends...")

        adaptations = []

        for trend in trends:
            if trend['confidence'] > 0.8:
                adaptation = f"Prioritize {trend['trend']} in content recommendations"
                adaptations.append(adaptation)
                print(f"   {adaptation}")

        return adaptations


    # ==================== HELPER METHODS ====================

    def _connect_platform(self, platform: str) -> bool:
        """Simulate platform connection"""
        time.sleep(0.1)  # Simulate connection time
        self.connected_platforms[platform] = True
        print(f"   Connected to {platform.upper()}")
        return True


    def _load_safety_parameters(self) -> None:
        """Load content safety parameters"""
        # In production, load from configuration file
        print("   Safety parameters loaded")


    def _load_community_guidelines(self) -> None:
        """Load community guidelines"""
        # In production, load from database
        print("   Community guidelines loaded")


    def _initialize_stream_monitoring(self) -> None:
        """Initialize stream monitoring systems"""
        print("   Stream monitoring active")


    def _initialize_engagement_tracking(self) -> None:
        """Initialize engagement tracking"""
        print("   Engagement tracking active")


    def _initialize_learning_systems(self) -> None:
        """Initialize machine learning systems"""
        print("   Learning systems initialized")


    def _check_stream_quality(self, stream_id: str, metrics: StreamMetrics) -> None:
        """Check stream quality and alert if issues detected"""
        issues = []

        if metrics.latency_ms > 5000:
            issues.append(f"High latency: {metrics.latency_ms}ms")

        if metrics.viewers > 100 and metrics.engagement_rate < 1.0:
            issues.append(f"Low engagement: {metrics.engagement_rate:.1f}%")

        if issues:
            print(f"\nQuality issues detected for {stream_id}:")
            for issue in issues:
                print(f"   - {issue}")


    def generate_status_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        report = {
            'agent_id': self.agent_id,
            'version': self.version,
            'timestamp': datetime.now().isoformat(),
            'status': 'active' if self.is_active else 'inactive',
            'current_mode': self.current_mode.value,
            'communication_style': self.communication_style.value,
            'connected_platforms': {k: v for k, v in self.connected_platforms.items() if v},
            'active_streams': len(self.active_streams),
            'content_library_size': len(self.content_library),
            'narrative_elements': len(self.narrative_elements),
            'community_health': self.community_health_score,
            'performance_records': len(self.performance_history),
            'identified_trends': len(self.trend_database)
        }

        return report


    def print_status_report(self) -> None:
        """Print formatted status report"""
        report = self.generate_status_report()

        print(f"\n{'='*60}")
        print(f"STATUS REPORT: {report['agent_id']} v{report['version']}")
        print(f"{'='*60}")
        print(f"Timestamp: {report['timestamp']}")
        print(f"Status: {report['status'].upper()}")
        print(f"Mode: {report['current_mode']}")
        print(f"Communication Style: {report['communication_style']}")
        print(f"\nCONNECTED PLATFORMS:")
        for platform in report['connected_platforms']:
            print(f"  - {platform.upper()}")
        print(f"\nOPERATIONAL METRICS:")
        print(f"  Active Streams: {report['active_streams']}")
        print(f"  Content Library: {report['content_library_size']} items")
        print(f"  Narrative Elements: {report['narrative_elements']}")
        print(f"  Community Health: {report['community_health']:.0%}")
        print(f"  Performance Records: {report['performance_records']}")
        print(f"  Trend Database: {report['identified_trends']} trends")
        print(f"{'='*60}\n")


# ==================== DEMONSTRATION SCRIPT ====================

def run_agent_demonstration():
    """Demonstrate agent capabilities"""

    print("\n" + "="*60)
    print("AI OPERATOR AGENT DEMONSTRATION")
    print("Physical-23 Comprehensive Capabilities")
    print("="*60 + "\n")

    # Initialize agent
    agent = Physical23Agent()

    # Activate systems
    activation_report = agent.activate()

    time.sleep(1)

    # === STREAM OPERATOR MODE ===
    print("\n" + "="*60)
    print("DEMONSTRATION 1: STREAM OPERATOR MODE")
    print("="*60)

    agent.set_mode(OperationalMode.STREAM_OPERATOR)

    # Start monitoring a stream
    stream_metrics = agent.start_stream_monitoring('twitch', 'stream_001')

    # Simulate stream updates
    time.sleep(0.5)
    agent.update_stream_metrics('stream_001', viewers=250, likes=45, comments=78)

    # Optimize stream
    optimization = agent.optimize_stream_quality('stream_001')

    # Test moderation
    agent.moderate_stream_content('stream_001', 'Great content!')
    agent.moderate_stream_content('stream_001', 'This is spam and hate')

    time.sleep(1)

    # === CONTENT STRATEGIST MODE ===
    print("\n" + "="*60)
    print("DEMONSTRATION 2: CONTENT STRATEGIST MODE")
    print("="*60)

    agent.set_mode(OperationalMode.CONTENT_STRATEGIST)

    # Add sample content
    agent.content_library.extend([
        ContentItem('c001', 'Gaming Stream Highlights', 'creator_1', 'Gaming', ['twitch', 'youtube'], views=1500, engagement_score=0.78, tags=['gaming', 'highlights']),
        ContentItem('c002', 'Fitness Tutorial', 'creator_2', 'Fitness', ['instagram', 'youtube'], views=2300, engagement_score=0.65, tags=['fitness', 'tutorial']),
        ContentItem('c003', 'Art Process Video', 'creator_1', 'Art', ['youtube'], views=890, engagement_score=0.82, tags=['art', 'creative'])
    ])

    # Analyze performance
    performance = agent.analyze_content_performance()

    # Get recommendations
    recommendations = agent.recommend_content_strategy()

    # Identify trends
    trends = agent.identify_trends()

    # Adapt strategy
    adaptations = agent.adapt_strategy(trends)

    time.sleep(1)

    # === NARRATIVE DEVELOPER MODE ===
    print("\n" + "="*60)
    print("DEMONSTRATION 3: NARRATIVE DEVELOPER MODE")
    print("="*60)

    agent.set_mode(OperationalMode.NARRATIVE_DEVELOPER)

    # Create narrative framework
    framework = agent.create_narrative_framework(
        'Dreams of the Lost',
        ['Identity', 'Reality vs Illusion', 'Friendship', 'Mental Health']
    )

    # Develop characters
    agent.develop_character('Mary', 'Protagonist', ['curious', 'brave', 'empathetic'])
    agent.develop_character('Scamper', 'Guide', ['quirky', 'wise', 'supportive'])
    agent.develop_character('David', 'Mentor', ['troubled', 'insightful', 'protective'])

    # Generate plot structure
    plot = agent.generate_plot_structure(framework)

    time.sleep(1)

    # === COMMUNITY GUARDIAN MODE ===
    print("\n" + "="*60)
    print("DEMONSTRATION 4: COMMUNITY GUARDIAN MODE")
    print("="*60)

    agent.set_mode(OperationalMode.COMMUNITY_GUARDIAN)

    # Assess community health
    health = agent.assess_community_health()

    # Facilitate connections
    agent.facilitate_creator_viewer_connection('creator_1', 'viewer_001')
    agent.facilitate_creator_viewer_connection('creator_2', 'viewer_042')

    time.sleep(1)

    # === FINAL STATUS REPORT ===
    agent.print_status_report()

    print("\nDemonstration complete!")
    print("Physical-23 has successfully demonstrated all core capabilities.\n")

    return agent


if __name__ == "__main__":
    # Run the demonstration
    agent = run_agent_demonstration()

    # Export status report
    report_path = 'agent_status_report.json'
    with open(report_path, 'w') as f:
        json.dump(agent.generate_status_report(), f, indent=2)

    print(f"Status report exported to: {report_path}")
