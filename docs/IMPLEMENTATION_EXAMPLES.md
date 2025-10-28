# Implementation Examples

Code examples and integration guides for Excel AI Assistant enhancements.

---

## Table of Contents

1. [Summary Generator Implementation](#summary-generator-implementation)
2. [Notion Integration Examples](#notion-integration-examples)
3. [Microsoft Teams Integration Examples](#microsoft-teams-integration-examples)
4. [Export Manager Implementation](#export-manager-implementation)
5. [Meta Prompt Engine Implementation](#meta-prompt-engine-implementation)
6. [UI Components](#ui-components)

---

## Summary Generator Implementation

### Core Summary Generator Class

```python
# app/services/summary_generator.py

import logging
from typing import Dict, Any, List, Optional
import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class SummaryReport:
    """Data structure for summary reports"""
    title: str
    generated_at: datetime
    dataset_info: Dict[str, Any]
    data_quality: Dict[str, Any]
    statistical_summary: Dict[str, Any]
    insights: List[str]
    anomalies: List[Dict[str, Any]]
    visualizations: List[Dict[str, Any]]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary"""
        return {
            'title': self.title,
            'generated_at': self.generated_at.isoformat(),
            'dataset_info': self.dataset_info,
            'data_quality': self.data_quality,
            'statistical_summary': self.statistical_summary,
            'insights': self.insights,
            'anomalies': self.anomalies,
            'visualizations': self.visualizations,
            'recommendations': self.recommendations,
            'metadata': self.metadata
        }

    def to_json(self, filepath: str):
        """Save report as JSON"""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class SummaryGenerator:
    """Generate AI-powered summaries and analyses of Excel data"""

    SUMMARY_LEVELS = {
        'quick': {
            'name': 'Quick Summary',
            'description': 'High-level overview with key metrics',
            'time_estimate': '30 seconds',
            'includes': ['basic_stats', 'row_count', 'key_metrics']
        },
        'standard': {
            'name': 'Standard Analysis',
            'description': 'Detailed statistical analysis with visualizations',
            'time_estimate': '2-3 minutes',
            'includes': ['data_quality', 'statistics', 'visualizations', 'basic_insights']
        },
        'deep': {
            'name': 'Deep Dive',
            'description': 'Comprehensive analysis with correlations and predictions',
            'time_estimate': '5-10 minutes',
            'includes': ['data_quality', 'statistics', 'visualizations', 'correlations',
                        'anomalies', 'trends', 'predictions', 'insights']
        },
        'executive': {
            'name': 'Executive Summary',
            'description': 'Business-focused insights for decision makers',
            'time_estimate': '1-2 minutes',
            'includes': ['key_metrics', 'business_insights', 'recommendations']
        }
    }

    def __init__(self, data_manager, api_manager, viz_manager, config):
        """
        Initialize the summary generator

        Args:
            data_manager: DataManager instance
            api_manager: APIManager instance
            viz_manager: VisualizationManager instance
            config: AppConfig instance
        """
        self.data_manager = data_manager
        self.api_manager = api_manager
        self.viz_manager = viz_manager
        self.config = config
        self.logger = logging.getLogger("SummaryGenerator")

    def generate_summary(
        self,
        level: str = 'standard',
        options: Optional[Dict[str, Any]] = None
    ) -> SummaryReport:
        """
        Generate AI-powered summary of the dataset

        Args:
            level: Summary level ('quick', 'standard', 'deep', 'executive')
            options: Additional options for customization

        Returns:
            SummaryReport object
        """
        if level not in self.SUMMARY_LEVELS:
            raise ValueError(f"Invalid summary level: {level}")

        options = options or {}
        df = self.data_manager.get_data()

        if df is None or df.empty:
            raise ValueError("No data available to summarize")

        self.logger.info(f"Generating {level} summary for dataset with {len(df)} rows")

        # Initialize report
        report = SummaryReport(
            title=f"{self.SUMMARY_LEVELS[level]['name']} - {self.data_manager.file_path or 'Untitled'}",
            generated_at=datetime.now(),
            dataset_info=self._get_dataset_info(df),
            data_quality={},
            statistical_summary={},
            insights=[],
            anomalies=[],
            visualizations=[],
            recommendations=[],
            metadata={'level': level, 'options': options}
        )

        # Generate components based on level
        includes = self.SUMMARY_LEVELS[level]['includes']

        if 'data_quality' in includes:
            report.data_quality = self._analyze_data_quality(df)

        if 'statistics' in includes or 'basic_stats' in includes:
            report.statistical_summary = self._generate_statistics(df)

        if 'visualizations' in includes:
            report.visualizations = self._generate_visualizations(df, options)

        if 'anomalies' in includes:
            report.anomalies = self._detect_anomalies(df)

        if 'basic_insights' in includes or 'business_insights' in includes or 'insights' in includes:
            report.insights = self._extract_insights(df, report, level)

        if 'recommendations' in includes:
            report.recommendations = self._generate_recommendations(report)

        self.logger.info(f"Summary generation complete")
        return report

    def _get_dataset_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get basic dataset information"""
        return {
            'file_path': self.data_manager.file_path,
            'file_name': self.data_manager.get_meta_info().get('file_name'),
            'rows': len(df),
            'columns': len(df.columns),
            'column_names': list(df.columns),
            'column_types': self.data_manager.get_column_data_types(),
            'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024 / 1024:.2f} MB"
        }

    def _analyze_data_quality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze data quality metrics"""
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isna().sum().sum()

        quality_report = {
            'overall_score': 0,
            'total_cells': total_cells,
            'missing_cells': int(missing_cells),
            'missing_percentage': round((missing_cells / total_cells) * 100, 2),
            'columns_with_missing': {},
            'duplicate_rows': int(df.duplicated().sum()),
            'data_types_consistent': True,
            'issues': []
        }

        # Analyze each column
        for col in df.columns:
            missing = df[col].isna().sum()
            if missing > 0:
                quality_report['columns_with_missing'][col] = {
                    'count': int(missing),
                    'percentage': round((missing / len(df)) * 100, 2)
                }

        # Calculate overall quality score (0-100)
        score = 100
        score -= min(quality_report['missing_percentage'] * 2, 30)  # Max 30 points for missing data
        score -= min((quality_report['duplicate_rows'] / len(df)) * 100, 20)  # Max 20 points for duplicates

        quality_report['overall_score'] = max(0, round(score, 1))

        # Classify quality level
        if quality_report['overall_score'] >= 90:
            quality_report['quality_level'] = 'Excellent'
        elif quality_report['overall_score'] >= 75:
            quality_report['quality_level'] = 'Good'
        elif quality_report['overall_score'] >= 60:
            quality_report['quality_level'] = 'Fair'
        else:
            quality_report['quality_level'] = 'Poor'

        return quality_report

    def _generate_statistics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate statistical summary"""
        stats = {
            'numeric_columns': {},
            'categorical_columns': {},
            'datetime_columns': {}
        }

        # Numeric columns
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        for col in numeric_cols:
            stats['numeric_columns'][col] = {
                'count': int(df[col].count()),
                'mean': float(df[col].mean()) if df[col].count() > 0 else None,
                'median': float(df[col].median()) if df[col].count() > 0 else None,
                'std': float(df[col].std()) if df[col].count() > 0 else None,
                'min': float(df[col].min()) if df[col].count() > 0 else None,
                'max': float(df[col].max()) if df[col].count() > 0 else None,
                'quartiles': {
                    '25%': float(df[col].quantile(0.25)) if df[col].count() > 0 else None,
                    '50%': float(df[col].quantile(0.50)) if df[col].count() > 0 else None,
                    '75%': float(df[col].quantile(0.75)) if df[col].count() > 0 else None,
                }
            }

        # Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols:
            unique_count = df[col].nunique()
            stats['categorical_columns'][col] = {
                'unique_values': int(unique_count),
                'most_common': df[col].value_counts().head(5).to_dict() if unique_count > 0 else {},
                'least_common': df[col].value_counts().tail(5).to_dict() if unique_count > 5 else {}
            }

        return stats

    def _generate_visualizations(
        self,
        df: pd.DataFrame,
        options: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate appropriate visualizations"""
        visualizations = []
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        # Generate correlation heatmap if multiple numeric columns
        if len(numeric_cols) > 1:
            try:
                fig = self.viz_manager.create_chart(
                    data=df,
                    chart_type='heatmap',
                    title='Correlation Matrix'
                )
                visualizations.append({
                    'type': 'heatmap',
                    'title': 'Correlation Matrix',
                    'description': 'Shows relationships between numeric variables',
                    'figure': fig
                })
            except Exception as e:
                self.logger.error(f"Error creating heatmap: {e}")

        # Generate distribution plots for key numeric columns (top 3 by variance)
        if len(numeric_cols) > 0:
            try:
                # Select columns with highest variance
                variances = df[numeric_cols].var().sort_values(ascending=False)
                top_cols = variances.head(3).index.tolist()

                for col in top_cols:
                    fig = self.viz_manager.create_chart(
                        data=df,
                        chart_type='histogram',
                        x_column=col,
                        title=f'Distribution of {col}'
                    )
                    visualizations.append({
                        'type': 'histogram',
                        'title': f'Distribution of {col}',
                        'description': f'Shows the distribution of values in {col}',
                        'figure': fig
                    })
            except Exception as e:
                self.logger.error(f"Error creating histograms: {e}")

        return visualizations

    def _detect_anomalies(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect anomalies and outliers in the data"""
        anomalies = []
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns

        for col in numeric_cols:
            # Use IQR method to detect outliers
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if len(outliers) > 0:
                anomalies.append({
                    'column': col,
                    'type': 'outliers',
                    'count': len(outliers),
                    'percentage': round((len(outliers) / len(df)) * 100, 2),
                    'lower_bound': float(lower_bound),
                    'upper_bound': float(upper_bound),
                    'severity': 'high' if len(outliers) / len(df) > 0.05 else 'medium'
                })

        return anomalies

    def _extract_insights(
        self,
        df: pd.DataFrame,
        report: SummaryReport,
        level: str
    ) -> List[str]:
        """Use AI to extract meaningful insights"""
        insights = []

        # Prepare context for AI
        context = self._prepare_insights_context(df, report)

        # Create prompt based on level
        if level == 'executive':
            prompt = """Based on this dataset analysis, provide 5 key business insights that would be valuable for executives.
Focus on:
1. Major trends or patterns
2. Areas of concern or opportunity
3. Actionable recommendations
4. Business impact
5. Strategic implications

Keep each insight to 1-2 sentences. Be specific and data-driven."""
        else:
            prompt = """Analyze this dataset and provide 7-10 key insights.
Include:
- Statistical observations
- Patterns and trends
- Data quality concerns
- Interesting findings
- Potential correlations
- Anomalies or outliers

Each insight should be specific and actionable."""

        # Combine context and prompt
        full_prompt = f"Dataset Context:\n{context}\n\n{prompt}"

        try:
            success, result, error = self.api_manager.process_single_cell(
                cell_content="",
                system_prompt="You are a data analyst expert. Provide clear, concise, data-driven insights.",
                user_prompt=full_prompt,
                temperature=0.4,
                max_tokens=800
            )

            if success and result:
                # Parse insights (assuming they're returned as numbered list or bullet points)
                insights_raw = result.split('\n')
                insights = [insight.strip('- •1234567890.)\t ') for insight in insights_raw if insight.strip()]
                insights = [i for i in insights if len(i) > 10]  # Filter out empty or very short lines

        except Exception as e:
            self.logger.error(f"Error extracting insights: {e}")
            insights = ["Error generating AI insights. Manual analysis recommended."]

        return insights

    def _prepare_insights_context(self, df: pd.DataFrame, report: SummaryReport) -> str:
        """Prepare context string for AI insight generation"""
        context_parts = []

        # Dataset overview
        context_parts.append(f"Dataset: {report.dataset_info['rows']} rows, {report.dataset_info['columns']} columns")

        # Data quality
        if report.data_quality:
            dq = report.data_quality
            context_parts.append(
                f"Data Quality: {dq.get('quality_level', 'Unknown')} "
                f"({dq.get('missing_percentage', 0)}% missing data, "
                f"{dq.get('duplicate_rows', 0)} duplicates)"
            )

        # Key statistics for numeric columns
        if report.statistical_summary.get('numeric_columns'):
            context_parts.append("\nNumeric Columns Summary:")
            for col, stats in list(report.statistical_summary['numeric_columns'].items())[:5]:
                context_parts.append(
                    f"  - {col}: mean={stats.get('mean'):.2f}, "
                    f"std={stats.get('std', 0):.2f}, "
                    f"range=[{stats.get('min'):.2f}, {stats.get('max'):.2f}]"
                )

        # Anomalies
        if report.anomalies:
            context_parts.append(f"\nAnomalies Detected: {len(report.anomalies)} columns with outliers")
            for anomaly in report.anomalies[:3]:
                context_parts.append(
                    f"  - {anomaly['column']}: {anomaly['count']} outliers ({anomaly['percentage']}%)"
                )

        return '\n'.join(context_parts)

    def _generate_recommendations(self, report: SummaryReport) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []

        # Data quality recommendations
        if report.data_quality:
            dq = report.data_quality
            if dq.get('missing_percentage', 0) > 5:
                recommendations.append(
                    f"Address missing data: {dq['missing_percentage']}% of cells are empty. "
                    "Consider imputation or removal strategies."
                )

            if dq.get('duplicate_rows', 0) > 0:
                recommendations.append(
                    f"Remove {dq['duplicate_rows']} duplicate rows to improve data quality."
                )

        # Anomaly recommendations
        if report.anomalies:
            high_severity = [a for a in report.anomalies if a.get('severity') == 'high']
            if high_severity:
                recommendations.append(
                    f"Investigate {len(high_severity)} columns with significant outliers. "
                    "These may represent errors or important exceptions."
                )

        # Add AI-generated recommendations
        try:
            context = f"""
Based on this dataset analysis:
- Data Quality Score: {report.data_quality.get('overall_score', 'N/A')}
- Total Rows: {report.dataset_info['rows']}
- Insights: {'; '.join(report.insights[:3])}

Provide 3-5 specific, actionable recommendations for:
1. Improving data quality
2. Further analysis to conduct
3. Potential use cases for this data
4. Data governance improvements
"""

            success, result, error = self.api_manager.process_single_cell(
                cell_content="",
                system_prompt="You are a data strategy consultant. Provide practical, specific recommendations.",
                user_prompt=context,
                temperature=0.4,
                max_tokens=500
            )

            if success and result:
                ai_recommendations = [r.strip('- •1234567890.)\t ') for r in result.split('\n') if r.strip()]
                recommendations.extend([r for r in ai_recommendations if len(r) > 10])

        except Exception as e:
            self.logger.error(f"Error generating AI recommendations: {e}")

        return recommendations


# Example usage
def example_usage():
    """Example of how to use the SummaryGenerator"""
    from app.services.data_manager import DataManager
    from app.services.api_manager import APIManager
    from app.services.visualization_manager import VisualizationManager
    from app.config import AppConfig

    # Initialize dependencies
    config = AppConfig()
    data_manager = DataManager()
    api_manager = APIManager(api_key=config.get('api_key'), model=config.get('model'))
    viz_manager = VisualizationManager()

    # Load data
    success, error = data_manager.load_file('path/to/data.xlsx')
    if not success:
        print(f"Error loading file: {error}")
        return

    # Generate summary
    generator = SummaryGenerator(data_manager, api_manager, viz_manager, config)

    # Quick summary
    quick_report = generator.generate_summary(level='quick')

    # Standard analysis
    standard_report = generator.generate_summary(level='standard')

    # Deep dive with options
    deep_report = generator.generate_summary(
        level='deep',
        options={
            'include_predictions': True,
            'max_visualizations': 10
        }
    )

    # Export report
    deep_report.to_json('analysis_report.json')

    # Print insights
    print("Key Insights:")
    for idx, insight in enumerate(deep_report.insights, 1):
        print(f"{idx}. {insight}")
```

---

## Notion Integration Examples

### Notion Integration Class

```python
# app/integrations/notion_integration.py

from notion_client import Client
from notion_client.errors import APIResponseError
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class NotionIntegration:
    """Integration with Notion API for exporting reports and data"""

    def __init__(self, api_key: str):
        """
        Initialize Notion integration

        Args:
            api_key: Notion API integration token
        """
        self.client = Client(auth=api_key)
        self.logger = logging.getLogger("NotionIntegration")

    def test_connection(self) -> tuple[bool, str]:
        """
        Test the Notion API connection

        Returns:
            Tuple of (success, message)
        """
        try:
            # Try to list users as a connection test
            self.client.users.list()
            return True, "Connection successful"
        except APIResponseError as e:
            return False, f"API Error: {str(e)}"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def list_databases(self) -> List[Dict[str, Any]]:
        """
        List accessible databases

        Returns:
            List of database objects
        """
        try:
            response = self.client.search(filter={"property": "object", "value": "database"})
            return response.get('results', [])
        except Exception as e:
            self.logger.error(f"Error listing databases: {e}")
            return []

    def create_summary_page(
        self,
        title: str,
        content: Dict[str, Any],
        parent_page_id: Optional[str] = None,
        database_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Create a new Notion page with summary content

        Args:
            title: Page title
            content: Report content dictionary
            parent_page_id: Optional parent page ID
            database_id: Optional database ID to add page to

        Returns:
            Created page ID or None if failed
        """
        try:
            # Determine parent
            if database_id:
                parent = {"database_id": database_id}
            elif parent_page_id:
                parent = {"page_id": parent_page_id}
            else:
                # No parent specified - error
                self.logger.error("Either parent_page_id or database_id must be specified")
                return None

            # Build page properties
            properties = {
                "title": {
                    "title": [{"text": {"content": title}}]
                }
            }

            # Build content blocks
            children = self._build_content_blocks(content)

            # Create page
            response = self.client.pages.create(
                parent=parent,
                properties=properties,
                children=children
            )

            page_id = response['id']
            self.logger.info(f"Created Notion page: {page_id}")
            return page_id

        except APIResponseError as e:
            self.logger.error(f"Notion API error creating page: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error creating page: {e}")
            return None

    def _build_content_blocks(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build Notion blocks from content dictionary

        Args:
            content: Summary report content

        Returns:
            List of Notion block objects
        """
        blocks = []

        # Add generated timestamp
        if 'generated_at' in content:
            blocks.append({
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [{
                        "type": "text",
                        "text": {
                            "content": f"Generated: {content['generated_at']}"
                        }
                    }],
                    "icon": {"emoji": "📊"}
                }
            })

        # Add dataset info
        if 'dataset_info' in content:
            info = content['dataset_info']
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Dataset Information"}}]
                }
            })

            info_text = f"• Rows: {info.get('rows', 'N/A')}\n"
            info_text += f"• Columns: {info.get('columns', 'N/A')}\n"
            info_text += f"• File: {info.get('file_name', 'N/A')}"

            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": info_text}}]
                }
            })

        # Add data quality section
        if 'data_quality' in content:
            dq = content['data_quality']
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Data Quality"}}]
                }
            })

            quality_text = f"Overall Score: {dq.get('overall_score', 'N/A')}/100 "
            quality_text += f"({dq.get('quality_level', 'Unknown')})\n"
            quality_text += f"Missing Data: {dq.get('missing_percentage', 0)}%\n"
            quality_text += f"Duplicate Rows: {dq.get('duplicate_rows', 0)}"

            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"text": {"content": quality_text}}]
                }
            })

        # Add insights
        if 'insights' in content and content['insights']:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Key Insights"}}]
                }
            })

            for insight in content['insights']:
                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"text": {"content": insight}}]
                    }
                })

        # Add recommendations
        if 'recommendations' in content and content['recommendations']:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "Recommendations"}}]
                }
            })

            for rec in content['recommendations']:
                blocks.append({
                    "object": "block",
                    "type": "numbered_list_item",
                    "numbered_list_item": {
                        "rich_text": [{"text": {"content": rec}}]
                    }
                })

        # Add anomalies if present
        if 'anomalies' in content and content['anomalies']:
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"text": {"content": "⚠️ Anomalies Detected"}}]
                }
            })

            for anomaly in content['anomalies']:
                anomaly_text = f"{anomaly.get('column', 'Unknown')}: "
                anomaly_text += f"{anomaly.get('count', 0)} outliers "
                anomaly_text += f"({anomaly.get('percentage', 0)}%)"

                blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"text": {"content": anomaly_text}}]
                    }
                })

        return blocks

    def upload_image(self, image_path: str) -> Optional[str]:
        """
        Upload image and get URL (Note: Notion doesn't support direct uploads,
        images must be hosted externally)

        Args:
            image_path: Path to image file

        Returns:
            Image URL or None
        """
        # Notion requires externally hosted images
        # This would need integration with a file hosting service
        # For now, return None and log a message
        self.logger.warning(
            "Notion requires externally hosted images. "
            "Please upload images to a hosting service first."
        )
        return None


# Example usage
def example_notion_usage():
    """Example of using Notion integration"""
    from app.services.summary_generator import SummaryReport
    import json

    # Initialize integration
    notion = NotionIntegration(api_key="your_notion_api_key")

    # Test connection
    success, message = notion.test_connection()
    print(f"Connection test: {message}")

    if not success:
        return

    # List databases
    databases = notion.list_databases()
    print(f"Found {len(databases)} databases")

    # Load a summary report
    with open('analysis_report.json', 'r') as f:
        report_data = json.load(f)

    # Create page in database
    page_id = notion.create_summary_page(
        title="Q4 Sales Analysis",
        content=report_data,
        database_id="your_database_id"
    )

    if page_id:
        print(f"Created Notion page: {page_id}")
        print(f"View at: https://notion.so/{page_id.replace('-', '')}")
```

---

## Microsoft Teams Integration Examples

```python
# app/integrations/teams_integration.py

import pymsteams
import requests
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class TeamsIntegration:
    """Integration with Microsoft Teams for posting reports"""

    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize Teams integration

        Args:
            webhook_url: Incoming webhook URL for Teams channel
        """
        self.webhook_url = webhook_url
        self.logger = logging.getLogger("TeamsIntegration")

    def set_webhook_url(self, url: str):
        """Set or update webhook URL"""
        self.webhook_url = url

    def test_connection(self) -> tuple[bool, str]:
        """
        Test Teams webhook connection

        Returns:
            Tuple of (success, message)
        """
        if not self.webhook_url:
            return False, "No webhook URL configured"

        try:
            # Send test message
            card = pymsteams.connectorcard(self.webhook_url)
            card.title("Connection Test")
            card.text("Excel AI Assistant connection successful!")
            card.color("00FF00")  # Green
            card.send()
            return True, "Connection successful"
        except Exception as e:
            return False, f"Connection failed: {str(e)}"

    def send_summary_card(
        self,
        summary_report: Dict[str, Any],
        mentions: Optional[List[str]] = None
    ) -> tuple[bool, str]:
        """
        Send summary report as adaptive card to Teams

        Args:
            summary_report: Summary report dictionary
            mentions: Optional list of user emails to mention

        Returns:
            Tuple of (success, message)
        """
        if not self.webhook_url:
            return False, "No webhook URL configured"

        try:
            card = pymsteams.connectorcard(self.webhook_url)

            # Set card title and theme
            title = summary_report.get('title', 'Data Analysis Report')
            card.title(f"📊 {title}")
            card.color("0078D4")  # Microsoft Blue

            # Add summary section
            dataset_info = summary_report.get('dataset_info', {})
            summary_text = f"**Dataset:** {dataset_info.get('file_name', 'Unknown')}\n\n"
            summary_text += f"**Rows:** {dataset_info.get('rows', 'N/A')} | "
            summary_text += f"**Columns:** {dataset_info.get('columns', 'N/A')}\n\n"

            # Add data quality if available
            if 'data_quality' in summary_report:
                dq = summary_report['data_quality']
                quality_emoji = self._get_quality_emoji(dq.get('overall_score', 0))
                summary_text += f"**Data Quality:** {quality_emoji} "
                summary_text += f"{dq.get('quality_level', 'Unknown')} "
                summary_text += f"({dq.get('overall_score', 0)}/100)\n\n"

            card.text(summary_text)

            # Add insights section
            insights = summary_report.get('insights', [])
            if insights:
                insights_section = card.addsection()
                insights_section.title("🔍 Key Insights")

                insights_text = ""
                for idx, insight in enumerate(insights[:5], 1):  # Limit to 5 for card
                    insights_text += f"{idx}. {insight}\n\n"

                insights_section.text(insights_text)

            # Add recommendations
            recommendations = summary_report.get('recommendations', [])
            if recommendations:
                rec_section = card.addsection()
                rec_section.title("💡 Recommendations")

                rec_text = ""
                for idx, rec in enumerate(recommendations[:5], 1):
                    rec_text += f"{idx}. {rec}\n\n"

                rec_section.text(rec_text)

            # Add anomalies alert if any
            anomalies = summary_report.get('anomalies', [])
            if anomalies:
                anomaly_section = card.addsection()
                anomaly_section.title("⚠️ Anomalies Detected")
                anomaly_section.activityTitle(f"Found {len(anomalies)} columns with outliers")

            # Add action buttons
            card.addLinkButton("View Full Report", "https://your-app-url/reports/latest")

            # Send card
            card.send()

            return True, "Summary sent successfully"

        except Exception as e:
            self.logger.error(f"Error sending Teams card: {e}")
            return False, f"Failed to send: {str(e)}"

    def _get_quality_emoji(self, score: float) -> str:
        """Get emoji based on quality score"""
        if score >= 90:
            return "🟢"
        elif score >= 75:
            return "🟡"
        elif score >= 60:
            return "🟠"
        else:
            return "🔴"

    def send_simple_message(
        self,
        title: str,
        message: str,
        color: str = "0078D4"
    ) -> tuple[bool, str]:
        """
        Send a simple message card

        Args:
            title: Message title
            message: Message text
            color: Hex color code

        Returns:
            Tuple of (success, message)
        """
        if not self.webhook_url:
            return False, "No webhook URL configured"

        try:
            card = pymsteams.connectorcard(self.webhook_url)
            card.title(title)
            card.text(message)
            card.color(color)
            card.send()
            return True, "Message sent successfully"
        except Exception as e:
            return False, f"Failed to send: {str(e)}"


# Example usage
def example_teams_usage():
    """Example of using Teams integration"""
    import json

    # Initialize integration
    teams = TeamsIntegration(webhook_url="your_webhook_url")

    # Test connection
    success, message = teams.test_connection()
    print(f"Connection test: {message}")

    # Load report
    with open('analysis_report.json', 'r') as f:
        report_data = json.load(f)

    # Send summary
    success, message = teams.send_summary_card(report_data)
    print(f"Send result: {message}")

    # Send simple notification
    teams.send_simple_message(
        title="Data Processing Complete",
        message="Your Excel file has been processed successfully!",
        color="00FF00"
    )
```

---

## Configuration Integration

Add to `app/config.py`:

```python
# Integration settings
'integrations': {
    'notion': {
        'enabled': False,
        'api_key': '',
        'default_database_id': '',
        'default_parent_page_id': '',
    },
    'teams': {
        'enabled': False,
        'webhook_url': '',
        'default_channel': '',
    },
},

# Summary generator settings
'summary_generator': {
    'default_level': 'standard',
    'include_visualizations': True,
    'max_insights': 10,
    'enable_ai_insights': True,
    'cache_duration_hours': 24,
},
```

---

This implementation guide provides the foundational code for the major new features. Each module is designed to be modular and can be integrated incrementally into the existing Excel AI Assistant codebase.
