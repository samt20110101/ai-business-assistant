import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import json
import time

# Firebase imports (will use secrets directly)
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False

# Gemini AI imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Configure page
st.set_page_config(
    page_title="AI Business Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .ai-chat-container {
        background: linear-gradient(145deg, #2c3e50, #3498db);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
    }
    
    .insight-card {
        background: linear-gradient(145deg, #e74c3c, #c0392b);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
        border-left: 4px solid #f39c12;
    }
    
    .demo-badge {
        background: #ff6b6b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .chart-section {
        background: #1a1a1a;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border: 2px solid #4ECDC4;
    }
    
    .chart-updating {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        animation: pulse 2s infinite;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        color: white;
        margin: 1rem 0;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize Firebase (using Streamlit secrets directly)
@st.cache_resource
def init_firebase():
    """Initialize Firebase using Streamlit secrets"""
    if not FIREBASE_AVAILABLE:
        return None
        
    try:
        firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        try:
            if 'firebase' in st.secrets:
                firebase_config = dict(st.secrets['firebase'])
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            else:
                return None
        except Exception as e:
            st.error(f"Firebase connection error: {str(e)}")
            return None

# Initialize Gemini AI
@st.cache_resource
def init_gemini():
    """Initialize Gemini AI"""
    if not GEMINI_AVAILABLE:
        return None
    
    try:
        if 'gemini_api_key' in st.secrets:
            api_key = st.secrets['gemini_api_key']
            genai.configure(api_key=api_key)
            
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                test_response = model.generate_content("Hello")
                st.sidebar.success("✅ Gemini 1.5 Flash connected!")
                return model
            except:
                try:
                    model = genai.GenerativeModel('gemini-1.5-pro')
                    test_response = model.generate_content("Hello")
                    st.sidebar.success("✅ Gemini 1.5 Pro connected!")
                    return model
                except:
                    model = genai.GenerativeModel('gemini-pro')
                    test_response = model.generate_content("Hello")
                    st.sidebar.success("✅ Gemini Pro connected!")
                    return model
        else:
            st.sidebar.warning("⚠️ gemini_api_key not found in secrets")
            return None
    except Exception as e:
        st.sidebar.error(f"❌ Gemini error: {str(e)}")
        return None

# Initialize connections
db = init_firebase()
gemini_model = init_gemini()

# Firebase helper functions
def save_to_firebase(collection_name, document_id, data):
    """Save data to Firebase"""
    if db:
        try:
            doc_ref = db.collection(collection_name).document(document_id)
            doc_ref.set(data)
            return True
        except Exception as e:
            st.error(f"Error saving to Firebase: {str(e)}")
            return False
    return False

def load_from_firebase(collection_name, document_id):
    """Load data from Firebase"""
    if db:
        try:
            doc_ref = db.collection(collection_name).document(document_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                return None
        except Exception as e:
            st.error(f"Error loading from Firebase: {str(e)}")
            return None
    return None

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = [
        {"role": "assistant", "content": "👋 Hello! I'm your AI Business Assistant. I can analyze your finances, predict trends, and provide recommendations. Try asking me anything about your business!"}
    ]

if 'business_data' not in st.session_state:
    # Initialize with sample Malaysian SME data
    st.session_state.business_data = {
        'revenue': [95000, 105000, 98000, 125430, 118000, 130000],
        'expenses': [78000, 82000, 85000, 89200, 91000, 88000],
        'months': ['Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025'],
        'customers': [
            {'name': 'ABC Trading Sdn Bhd', 'revenue': 45000, 'margin': 35, 'region': 'KL'},
            {'name': 'XYZ Manufacturing', 'revenue': 38000, 'margin': 28, 'region': 'Selangor'},
            {'name': 'DEF Industries', 'revenue': 25000, 'margin': 42, 'region': 'Penang'},
            {'name': 'GHI Solutions', 'revenue': 17430, 'margin': 31, 'region': 'Johor'}
        ],
        'expenses_breakdown': {
            'Staff Costs': 35000,
            'Rent': 12000,
            'Utilities': 8200,
            'Marketing': 15000,
            'Supplies': 11000,
            'Insurance': 5000,
            'Others': 3000
        }
    }

# FIXED: Initialize chart state with proper defaults
if 'active_chart' not in st.session_state:
    st.session_state.active_chart = None
    
if 'chart_timestamp' not in st.session_state:
    st.session_state.chart_timestamp = None

if 'pending_chart' not in st.session_state:
    st.session_state.pending_chart = None

# FIXED: Simplified chart activation
def activate_chart(chart_type):
    """Activate a chart for display"""
    st.session_state.active_chart = chart_type
    st.session_state.chart_timestamp = int(time.time())
    st.session_state.pending_chart = None
    
def clear_charts():
    """Clear all active charts"""
    st.session_state.active_chart = None
    st.session_state.chart_timestamp = None
    st.session_state.pending_chart = None

# AI Response System
def get_ai_response(question):
    """Get AI response using Gemini or fallback to demo responses"""
    
    if gemini_model:
        try:
            context = f"""
            You are a Malaysian business intelligence assistant with ADVANCED CHARTING CAPABILITIES.

            CHART COMMAND: When users request ANY type of chart/graph/visualization, use this format:
            CHART_REQUEST:[chart_type]|[data_focus]|[description]

            Chart Types Available:
            - pie: For breakdowns, distributions, percentages
            - bar: For comparisons between categories  
            - line: For trends over time

            COMPANY DATA AVAILABLE:
            Monthly Revenue: RM 130,000 (↑10.2%)
            Operating Expenses: RM 88,000 (↓3.3%)  
            Net Profit: RM 42,000 (↑55.6%)
            Profit Margin: 32.3% (↑4.2%)
            
            CUSTOMER REVENUE:
            - ABC Trading Sdn Bhd: RM 45,000 (34.6%)
            - XYZ Manufacturing: RM 38,000 (29.2%)
            - DEF Industries: RM 25,000 (19.2%)
            - GHI Solutions: RM 17,430 (13.4%)
            
            EXPENSE CATEGORIES:
            - Staff Costs: RM 35,000 (39.2%)
            - Marketing: RM 15,000 (16.8%)
            - Rent: RM 12,000 (13.5%)
            - Supplies: RM 11,000 (12.3%)
            - Utilities: RM 8,000 (9.0%)
            - Insurance: RM 7,000 (9.2%)
            
            MONTHLY TRENDS (Aug 2024 - Jan 2025):
            Aug: Revenue RM95k, Expenses RM78k, Profit RM17k, Margin 17.9%
            Sep: Revenue RM105k, Expenses RM82k, Profit RM23k, Margin 21.9%
            Oct: Revenue RM98k, Expenses RM85k, Profit RM13k, Margin 13.3%
            Nov: Revenue RM125k, Expenses RM89k, Profit RM36k, Margin 28.9%
            Dec: Revenue RM118k, Expenses RM91k, Profit RM27k, Margin 22.9%
            Jan: Revenue RM130k, Expenses RM88k, Profit RM42k, Margin 32.3%
            
            USER REQUEST: {question}
            
            EXAMPLES:
            - "Show regional sales" → CHART_REQUEST:bar|regions|Regional revenue comparison
            - "Profit margin trends" → CHART_REQUEST:line|profit_margins|Monthly profit margin trends
            - "Customer pie chart" → CHART_REQUEST:pie|customers|Customer revenue distribution
            - "Expense breakdown" → CHART_REQUEST:pie|expenses|Operating expense categories
            - "Revenue trends" → CHART_REQUEST:line|revenue_trend|Revenue and expense trends
            
            CRITICAL: Always include the CHART_REQUEST if they want ANY visualization, then provide analysis!
            """
            
            response = gemini_model.generate_content(context)
            return f"🤖 {response.text}"
            
        except Exception as e:
            st.error(f"Gemini AI error: {str(e)}")
            return get_fallback_response(question)
    else:
        return get_fallback_response(question)

def get_fallback_response(question):
    """Fallback responses when Gemini is not available"""
    responses = {
        'cash flow': "📊 Your cash flow is healthy! Current month shows RM 42,000 net profit. Based on trends, I predict next month you'll have RM 45,000 excess cash.",
        'performance': "🚀 Excellent performance this month! Revenue up 10% to RM 130,000, expenses down to RM 88,000, resulting in 23% profit increase.",
        'chart': "CHART_REQUEST:line|revenue_trend|Monthly revenue and profit trends",
        'profit margin': "CHART_REQUEST:line|profit_margins|Monthly profit margin trends",
        'profit trend': "CHART_REQUEST:line|profit_margins|Monthly profit margin trends",
        'customer': "CHART_REQUEST:pie|customers|Customer revenue distribution", 
        'expense': "CHART_REQUEST:pie|expenses|Operating expense breakdown",
        'region': "CHART_REQUEST:bar|regions|Regional revenue comparison"
    }
    
    question_lower = question.lower()
    for key, response in responses.items():
        if key in question_lower:
            return response
    
    return "🤖 Great question! Based on your data: Revenue trending upward (+10%), expenses controlled (RM 88k), profit margin strong at 32.3%. What specific aspect would you like me to analyze?"

def parse_chart_request(response):
    """Parse chart request from AI response"""
    chart_request_line = ""
    for line in response.split('\n'):
        if line.startswith('CHART_REQUEST:'):
            chart_request_line = line
            break
    
    if not chart_request_line:
        return None
    
    try:
        parts = chart_request_line.replace('CHART_REQUEST:', '').split('|')
        data_focus = parts[1].strip() if len(parts) > 1 else ""
        
        # Map chart request to actual chart type
        if 'profit_margin' in data_focus.lower() or 'margin' in data_focus.lower():
            return 'profit_margin'
        elif 'customer' in data_focus.lower():
            return 'customer_pie'
        elif 'expense' in data_focus.lower():
            return 'expense_pie'
        elif 'region' in data_focus.lower():
            return 'regional_bar'
        else:
            return 'revenue_trend'
            
    except Exception as e:
        return 'revenue_trend'

def create_chart_display(chart_type):
    """Create chart display based on type"""
    try:
        if chart_type == "profit_margin":
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.subheader("📈 Profit Margin Trends")
            
            months = ['Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025']
            profit_margins = [17.9, 21.9, 13.3, 28.8, 22.9, 32.3]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=months, 
                y=profit_margins, 
                mode='lines+markers', 
                name='Profit Margin (%)',
                line=dict(color='#4ECDC4', width=4),
                marker=dict(size=10, color='#4ECDC4')
            ))
            
            fig.update_layout(
                title="Monthly Profit Margin Trends (Aug 2024 - Jan 2025)",
                xaxis_title="Month",
                yaxis_title="Profit Margin (%)",
                template="plotly_dark",
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"profit_margin_{st.session_state.chart_timestamp}")
            st.success("✅ Profit margin chart active")
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif chart_type == "customer_pie":
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.subheader("🥧 Customer Revenue Distribution")
            
            labels = ['ABC Trading Sdn Bhd', 'XYZ Manufacturing', 'DEF Industries', 'GHI Solutions', 'Others']
            values = [45000, 38000, 25000, 17430, 4570]
            colors = ['#00D4AA', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels, 
                values=values, 
                hole=.3, 
                marker_colors=colors,
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                title="Customer Revenue Distribution",
                template="plotly_dark",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"customer_pie_{st.session_state.chart_timestamp}")
            st.success("✅ Customer pie chart active")
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif chart_type == "expense_pie":
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.subheader("💰 Expense Breakdown")
            
            expense_data = st.session_state.business_data['expenses_breakdown']
            labels = list(expense_data.keys())
            values = list(expense_data.values())
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                hole=.3,
                marker_colors=colors,
                textinfo='label+percent'
            )])
            
            fig.update_layout(
                title="Operating Expense Breakdown",
                template="plotly_dark",
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"expense_pie_{st.session_state.chart_timestamp}")
            st.success("✅ Expense breakdown chart active")
            st.markdown('</div>', unsafe_allow_html=True)
            
        elif chart_type == "regional_bar":
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.subheader("🌏 Regional Revenue")
            
            regions = ['KL', 'Selangor', 'Penang', 'Johor', 'Others']
            regional_revenue = [45000, 35000, 25000, 15000, 10000]
            colors = ['#00D4AA', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
            
            fig = go.Figure(data=[go.Bar(
                x=regions,
                y=regional_revenue,
                marker_color=colors
            )])
            
            fig.update_layout(
                title="Revenue by Region",
                xaxis_title="Region",
                yaxis_title="Revenue (RM)",
                template="plotly_dark",
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"regional_bar_{st.session_state.chart_timestamp}")
            st.success("✅ Regional bar chart active")
            st.markdown('</div>', unsafe_allow_html=True)
            
        else:  # revenue_trend
            st.markdown('<div class="chart-section">', unsafe_allow_html=True)
            st.subheader("📈 Revenue, Expenses & Profit Trends")
            
            months = ['Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025']
            revenue = [95000, 105000, 98000, 125000, 118000, 130000]
            expenses = [78000, 82000, 85000, 89000, 91000, 88000]
            profit = [17000, 23000, 13000, 36000, 27000, 42000]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=months, y=revenue, mode='lines+markers', name='Revenue', 
                                   line=dict(color='#00D4AA', width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=months, y=expenses, mode='lines+markers', name='Expenses', 
                                   line=dict(color='#FF6B6B', width=3), marker=dict(size=8)))
            fig.add_trace(go.Scatter(x=months, y=profit, mode='lines+markers', name='Profit', 
                                   line=dict(color='#4ECDC4', width=3), marker=dict(size=8)))
            
            fig.update_layout(
                title="Revenue, Expenses & Profit Trends (Aug 2024 - Jan 2025)",
                xaxis_title="Month",
                yaxis_title="Amount (RM)",
                template="plotly_dark",
                height=450
            )
            
            st.plotly_chart(fig, use_container_width=True, key=f"revenue_trend_{st.session_state.chart_timestamp}")
            st.success("✅ Multi-line trend chart active")
            st.markdown('</div>', unsafe_allow_html=True)
            
    except Exception as e:
        st.error(f"❌ Chart display failed: {e}")

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Business Assistant</h1>
    <p>Smart Financial Intelligence for Malaysian SMEs</p>
    <div class="demo-badge">LIVE DEMO - Natural Language Business Intelligence</div>
</div>
""", unsafe_allow_html=True)

# Show connection status
if db:
    st.sidebar.success("🔥 Firebase Connected")
else:
    st.sidebar.info("📊 Using Demo Data")

if gemini_model:
    st.sidebar.success("🧠 Gemini AI Connected")
else:
    st.sidebar.info("🤖 Using Demo AI Responses")

# Sidebar for navigation
with st.sidebar:
    st.title("🎛️ Navigation")
    page = st.selectbox(
        "Choose Section:",
        ["Dashboard", "AI Chat", "Analytics", "Data Viewer", "Settings"]
    )

# Main content based on selected page
if page == "AI Chat":
    st.header("💬 AI Business Assistant")
    
    # Chat interface
    st.markdown("""
    <div class="ai-chat-container">
        <h3>Ask me anything about your business!</h3>
        <p>Try natural language questions like "How's my cash flow?" or "Show me profit margin trends"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick query buttons
    st.markdown("**Quick Queries:**")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("💰 Cash Flow"):
            user_question = "How's my cash flow?"
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            response = get_ai_response(user_question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("📈 Performance"):
            user_question = "How is my business performing?"
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            response = get_ai_response(user_question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("📊 Revenue Chart"):
            activate_chart('revenue_trend')
            st.rerun()
    
    with col4:
        if st.button("🔄 Clear Charts"):
            clear_charts()
            st.rerun()
    
    # FIXED: Chart display FIRST (before conversation) - this ensures charts update immediately
    if st.session_state.active_chart and st.session_state.chart_timestamp:
        st.markdown("### 📊 Active Chart")
        create_chart_display(st.session_state.active_chart)
    
    # Chat history display
    st.markdown("### 💬 Conversation")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            # Check for chart requests and activate them IMMEDIATELY
            if "CHART_REQUEST:" in message['content']:
                # Show clean response without CHART_REQUEST line
                clean_content = '\n'.join([line for line in message['content'].split('\n') if not line.startswith('CHART_REQUEST:')])
                st.markdown(f"**AI Assistant:** {clean_content}")
                
                # FIXED: Activate chart immediately when processing the message
                chart_type = parse_chart_request(message['content'])
                if chart_type and chart_type != st.session_state.active_chart:
                    # Set pending chart to trigger on next rerun
                    st.session_state.pending_chart = chart_type
            else:
                st.markdown(f"**AI Assistant:** {message['content']}")
    
    # FIXED: Process pending charts
    if st.session_state.pending_chart:
        activate_chart(st.session_state.pending_chart)
        st.rerun()
    
    # Chat input
    st.markdown("### 💭 Ask a Question")
    user_input = st.text_input("", placeholder="e.g., 'Show me profit margin trends' or 'Create a customer pie chart'", key="chat_input")
    
    if st.button("Send", type="primary") and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        response = get_ai_response(user_input)
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # FIXED: Check for chart requests and activate immediately
        if "CHART_REQUEST:" in response:
            chart_type = parse_chart_request(response)
            if chart_type:
                activate_chart(chart_type)
        
        # Save to Firebase
        save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
        
        # Rerun to update display
        st.rerun()

elif page == "Dashboard":
    st.header("📊 Business Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    current_revenue = st.session_state.business_data['revenue'][-1]
    current_expenses = st.session_state.business_data['expenses'][-1]
    net_profit = current_revenue - current_expenses
    profit_margin = (net_profit / current_revenue) * 100
    
    with col1:
        st.metric("Monthly Revenue", f"RM {current_revenue:,.0f}", delta="10.2%")
    with col2:
        st.metric("Operating Expenses", f"RM {current_expenses:,.0f}", delta="-3.3%")
    with col3:
        st.metric("Net Profit", f"RM {net_profit:,.0f}", delta="55.6%")
    with col4:
        st.metric("Profit Margin", f"{profit_margin:.1f}%", delta="4.2%")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Revenue Trend")
        df_revenue = pd.DataFrame({
            'Month': st.session_state.business_data['months'],
            'Revenue': st.session_state.business_data['revenue'],
            'Expenses': st.session_state.business_data['expenses']
        })
        
        fig = px.line(df_revenue, x='Month', y=['Revenue', 'Expenses'], 
                     title="Revenue vs Expenses Trend")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Expense Breakdown")
        fig_pie = px.pie(
            values=list(st.session_state.business_data['expenses_breakdown'].values()),
            names=list(st.session_state.business_data['expenses_breakdown'].keys()),
            title="Current Month Expenses"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

elif page == "Analytics":
    st.header("📊 Advanced Analytics")
    
    # Quick Chart Buttons
    st.subheader("📈 Quick Charts")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📈 Profit Margins", key="profit_btn"):
            activate_chart('profit_margin')
            st.rerun()
    
    with col2:
        if st.button("🥧 Customer Distribution", key="customer_btn"):
            activate_chart('customer_pie')
            st.rerun()
    
    with col3:
        if st.button("💰 Expense Breakdown", key="expense_btn"):
            activate_chart('expense_pie')
            st.rerun()
    
    with col4:
        if st.button("🌏 Regional Revenue", key="regional_btn"):
            activate_chart('regional_bar')
            st.rerun()
    
    # Chart display section for Analytics page
    if st.session_state.active_chart and st.session_state.chart_timestamp:
        st.markdown("### 📊 Active Chart")
        create_chart_display(st.session_state.active_chart)

elif page == "Data Viewer":
    st.header("📋 Demo Data Viewer")
    
    # Financial Data
    st.subheader("💰 Financial Data (Last 6 Months)")
    financial_df = pd.DataFrame({
        'Month': st.session_state.business_data['months'],
        'Revenue (RM)': st.session_state.business_data['revenue'],
        'Expenses (RM)': st.session_state.business_data['expenses']
    })
    financial_df['Net Profit (RM)'] = financial_df['Revenue (RM)'] - financial_df['Expenses (RM)']
    financial_df['Profit Margin (%)'] = ((financial_df['Net Profit (RM)'] / financial_df['Revenue (RM)']) * 100).round(1)
    
    st.dataframe(financial_df, use_container_width=True)
    
    # Customer Data
    st.subheader("🎯 Customer Portfolio")
    customers_df = pd.DataFrame(st.session_state.business_data['customers'])
    st.dataframe(customers_df, use_container_width=True)

elif page == "Settings":
    st.header("⚙️ Settings")
    
    st.subheader("Chart Preferences")
    chart_theme = st.selectbox("Chart Theme", ["Dark", "Light", "Colorful"])
    auto_chart = st.checkbox("Auto-generate charts from AI responses", value=True)
    
    st.subheader("Data Connection")
    if db:
        st.success("🔥 Firebase Database: Connected")
    else:
        st.info("📊 Demo Mode: Firebase not connected")
    
    if gemini_model:
        st.success("🧠 Gemini AI: Connected")
    else:
        st.info("🤖 Demo AI: Using fallback responses")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🤖 AI Business Assistant for Malaysian SMEs | Built with Streamlit & Firebase</p>
</div>
""", unsafe_allow_html=True)
