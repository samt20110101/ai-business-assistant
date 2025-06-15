import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import re

# Configure page
st.set_page_config(
    page_title="Truly Dynamic AI Charts",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .chart-container {
        background: linear-gradient(145deg, #1e3c72, #2a5298);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        color: white;
    }
    
    .ai-response {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #007bff;
        margin: 1rem 0;
    }
    
    .debug-info {
        background: #fff3cd;
        padding: 0.5rem;
        border-radius: 5px;
        font-size: 0.8rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Sample business data
@st.cache_data
def get_business_data():
    return {
        'monthly_data': {
            'months': ['Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025'],
            'revenue': [95000, 105000, 98000, 125000, 118000, 130000],
            'expenses': [78000, 82000, 85000, 89000, 91000, 88000],
            'profit': [17000, 23000, 13000, 36000, 27000, 42000],
            'profit_margin': [17.9, 21.9, 13.3, 28.8, 22.9, 32.3]
        },
        'customers': {
            'names': ['ABC Trading', 'XYZ Manufacturing', 'DEF Industries', 'GHI Solutions', 'Others'],
            'revenue': [45000, 38000, 25000, 17430, 4570],
            'margin': [35, 28, 42, 31, 25],
            'region': ['KL', 'Selangor', 'Penang', 'Johor', 'Others']
        },
        'expenses': {
            'categories': ['Staff Costs', 'Marketing', 'Rent', 'Supplies', 'Utilities', 'Insurance'],
            'amounts': [35000, 15000, 12000, 11000, 8000, 7000]
        },
        'regions': {
            'names': ['KL', 'Selangor', 'Penang', 'Johor', 'Others'],
            'revenue': [45000, 38000, 25000, 17000, 5000]
        }
    }

# Truly Dynamic Chart Engine
class TrulyDynamicChartEngine:
    def __init__(self, data):
        self.data = data
    
    def analyze_request(self, user_request):
        """Analyze user request to determine exactly what they want"""
        request_lower = user_request.lower()
        
        # Initialize chart specification
        chart_spec = {
            'data_source': None,
            'chart_type': None,
            'x_axis': None,
            'y_axis': [],
            'title': '',
            'description': '',
            'time_filter': None,  # New: for date filtering
            'comparison_months': [],  # New: for specific month comparisons
            'is_modification': False,  # New: for chart modifications
            'modification_type': None,  # New: type of modification
            'secondary_axis': []  # New: for secondary axis metrics
        }
        
        # Check if this is a chart modification request
        modification_keywords = ['also', 'add', 'include', 'plus', 'with', 'and also', 'can you also']
        if any(keyword in request_lower for keyword in modification_keywords):
            chart_spec['is_modification'] = True
            
            # Determine what to add
            if any(word in request_lower for word in ['profit margin', 'margin']):
                chart_spec['modification_type'] = 'add_secondary_axis'
                chart_spec['secondary_axis'] = ['profit_margin']
            elif 'profit' in request_lower and 'margin' not in request_lower:
                chart_spec['modification_type'] = 'add_metric'
                chart_spec['y_axis'] = ['profit']
            elif 'revenue' in request_lower:
                chart_spec['modification_type'] = 'add_metric'
                chart_spec['y_axis'] = ['revenue']
            elif 'expense' in request_lower:
                chart_spec['modification_type'] = 'add_metric'
                chart_spec['y_axis'] = ['expenses']
        
        # Check for specific month/time filtering
        months_mentioned = []
        
        # Extract specific months mentioned
        month_patterns = {
            'jan': 'Jan 2025', 'january': 'Jan 2025',
            'dec': 'Dec 2024', 'december': 'Dec 2024', 
            'nov': 'Nov 2024', 'november': 'Nov 2024',
            'oct': 'Oct 2024', 'october': 'Oct 2024',
            'sep': 'Sep 2024', 'september': 'Sep 2024',
            'aug': 'Aug 2024', 'august': 'Aug 2024'
        }
        
        for month_key, month_value in month_patterns.items():
            if month_key in request_lower:
                months_mentioned.append(month_value)
        
        # Check for comparison keywords
        if any(word in request_lower for word in ['compare', 'vs', 'versus', 'against']):
            chart_spec['comparison_months'] = months_mentioned
        elif len(months_mentioned) > 0:
            chart_spec['time_filter'] = months_mentioned
        
        # Check for "last X months" patterns
        if 'last 3 months' in request_lower or 'past 3 months' in request_lower:
            chart_spec['time_filter'] = self.data['monthly_data']['months'][-3:]
        elif 'last 2 months' in request_lower or 'past 2 months' in request_lower:
            chart_spec['time_filter'] = self.data['monthly_data']['months'][-2:]
        
        # If not a modification, proceed with normal analysis
        if not chart_spec['is_modification']:
            # Determine data source and variables
            if any(word in request_lower for word in ['customer', 'client']):
                chart_spec['data_source'] = 'customers'
                chart_spec['x_axis'] = 'names'
                
                if any(word in request_lower for word in ['revenue', 'sales', 'income']):
                    chart_spec['y_axis'] = ['revenue']
                elif any(word in request_lower for word in ['margin', 'profit margin']):
                    chart_spec['y_axis'] = ['margin']
                else:
                    chart_spec['y_axis'] = ['revenue']  # default
                    
            elif any(word in request_lower for word in ['expense breakdown', 'cost breakdown', 'expense categories', 'cost categories']) and not any(word in request_lower for word in ['revenue', 'profit']):
                # Only expense breakdown when specifically asked and no other metrics mentioned
                chart_spec['data_source'] = 'expenses'
                chart_spec['x_axis'] = 'categories'
                chart_spec['y_axis'] = ['amounts']
                
            elif any(word in request_lower for word in ['region', 'area', 'location', 'geographic']):
                chart_spec['data_source'] = 'regions'
                chart_spec['x_axis'] = 'names'
                chart_spec['y_axis'] = ['revenue']
                
            else:
                # Monthly data (revenue, profit, expenses, etc.) - DEFAULT CASE
                chart_spec['data_source'] = 'monthly_data'
                chart_spec['x_axis'] = 'months'
                
                # Smart detection of multiple metrics in one request
                metrics_requested = []
                
                if any(word in request_lower for word in ['revenue', 'sales', 'income']):
                    metrics_requested.append('revenue')
                
                if any(word in request_lower for word in ['expense', 'cost', 'spending']) and 'breakdown' not in request_lower:
                    metrics_requested.append('expenses')
                
                if any(word in request_lower for word in ['profit margin', 'margin']) and 'net profit' not in request_lower:
                    metrics_requested.append('profit_margin')
                elif any(word in request_lower for word in ['profit', 'net profit']) and 'margin' not in request_lower:
                    metrics_requested.append('profit')
                
                # If multiple metrics detected, use them all
                if len(metrics_requested) > 1:
                    chart_spec['y_axis'] = metrics_requested
                elif len(metrics_requested) == 1:
                    chart_spec['y_axis'] = metrics_requested
                else:
                    # Default to revenue if nothing specific mentioned
                    chart_spec['y_axis'] = ['revenue']
        
        # Determine chart type
        if any(word in request_lower for word in ['pie', 'donut', 'distribution', 'breakdown']):
            chart_spec['chart_type'] = 'pie'
        elif any(word in request_lower for word in ['bar', 'column', 'compare', 'comparison']):
            chart_spec['chart_type'] = 'bar'
        elif any(word in request_lower for word in ['line', 'trend', 'time', 'monthly', 'over time']):
            chart_spec['chart_type'] = 'line'
        elif any(word in request_lower for word in ['area', 'filled']):
            chart_spec['chart_type'] = 'area'
        else:
            # Smart default based on data and filtering
            if chart_spec['comparison_months'] or chart_spec['time_filter']:
                chart_spec['chart_type'] = 'bar'  # Better for comparisons
            elif chart_spec['data_source'] in ['customers', 'expenses', 'regions'] and len(chart_spec['y_axis']) == 1:
                chart_spec['chart_type'] = 'pie'
            else:
                chart_spec['chart_type'] = 'line'
        
        return chart_spec
    
    def filter_monthly_data(self, data_source, time_filter=None, comparison_months=None):
        """Filter monthly data based on time specifications"""
        if time_filter:
            # Filter to specific months
            filtered_indices = [i for i, month in enumerate(data_source['months']) if month in time_filter]
            filtered_data = {}
            for key, values in data_source.items():
                if isinstance(values, list) and len(values) == len(data_source['months']):
                    filtered_data[key] = [values[i] for i in filtered_indices]
                else:
                    filtered_data[key] = values
            return filtered_data
        
        elif comparison_months:
            # Filter to comparison months only
            filtered_indices = [i for i, month in enumerate(data_source['months']) if month in comparison_months]
            filtered_data = {}
            for key, values in data_source.items():
                if isinstance(values, list) and len(values) == len(data_source['months']):
                    filtered_data[key] = [values[i] for i in filtered_indices]
                else:
                    filtered_data[key] = values
            return filtered_data
        
        return data_source
    
    def create_dynamic_chart(self, chart_spec, previous_chart_config=None):
        """Create chart based on the analyzed specification"""
        data_source = self.data[chart_spec['data_source']]
        
        # Handle chart modifications
        if chart_spec['is_modification'] and previous_chart_config:
            if chart_spec['modification_type'] == 'add_secondary_axis':
                return self.create_chart_with_secondary_axis(previous_chart_config, chart_spec)
            elif chart_spec['modification_type'] == 'add_metric':
                # Add metric to existing chart
                previous_chart_config['y_axis'].extend(chart_spec['y_axis'])
                chart_spec = previous_chart_config
                chart_spec['y_axis'] = list(set(chart_spec['y_axis']))  # Remove duplicates
        
        # Apply time filtering for monthly data
        if chart_spec['data_source'] == 'monthly_data':
            if chart_spec['time_filter'] or chart_spec['comparison_months']:
                data_source = self.filter_monthly_data(
                    data_source, 
                    chart_spec['time_filter'], 
                    chart_spec['comparison_months']
                )
        
        if chart_spec['chart_type'] == 'pie':
            # Create pie chart
            fig = go.Figure(data=[go.Pie(
                labels=data_source[chart_spec['x_axis']],
                values=data_source[chart_spec['y_axis'][0]],
                hole=.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            )])
            
            y_label = chart_spec['y_axis'][0].replace('_', ' ').title()
            title = f"🥧 {chart_spec['data_source'].replace('_', ' ').title()} {y_label} Distribution"
            
        elif chart_spec['chart_type'] == 'bar':
            # Create bar chart
            if len(chart_spec['y_axis']) == 1:
                fig = px.bar(
                    x=data_source[chart_spec['x_axis']],
                    y=data_source[chart_spec['y_axis'][0]],
                    color=data_source[chart_spec['y_axis'][0]],
                    color_continuous_scale='viridis'
                )
            else:
                # Multiple metrics
                df = pd.DataFrame(data_source)
                fig = px.bar(df, x=chart_spec['x_axis'], y=chart_spec['y_axis'])
            
            y_labels = [y.replace('_', ' ').title() for y in chart_spec['y_axis']]
            
            # Add time period to title if filtered
            time_period = ""
            if chart_spec['time_filter']:
                if len(chart_spec['time_filter']) == 2:
                    time_period = f" ({chart_spec['time_filter'][0]} vs {chart_spec['time_filter'][1]})"
                else:
                    time_period = f" ({', '.join(chart_spec['time_filter'])})"
            elif chart_spec['comparison_months']:
                time_period = f" ({' vs '.join(chart_spec['comparison_months'])})"
            
            title = f"📊 {' & '.join(y_labels)} by {chart_spec['x_axis'].replace('_', ' ').title()}{time_period}"
            
        elif chart_spec['chart_type'] == 'line':
            # Create line chart
            fig = go.Figure()
            
            colors = ['#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1']
            for i, y_metric in enumerate(chart_spec['y_axis']):
                fig.add_trace(go.Scatter(
                    x=data_source[chart_spec['x_axis']],
                    y=data_source[y_metric],
                    mode='lines+markers',
                    name=y_metric.replace('_', ' ').title(),
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=8)
                ))
            
            y_labels = [y.replace('_', ' ').title() for y in chart_spec['y_axis']]
            
            # Add time period to title if filtered
            time_period = ""
            if chart_spec['time_filter']:
                time_period = f" ({', '.join(chart_spec['time_filter'])})"
            elif chart_spec['comparison_months']:
                time_period = f" ({' vs '.join(chart_spec['comparison_months'])})"
            
            title = f"📈 {' & '.join(y_labels)} Trends{time_period}"
            
        elif chart_spec['chart_type'] == 'area':
            # Create area chart
            fig = go.Figure()
            
            for y_metric in chart_spec['y_axis']:
                fig.add_trace(go.Scatter(
                    x=data_source[chart_spec['x_axis']],
                    y=data_source[y_metric],
                    mode='lines+markers',
                    name=y_metric.replace('_', ' ').title(),
                    fill='tonexty' if len(chart_spec['y_axis']) > 1 else 'tozeroy',
                    line=dict(width=4),
                    marker=dict(size=10)
                ))
            
            y_labels = [y.replace('_', ' ').title() for y in chart_spec['y_axis']]
            
            # Add time period to title if filtered
            time_period = ""
            if chart_spec['time_filter']:
                time_period = f" ({', '.join(chart_spec['time_filter'])})"
            
            title = f"📊 {' & '.join(y_labels)} Area Chart{time_period}"
        
        # Update layout
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=400,
            showlegend=len(chart_spec['y_axis']) > 1
        )
        
        # Create description with filtering info
        y_labels = [y.replace('_', ' ') for y in chart_spec['y_axis']]
        description = f"{chart_spec['chart_type'].title()} chart showing {', '.join(y_labels)} by {chart_spec['x_axis'].replace('_', ' ')}"
        
        if chart_spec['time_filter']:
            description += f" filtered to {len(chart_spec['time_filter'])} months: {', '.join(chart_spec['time_filter'])}"
        elif chart_spec['comparison_months']:
            description += f" comparing {', '.join(chart_spec['comparison_months'])}"
        
        return fig, description, chart_spec
    
    def create_chart_with_secondary_axis(self, previous_config, new_spec):
        """Create chart with secondary axis for profit margin"""
        data_source = self.data[previous_config['data_source']]
        
        # Apply time filtering
        if previous_config['time_filter'] or previous_config['comparison_months']:
            data_source = self.filter_monthly_data(
                data_source, 
                previous_config['time_filter'], 
                previous_config['comparison_months']
            )
        
        # Create figure with secondary y-axis
        fig = go.Figure()
        
        # Add primary metrics
        colors = ['#00D4AA', '#FF6B6B', '#4ECDC4']
        for i, y_metric in enumerate(previous_config['y_axis']):
            fig.add_trace(go.Scatter(
                x=data_source[previous_config['x_axis']],
                y=data_source[y_metric],
                mode='lines+markers',
                name=y_metric.replace('_', ' ').title(),
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=8),
                yaxis='y'
            ))
        
        # Add secondary axis metric (profit margin)
        for secondary_metric in new_spec['secondary_axis']:
            fig.add_trace(go.Scatter(
                x=data_source[previous_config['x_axis']],
                y=data_source[secondary_metric],
                mode='lines+markers',
                name=secondary_metric.replace('_', ' ').title(),
                line=dict(color='#FFD700', width=3, dash='dot'),
                marker=dict(size=8, symbol='diamond'),
                yaxis='y2'
            ))
        
        # Update layout with secondary y-axis
        primary_labels = [y.replace('_', ' ').title() for y in previous_config['y_axis']]
        secondary_labels = [y.replace('_', ' ').title() for y in new_spec['secondary_axis']]
        
        time_period = ""
        if previous_config['time_filter']:
            time_period = f" ({', '.join(previous_config['time_filter'])})"
        
        fig.update_layout(
            title=f"📈 {' & '.join(primary_labels)} + {' & '.join(secondary_labels)} (Secondary Axis){time_period}",
            template="plotly_white",
            height=400,
            showlegend=True,
            yaxis=dict(
                title=' & '.join(primary_labels),
                side='left'
            ),
            yaxis2=dict(
                title=' & '.join(secondary_labels) + ' (%)',
                side='right',
                overlaying='y'
            )
        )
        
        description = f"Dual-axis chart: {', '.join(primary_labels)} (left axis) + {', '.join(secondary_labels)} (right axis)"
        
        # Merge configurations
        merged_config = previous_config.copy()
        merged_config['secondary_axis'] = new_spec['secondary_axis']
        
        return fig, description, merged_configfilter'])}"
        elif chart_spec['comparison_months']:
            description += f" comparing {', '.join(chart_spec['comparison_months'])}"
        
        return fig, description, chart_spec

# Enhanced AI Response Engine
class SmartAIEngine:
    def __init__(self, data):
        self.data = data
    
    def get_response(self, question):
        """Generate rich, contextual AI business analysis"""
        question_lower = question.lower()
        
        # Advanced Revenue Analysis
        if 'revenue' in question_lower and 'expense' not in question_lower:
            current_revenue = self.data['monthly_data']['revenue'][-1]
            prev_revenue = self.data['monthly_data']['revenue'][-2]
            growth = ((current_revenue / prev_revenue) - 1) * 100
            six_month_growth = ((current_revenue / self.data['monthly_data']['revenue'][0]) - 1) * 100
            avg_revenue = sum(self.data['monthly_data']['revenue']) / len(self.data['monthly_data']['revenue'])
            
            return f"""📈 **Revenue Deep Analysis:**
            
**Current Performance:** RM {current_revenue:,} (+{growth:.1f}% MoM)
**6-Month Growth:** {six_month_growth:.1f}% (RM {current_revenue - self.data['monthly_data']['revenue'][0]:,} increase)
**Average Monthly:** RM {avg_revenue:,.0f}
**Peak Month:** {self.data['monthly_data']['months'][self.data['monthly_data']['revenue'].index(max(self.data['monthly_data']['revenue']))]} (RM {max(self.data['monthly_data']['revenue']):,})

**💡 Strategic Insights:**
• Revenue trajectory is strongly upward - excellent momentum
• Current month is {((current_revenue/avg_revenue-1)*100):+.1f}% above 6-month average
• Growth acceleration suggests successful business strategies
• Recommend: Capitalize on momentum with increased marketing investment"""
        
        # Advanced Profit Analysis
        elif 'profit' in question_lower and 'margin' not in question_lower:
            current_profit = self.data['monthly_data']['profit'][-1]
            profit_growth = ((current_profit / self.data['monthly_data']['profit'][0]) - 1) * 100
            current_revenue = self.data['monthly_data']['revenue'][-1]
            current_expenses = self.data['monthly_data']['expenses'][-1]
            
            return f"""💰 **Profit Deep Analysis:**
            
**Current Net Profit:** RM {current_profit:,}
**6-Month Growth:** {profit_growth:.0f}% (RM {current_profit - self.data['monthly_data']['profit'][0]:,} increase)
**Profit Velocity:** +RM {(current_profit - self.data['monthly_data']['profit'][0])/6:,.0f} per month average
**ROI Trend:** Accelerating upward

**💡 Strategic Insights:**
• Exceptional profit growth - outpacing revenue growth indicates improving efficiency
• Current profit represents {(current_profit/current_revenue*100):.1f}% of revenue (healthy margin)
• Expense control excellent: RM {current_expenses:,} vs RM {current_revenue:,} revenue
• Recommendation: Consider profit reinvestment for growth acceleration"""
        
        # Advanced Profit Margin Analysis
        elif 'profit margin' in question_lower or ('margin' in question_lower and 'profit' in question_lower):
            current_margin = self.data['monthly_data']['profit_margin'][-1]
            margin_improvement = current_margin - self.data['monthly_data']['profit_margin'][0]
            best_margin_month = self.data['monthly_data']['months'][self.data['monthly_data']['profit_margin'].index(max(self.data['monthly_data']['profit_margin']))]
            
            return f"""📊 **Profit Margin Deep Analysis:**
            
**Current Margin:** {current_margin}%
**Improvement:** +{margin_improvement:.1f} percentage points since August
**Best Performance:** {best_margin_month} ({max(self.data['monthly_data']['profit_margin'])}%)
**Industry Benchmark:** Exceeding typical SME margins (15-25%)

**💡 Strategic Insights:**
• Outstanding margin improvement trajectory - operational excellence
• {current_margin}% margin puts you in top quartile of Malaysian SMEs
• Margin growth shows pricing power and cost discipline
• Risk Alert: Monitor for margin sustainability as you scale
• Opportunity: Margin leadership creates competitive moat"""
        
        # Advanced Customer Analysis
        elif 'customer' in question_lower or 'client' in question_lower:
            top_customers = sorted(zip(self.data['customers']['names'], self.data['customers']['revenue'], self.data['customers']['margin']), 
                                 key=lambda x: x[1], reverse=True)
            total_customer_revenue = sum(self.data['customers']['revenue'])
            top_3_revenue = sum([x[1] for x in top_customers[:3]])
            concentration_risk = (top_3_revenue / total_customer_revenue) * 100
            
            return f"""👥 **Customer Portfolio Deep Analysis:**
            
**Top Customer:** {top_customers[0][0]} - RM {top_customers[0][1]:,} ({top_customers[0][2]}% margin)
**#2 Customer:** {top_customers[1][0]} - RM {top_customers[1][1]:,} ({top_customers[1][2]}% margin)  
**#3 Customer:** {top_customers[2][0]} - RM {top_customers[2][1]:,} ({top_customers[2][2]}% margin)
**Customer Concentration:** {concentration_risk:.0f}% in top 3 clients

**💡 Strategic Insights:**
• **Risk Alert:** {concentration_risk:.0f}% revenue concentration creates vulnerability
• Top customer profitability varies: {min([x[2] for x in top_customers[:3]])}%-{max([x[2] for x in top_customers[:3]])}% margins
• Revenue diversification opportunity: Develop 2-3 more mid-size clients
• Customer lifetime value optimization potential in lower-margin accounts
• Recommend: Implement customer retention programs for top 3 clients"""
        
        # Advanced Expense Analysis
        elif 'expense' in question_lower or 'cost' in question_lower:
            total_expenses = sum(self.data['expenses']['amounts'])
            current_revenue = self.data['monthly_data']['revenue'][-1]
            expense_ratio = (total_expenses / current_revenue) * 100
            largest_expense = max(zip(self.data['expenses']['categories'], self.data['expenses']['amounts']), key=lambda x: x[1])
            
            return f"""💸 **Expense Deep Analysis:**
            
**Total Monthly Expenses:** RM {total_expenses:,}
**Expense Ratio:** {expense_ratio:.1f}% of revenue (excellent control)
**Largest Category:** {largest_expense[0]} - RM {largest_expense[1]:,} ({(largest_expense[1]/total_expenses*100):.1f}% of total)
**Cost Structure:** Variable vs Fixed ratio optimized

**💡 Strategic Insights:**
• Expense discipline excellent: {expense_ratio:.1f}% ratio vs industry avg 75-85%
• Staff costs at RM 35k represents investment in talent (positive signal)
• Marketing spend RM 15k shows growth focus - monitor ROI closely
• Opportunity: Utility costs RM 8k - energy audit could save 15-20%
• Scale advantage: Fixed costs will dilute as revenue grows"""
        
        # General Business Health Analysis
        elif any(word in question_lower for word in ['performance', 'business', 'health', 'analysis', 'how am i doing']):
            current_revenue = self.data['monthly_data']['revenue'][-1]
            current_profit = self.data['monthly_data']['profit'][-1]
            current_margin = self.data['monthly_data']['profit_margin'][-1]
            revenue_growth = ((current_revenue / self.data['monthly_data']['revenue'][0]) - 1) * 100
            
            return f"""🚀 **Comprehensive Business Health Analysis:**
            
**Financial Scorecard:**
• Revenue: RM {current_revenue:,} (+{revenue_growth:.1f}% growth) ✅ Excellent
• Net Profit: RM {current_profit:,} ✅ Strong  
• Profit Margin: {current_margin}% ✅ Outstanding
• Cash Generation: RM {current_profit:,}/month ✅ Healthy

**Key Strengths:**
✅ Revenue momentum accelerating
✅ Profit margins expanding (rare combination)
✅ Expense discipline maintained
✅ Strong customer base with growth potential

**Strategic Priorities:**
🎯 **Immediate (30 days):** Customer diversification planning
🎯 **Short-term (90 days):** Scale marketing while maintaining margins  
🎯 **Medium-term (180 days):** Geographic/product expansion evaluation

**Competitive Position:** Top quartile performance vs Malaysian SME benchmarks"""
        
        # Cash Flow Analysis
        elif 'cash' in question_lower or 'flow' in question_lower:
            current_profit = self.data['monthly_data']['profit'][-1]
            avg_profit = sum(self.data['monthly_data']['profit']) / len(self.data['monthly_data']['profit'])
            next_month_projection = current_profit * 1.06  # 6% growth assumption
            
            return f"""💰 **Cash Flow Deep Analysis:**
            
**Current Cash Generation:** RM {current_profit:,}/month
**6-Month Average:** RM {avg_profit:,.0f}/month  
**Next Month Projection:** RM {next_month_projection:,.0f}
**Quarterly Outlook:** RM {next_month_projection*3:,.0f}

**💡 Strategic Cash Insights:**
• Strong positive cash flow trend - excellent liquidity position
• Cash generation rate improving: +RM {(current_profit - avg_profit):,.0f} above average
• Recommendation: Set aside RM {next_month_projection*0.3:,.0f} for growth investments
• Consider: Equipment financing for expansion (leverage cheap capital)
• Opportunity: Excess cash earning potential through business reinvestment"""
        
        # Default comprehensive response
        else:
            return f"""🤖 **AI Business Intelligence Summary:**
            
**Current Performance Snapshot:**
• Revenue: RM {self.data['monthly_data']['revenue'][-1]:,} (Strong momentum)
• Profitability: {self.data['monthly_data']['profit_margin'][-1]}% margin (Excellent)
• Growth Rate: {((self.data['monthly_data']['revenue'][-1]/self.data['monthly_data']['revenue'][0])-1)*100:.1f}% over 6 months

**Key Insight:** Your business fundamentals are exceptionally strong. Revenue growth with expanding margins is a rare and valuable combination that indicates both market demand and operational excellence.

**Next Steps:** Consider strategic growth investments while maintaining your competitive advantages."""

# Main App
def main():
    st.title("🤖 Truly AI-Dynamic Chart Generator")
    st.markdown("Ask for **exactly** what you want - I'll create the perfect chart!")
    
    # Initialize data and engines
    business_data = get_business_data()
    chart_engine = TrulyDynamicChartEngine(business_data)
    ai_engine = SmartAIEngine(business_data)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "👋 Hello! I create charts based on exactly what you ask for. Try: 'revenue chart', 'customer pie chart', 'monthly profit', 'expense breakdown', etc."}
        ]
    
    # Initialize chart memory
    if 'current_chart_config' not in st.session_state:
        st.session_state.current_chart_config = None
    
    if 'chart_history' not in st.session_state:
        st.session_state.chart_history = []
    
    # Sample data display
    with st.expander("📊 View Available Data"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Monthly Data:**")
            st.write("• Revenue, Expenses, Profit, Profit Margin")
            st.write("• 6 months: Aug 2024 - Jan 2025")
            
            st.write("**Customer Data:**")
            st.write("• 5 customers with revenue & margins")
            
        with col2:
            st.write("**Expense Data:**")
            st.write("• 6 categories: Staff, Marketing, Rent, etc.")
            
            st.write("**Regional Data:**")
            st.write("• 5 regions: KL, Selangor, Penang, etc.")
    
    # Example requests
    st.markdown("### 🎯 Try These Exact Requests")
    
    example_col1, example_col2, example_col3, example_col4 = st.columns(4)
    
    with example_col1:
        if st.button("Just Revenue"):
            user_input = "my revenue chart"
            st.session_state.process_request = user_input
    
    with example_col2:
        if st.button("Monthly Profit Amount"):
            user_input = "my monthly profit"
            st.session_state.process_request = user_input
    
    with example_col3:
        if st.button("Customer Revenue Pie"):
            user_input = "customer revenue pie chart"
            st.session_state.process_request = user_input
    
    with example_col4:
        if st.button("Expense Bar Chart"):
            user_input = "expense comparison bar chart"
            st.session_state.process_request = user_input
    
    # Chat interface
    st.markdown("### 💬 Chat with AI Assistant")
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")
    
    # Chat input
    user_input = st.text_input(
        "Ask for any chart:",
        placeholder="e.g., 'revenue only', 'profit amounts by month', 'customer breakdown pie'"
    )
    
    # Process request (from button or text input)
    if st.button("Send") and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Analyze the request
        chart_spec = chart_engine.analyze_request(user_input)
        
        # Get AI response
        ai_response = ai_engine.get_response(user_input)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Store chart info for display
        st.session_state.current_chart_spec = chart_spec
        st.session_state.show_chart = True
        
        # Refresh to show new messages
        st.rerun()
    
    # Handle button requests
    if hasattr(st.session_state, 'process_request'):
        request = st.session_state.process_request
        
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": request})
        
        # Analyze the request
        chart_spec = chart_engine.analyze_request(request)
        
        # Get AI response
        ai_response = ai_engine.get_response(request)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Store chart info for display
        st.session_state.current_chart_spec = chart_spec
        st.session_state.show_chart = True
        
        # Clear the request
        del st.session_state.process_request
        
        # Refresh to show new messages
        st.rerun()
    
    # Display chart if one was requested
    if hasattr(st.session_state, 'show_chart') and st.session_state.show_chart:
        chart_spec = st.session_state.current_chart_spec
        
        # Show debug info
        st.markdown("### 🔍 AI Analysis")
        st.markdown('<div class="debug-info">', unsafe_allow_html=True)
        st.write(f"**Data Source:** {chart_spec['data_source']}")
        st.write(f"**Chart Type:** {chart_spec['chart_type']}")
        st.write(f"**X-Axis:** {chart_spec['x_axis']}")
        st.write(f"**Y-Axis:** {', '.join(chart_spec['y_axis'])}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Create and display chart
        chart_fig, chart_desc, chart_spec_updated = chart_engine.create_dynamic_chart(
            chart_spec, 
            st.session_state.current_chart_config if chart_spec.get('is_modification') else None
        )
        
        st.markdown("### 📊 Generated Chart")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(chart_fig, use_container_width=True)
        st.success(f"✅ {chart_desc}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Store current chart configuration for future modifications
        st.session_state.current_chart_config = chart_spec_updated
        st.session_state.chart_history.append({
            'request': request,
            'config': chart_spec_updated,
            'description': chart_desc
        })
        
        # Show modification tips if this was a new chart
        if not chart_spec.get('is_modification'):
            st.info("💡 **Tip:** You can now modify this chart! Try: 'also include profit margin', 'add revenue to this', etc.")
        
        # Clear the chart flag after displaying
        st.session_state.show_chart = False
    
    # Available commands
    st.markdown("### 📋 What You Can Ask For")
    st.markdown("""
    **Data Types:**
    - `revenue`, `expenses`, `profit`, `profit margin`
    - `customer`, `expense categories`, `regions`
    
    **Chart Types:**
    - `pie chart`, `bar chart`, `line chart`, `area chart`
    
    **Examples:**
    - "revenue chart" → Line chart with only revenue
    - "monthly profit" → Line chart with profit amounts  
    - "customer pie" → Pie chart of customer revenue
    - "expense bar chart" → Bar chart of expense categories
    - "profit margin trend" → Line chart of profit margins
    """)

if __name__ == "__main__":
    main()
