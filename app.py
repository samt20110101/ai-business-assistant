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
            'description': ''
        }
        
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
                
        elif any(word in request_lower for word in ['expense', 'cost', 'spending']):
            chart_spec['data_source'] = 'expenses'
            chart_spec['x_axis'] = 'categories'
            chart_spec['y_axis'] = ['amounts']
            
        elif any(word in request_lower for word in ['region', 'area', 'location', 'geographic']):
            chart_spec['data_source'] = 'regions'
            chart_spec['x_axis'] = 'names'
            chart_spec['y_axis'] = ['revenue']
            
        else:
            # Monthly data (revenue, profit, expenses, etc.)
            chart_spec['data_source'] = 'monthly_data'
            chart_spec['x_axis'] = 'months'
            
            # Determine which metrics to show
            if 'revenue' in request_lower and 'expense' not in request_lower:
                chart_spec['y_axis'] = ['revenue']
            elif 'expense' in request_lower and 'revenue' not in request_lower:
                chart_spec['y_axis'] = ['expenses']
            elif any(word in request_lower for word in ['profit margin', 'margin']):
                chart_spec['y_axis'] = ['profit_margin']
            elif any(word in request_lower for word in ['profit', 'net profit']) and 'margin' not in request_lower:
                chart_spec['y_axis'] = ['profit']
            elif 'revenue' in request_lower and 'expense' in request_lower:
                chart_spec['y_axis'] = ['revenue', 'expenses']
            else:
                # Default to revenue
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
            # Smart default based on data
            if chart_spec['data_source'] in ['customers', 'expenses', 'regions'] and len(chart_spec['y_axis']) == 1:
                chart_spec['chart_type'] = 'pie'
            else:
                chart_spec['chart_type'] = 'line'
        
        return chart_spec
    
    def create_dynamic_chart(self, chart_spec):
        """Create chart based on the analyzed specification"""
        data_source = self.data[chart_spec['data_source']]
        
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
            title = f"📊 {' & '.join(y_labels)} by {chart_spec['x_axis'].replace('_', ' ').title()}"
            
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
            title = f"📈 {' & '.join(y_labels)} Trends"
            
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
            title = f"📊 {' & '.join(y_labels)} Area Chart"
        
        # Update layout
        fig.update_layout(
            title=title,
            template="plotly_white",
            height=400,
            showlegend=len(chart_spec['y_axis']) > 1
        )
        
        # Create description
        y_labels = [y.replace('_', ' ') for y in chart_spec['y_axis']]
        description = f"{chart_spec['chart_type'].title()} chart showing {', '.join(y_labels)} by {chart_spec['x_axis'].replace('_', ' ')}"
        
        return fig, description, chart_spec

# AI Response Engine
class SmartAIEngine:
    def __init__(self, data):
        self.data = data
    
    def get_response(self, question):
        """Generate contextual AI response"""
        question_lower = question.lower()
        
        # Revenue-specific responses
        if 'revenue' in question_lower and 'expense' not in question_lower:
            current_revenue = self.data['monthly_data']['revenue'][-1]
            growth = ((current_revenue / self.data['monthly_data']['revenue'][-2]) - 1) * 100
            return f"📈 Revenue Analysis: Current month revenue is RM {current_revenue:,}, up {growth:.1f}% from last month. Revenue has grown {((current_revenue / self.data['monthly_data']['revenue'][0]) - 1) * 100:.1f}% over the past 6 months!"
        
        # Profit-specific responses  
        elif 'profit' in question_lower and 'margin' not in question_lower:
            current_profit = self.data['monthly_data']['profit'][-1]
            return f"💰 Profit Analysis: Current month net profit is RM {current_profit:,}. Your profit has grown significantly - from RM 17k in Aug to RM 42k in Jan, that's a {((current_profit / self.data['monthly_data']['profit'][0]) - 1) * 100:.0f}% increase!"
        
        # Profit margin responses
        elif 'profit margin' in question_lower or 'margin' in question_lower:
            current_margin = self.data['monthly_data']['profit_margin'][-1]
            return f"📊 Profit Margin Analysis: Current margin is {current_margin}%, up from 17.9% in August. This shows excellent operational efficiency improvements!"
        
        # Customer responses
        elif 'customer' in question_lower:
            top_customer_revenue = max(self.data['customers']['revenue'])
            return f"👥 Customer Analysis: ABC Trading is your top customer with RM {top_customer_revenue:,} revenue. Your top 3 customers contribute {(sum(self.data['customers']['revenue'][:3]) / sum(self.data['customers']['revenue']) * 100):.0f}% of total revenue."
        
        # Default response
        else:
            return f"🤖 I've analyzed your request and created the chart below. Your business shows strong performance with RM {self.data['monthly_data']['revenue'][-1]:,} current revenue!"

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
        chart_fig, chart_desc, chart_spec_updated = chart_engine.create_dynamic_chart(chart_spec)
        
        st.markdown("### 📊 Generated Chart")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(chart_fig, use_container_width=True)
        st.success(f"✅ {chart_desc}")
        st.markdown('</div>', unsafe_allow_html=True)
        
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
