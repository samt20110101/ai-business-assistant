import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import re

# Configure page
st.set_page_config(
    page_title="AI Business Assistant",
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
    
    .demo-data {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Sample business data - clean and structured
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

# Chart generation engine
class ChartEngine:
    def __init__(self, data):
        self.data = data
    
    def parse_chart_request(self, ai_response):
        """Parse AI response for chart requests"""
        patterns = {
            'revenue_trend': r'(revenue.*trend|monthly.*revenue|revenue.*time|trend.*revenue)',
            'profit_trend': r'(profit.*trend|profit.*margin|margin.*trend)',
            'customer_pie': r'(customer.*pie|customer.*distribution|pie.*customer)',
            'expense_pie': r'(expense.*breakdown|expense.*pie|cost.*breakdown)',
            'regional_bar': r'(regional.*sales|region.*revenue|sales.*region)',
            'customer_bar': r'(customer.*revenue|top.*customer|customer.*comparison)',
            'expense_bar': r'(expense.*comparison|cost.*category)',
            'profit_line': r'(profit.*line|net.*profit|profit.*month)'
        }
        
        response_lower = ai_response.lower()
        
        for chart_type, pattern in patterns.items():
            if re.search(pattern, response_lower):
                return chart_type
        
        # Default based on keywords
        if any(word in response_lower for word in ['pie', 'breakdown', 'distribution']):
            return 'customer_pie'
        elif any(word in response_lower for word in ['trend', 'line', 'time', 'monthly']):
            return 'revenue_trend'
        elif any(word in response_lower for word in ['bar', 'comparison', 'compare']):
            return 'customer_bar'
        
        return 'revenue_trend'  # Default
    
    def create_chart(self, chart_type):
        """Create specific chart based on type"""
        
        if chart_type == 'revenue_trend':
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.data['monthly_data']['months'],
                y=self.data['monthly_data']['revenue'],
                mode='lines+markers',
                name='Revenue',
                line=dict(color='#00D4AA', width=3),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=self.data['monthly_data']['months'],
                y=self.data['monthly_data']['expenses'],
                mode='lines+markers',
                name='Expenses',
                line=dict(color='#FF6B6B', width=3),
                marker=dict(size=8)
            ))
            fig.update_layout(
                title="📈 Revenue & Expenses Trend",
                xaxis_title="Month",
                yaxis_title="Amount (RM)",
                template="plotly_white",
                height=400
            )
            return fig, "Line chart showing revenue and expense trends over 6 months"
        
        elif chart_type == 'profit_trend':
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.data['monthly_data']['months'],
                y=self.data['monthly_data']['profit_margin'],
                mode='lines+markers',
                name='Profit Margin (%)',
                line=dict(color='#4ECDC4', width=4),
                marker=dict(size=10),
                fill='tonexty'
            ))
            fig.update_layout(
                title="📊 Profit Margin Trends",
                xaxis_title="Month",
                yaxis_title="Profit Margin (%)",
                template="plotly_white",
                height=400
            )
            return fig, "Area chart showing profit margin growth from 17.9% to 32.3%"
        
        elif chart_type == 'customer_pie':
            fig = go.Figure(data=[go.Pie(
                labels=self.data['customers']['names'],
                values=self.data['customers']['revenue'],
                hole=.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            )])
            fig.update_layout(
                title="🥧 Customer Revenue Distribution",
                template="plotly_white",
                height=400
            )
            return fig, "Pie chart showing revenue contribution by top customers"
        
        elif chart_type == 'expense_pie':
            fig = go.Figure(data=[go.Pie(
                labels=self.data['expenses']['categories'],
                values=self.data['expenses']['amounts'],
                hole=.3,
                marker_colors=['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
            )])
            fig.update_layout(
                title="💰 Expense Breakdown",
                template="plotly_white",
                height=400
            )
            return fig, "Pie chart showing expense distribution by category"
        
        elif chart_type == 'regional_bar':
            fig = px.bar(
                x=self.data['regions']['names'],
                y=self.data['regions']['revenue'],
                title="🌍 Regional Revenue Distribution",
                color=self.data['regions']['revenue'],
                color_continuous_scale='viridis'
            )
            fig.update_layout(template="plotly_white", height=400)
            return fig, "Bar chart comparing revenue across regions"
        
        elif chart_type == 'customer_bar':
            fig = px.bar(
                x=self.data['customers']['names'],
                y=self.data['customers']['revenue'],
                title="👥 Customer Revenue Comparison",
                color=self.data['customers']['margin'],
                color_continuous_scale='plasma'
            )
            fig.update_xaxis(tickangle=45)
            fig.update_layout(template="plotly_white", height=400)
            return fig, "Bar chart showing revenue by customer with profit margin colors"
        
        elif chart_type == 'profit_line':
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=self.data['monthly_data']['months'],
                y=self.data['monthly_data']['profit'],
                mode='lines+markers',
                name='Net Profit',
                line=dict(color='#00C851', width=4),
                marker=dict(size=10)
            ))
            fig.update_layout(
                title="💰 Net Profit Trends",
                xaxis_title="Month",
                yaxis_title="Net Profit (RM)",
                template="plotly_white",
                height=400
            )
            return fig, "Line chart showing net profit trends over time"
        
        else:
            # Default revenue trend
            return self.create_chart('revenue_trend')

# AI Response Engine
class AIEngine:
    def __init__(self, data):
        self.data = data
    
    def get_response(self, question):
        """Generate AI response based on question"""
        question_lower = question.lower()
        
        # Chart-related responses
        if any(word in question_lower for word in ['chart', 'graph', 'show', 'visualize', 'plot']):
            if any(word in question_lower for word in ['customer', 'client']):
                return "Here's your customer analysis! Your top 3 customers (ABC Trading, XYZ Manufacturing, DEF Industries) contribute 83% of total revenue. ABC Trading leads with RM 45k revenue and 35% margin. I'll show you the customer distribution chart.", 'customer_pie'
            elif any(word in question_lower for word in ['expense', 'cost', 'spending']):
                return "Let me break down your expenses. Staff costs dominate at RM 35k (40% of total), followed by marketing at RM 15k. This suggests a healthy investment in people and growth. Here's the expense breakdown chart.", 'expense_pie'
            elif any(word in question_lower for word in ['profit', 'margin']):
                return "Excellent profit performance! Your margin improved from 17.9% to 32.3% over 6 months - that's phenomenal growth. This shows strong operational efficiency improvements. Here's your profit trend chart.", 'profit_trend'
            elif any(word in question_lower for word in ['region', 'area', 'location']):
                return "Your regional performance shows KL leading with RM 45k, followed by Selangor (RM 38k) and Penang (RM 25k). Consider expanding marketing in underperforming regions. Here's the regional breakdown.", 'regional_bar'
            else:
                return "Here's your overall business trend! Revenue grew 37% from Aug to Jan, reaching RM 130k. Expenses are well-controlled at RM 88k. Your business is on a strong growth trajectory! Let me show you the trends.", 'revenue_trend'
        
        # Non-chart responses
        elif any(word in question_lower for word in ['cash', 'flow', 'money']):
            return "💰 Your cash flow is excellent! Current month: RM 42k net profit. Based on trends, next month should generate RM 45k excess cash. Recommendation: Consider investing in inventory or equipment for growth.", None
        
        elif any(word in question_lower for word in ['performance', 'how am i doing']):
            return "🚀 Outstanding performance! Revenue up 10% to RM 130k, expenses down 3% to RM 88k, profit up 56% to RM 42k. Your 32.3% profit margin beats industry average of 22%. Keep it up!", None
        
        elif any(word in question_lower for word in ['hire', 'staff', 'employee']):
            return "👥 Based on your RM 130k revenue and current workload, yes! Revenue per employee analysis shows good productivity. Adding 1 sales person could increase revenue by RM 180k annually. ROI: 340%.", None
        
        elif any(word in question_lower for word in ['predict', 'forecast', 'future']):
            return "🔮 Next month prediction: Revenue RM 132k (+2%), Expenses RM 87.5k (-1%), Net Profit RM 44.5k (+6%). Confidence: 87%. Growth drivers: customer retention + seasonal uptick.", None
        
        else:
            return "🤖 I'm analyzing your business data... Revenue trending upward (+37% growth), expenses controlled, profit margin strong at 32.3%. Your fundamentals look solid! What specific aspect would you like me to analyze or visualize?", None

# Main App
def main():
    st.title("🤖 AI Business Assistant with Dynamic Charts")
    st.markdown("Ask me to show you any business chart and I'll create it instantly!")
    
    # Initialize data and engines
    business_data = get_business_data()
    chart_engine = ChartEngine(business_data)
    ai_engine = AIEngine(business_data)
    
    # Initialize session state
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "👋 Hello! I can analyze your business data and create dynamic charts. Try asking: 'Show me customer revenue pie chart' or 'Create profit trend graph'"}
        ]
    
    # Sample data display
    with st.expander("📊 View Sample Business Data"):
        st.markdown('<div class="demo-data">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Monthly Revenue:**")
            for i, month in enumerate(business_data['monthly_data']['months']):
                st.write(f"{month}: RM {business_data['monthly_data']['revenue'][i]:,}")
        
        with col2:
            st.write("**Top Customers:**")
            for i, customer in enumerate(business_data['customers']['names'][:4]):
                st.write(f"{customer}: RM {business_data['customers']['revenue'][i]:,}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Quick chart buttons
    st.markdown("### 🎯 Quick Chart Examples")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Revenue Trends"):
            ai_response, chart_type = ai_engine.get_response("show revenue trends")
            chart_fig, chart_desc = chart_engine.create_chart(chart_type)
            
            st.markdown('<div class="ai-response">', unsafe_allow_html=True)
            st.write(f"**AI:** {ai_response}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(chart_fig, use_container_width=True)
            st.success(f"✅ {chart_desc}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        if st.button("🥧 Customer Pie"):
            ai_response, chart_type = ai_engine.get_response("show customer pie chart")
            chart_fig, chart_desc = chart_engine.create_chart(chart_type)
            
            st.markdown('<div class="ai-response">', unsafe_allow_html=True)
            st.write(f"**AI:** {ai_response}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(chart_fig, use_container_width=True)
            st.success(f"✅ {chart_desc}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        if st.button("💰 Profit Margins"):
            ai_response, chart_type = ai_engine.get_response("show profit margin trends")
            chart_fig, chart_desc = chart_engine.create_chart(chart_type)
            
            st.markdown('<div class="ai-response">', unsafe_allow_html=True)
            st.write(f"**AI:** {ai_response}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(chart_fig, use_container_width=True)
            st.success(f"✅ {chart_desc}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        if st.button("🌍 Regional Sales"):
            ai_response, chart_type = ai_engine.get_response("show regional revenue")
            chart_fig, chart_desc = chart_engine.create_chart(chart_type)
            
            st.markdown('<div class="ai-response">', unsafe_allow_html=True)
            st.write(f"**AI:** {ai_response}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            st.plotly_chart(chart_fig, use_container_width=True)
            st.success(f"✅ {chart_desc}")
            st.markdown('</div>', unsafe_allow_html=True)
    
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
        "Ask me anything about your business or request a chart:",
        placeholder="e.g., 'Show customer revenue breakdown' or 'Create expense pie chart'"
    )
    
    if st.button("Send") and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        ai_response, chart_type = ai_engine.get_response(user_input)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
        
        # Store chart info in session state if chart is needed
        if chart_type:
            st.session_state.show_chart = True
            st.session_state.chart_type = chart_type
        
        # Refresh to show new messages and chart
        st.rerun()
    
    # Display chart if one was requested
    if hasattr(st.session_state, 'show_chart') and st.session_state.show_chart:
        chart_fig, chart_desc = chart_engine.create_chart(st.session_state.chart_type)
        
        st.markdown("### 📊 Generated Chart")
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(chart_fig, use_container_width=True)
        st.success(f"✅ {chart_desc}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Clear the chart flag
        st.session_state.show_chart = False
    
    # Available chart types
    st.markdown("### 📋 Available Chart Types")
    st.markdown("""
    **Try these commands:**
    - "Show revenue trends" → Line chart with revenue/expenses
    - "Customer pie chart" → Pie chart of customer revenue
    - "Profit margin trends" → Area chart of profit margins  
    - "Regional sales breakdown" → Bar chart by region
    - "Expense breakdown" → Pie chart of expense categories
    - "Customer revenue comparison" → Bar chart of customer revenue
    - "Show me profit trends" → Line chart of net profit
    """)

if __name__ == "__main__":
    main()
