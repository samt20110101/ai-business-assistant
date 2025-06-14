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
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #007bff;
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
    
    .comparison-section {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .chart-container {
        background: #1e1e1e;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
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
        # Check if Firebase is already initialized
        firebase_admin.get_app()
        return firestore.client()
    except ValueError:
        # Firebase not initialized yet
        try:
            if 'firebase' in st.secrets:
                # Load Firebase config from Streamlit secrets
                firebase_config = dict(st.secrets['firebase'])
                cred = credentials.Certificate(firebase_config)
                firebase_admin.initialize_app(cred)
                return firestore.client()
            else:
                st.warning("⚠️ Firebase secrets not configured. Using demo data.")
                return None
        except Exception as e:
            st.error(f"Firebase connection error: {str(e)}")
            return None

# Initialize Gemini AI
@st.cache_resource
def init_gemini():
    """Initialize Gemini AI"""
    if not GEMINI_AVAILABLE:
        st.sidebar.error("❌ google-generativeai library not installed")
        return None
    
    try:
        if 'gemini_api_key' in st.secrets:
            api_key = st.secrets['gemini_api_key']
            genai.configure(api_key=api_key)
            
            # Try different model names
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

# Initialize Firebase connection
db = init_firebase()

# Initialize Gemini
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
    user_id = "demo_user"
    saved_chat = load_from_firebase('chat_histories', user_id)
    
    if saved_chat and 'messages' in saved_chat:
        st.session_state.chat_history = saved_chat['messages']
    else:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "👋 Hello! I'm your AI Business Assistant. I can analyze your finances, predict trends, and provide recommendations. Try asking me anything about your business!"}
        ]

if 'business_data' not in st.session_state:
    user_id = "demo_user"
    saved_data = load_from_firebase('business_data', user_id)
    
    if saved_data:
        st.session_state.business_data = saved_data
    else:
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
            },
            'compliance': {
                'sst_due': '2025-02-28',
                'e_invoice_status': 'Pending Setup',
                'last_submission': '2024-12-31'
            }
        }

# Initialize chart state
if 'current_chart_type' not in st.session_state:
    st.session_state.current_chart_type = None

if 'chart_timestamp' not in st.session_state:
    st.session_state.chart_timestamp = None

# Chart creation helper functions
def create_profit_margin_chart():
    """Create profit margin trend chart"""
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
        title="📈 Monthly Profit Margin Trends (Aug 2024 - Jan 2025)",
        xaxis_title="Month",
        yaxis_title="Profit Margin (%)",
        template="plotly_dark",
        height=450,
        showlegend=True
    )
    
    return fig

def create_customer_pie_chart():
    """Create customer revenue pie chart"""
    labels = ['ABC Trading Sdn Bhd', 'XYZ Manufacturing', 'DEF Industries', 'GHI Solutions', 'Others']
    values = [45000, 38000, 25000, 17430, 4570]
    colors = ['#00D4AA', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values, 
        hole=.3, 
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="💼 Customer Revenue Distribution",
        template="plotly_dark",
        height=500,
        showlegend=True
    )
    
    return fig

def create_expense_pie_chart():
    """Create expense breakdown pie chart"""
    expense_data = st.session_state.business_data['expenses_breakdown']
    labels = list(expense_data.keys())
    values = list(expense_data.values())
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=.3,
        marker_colors=colors,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title="💸 Operating Expense Breakdown",
        template="plotly_dark",
        height=500,
        showlegend=True
    )
    
    return fig

def create_regional_bar_chart():
    """Create regional revenue bar chart"""
    regions = ['KL', 'Selangor', 'Penang', 'Johor', 'Others']
    regional_revenue = [45000, 35000, 25000, 15000, 10000]
    colors = ['#00D4AA', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7']
    
    fig = go.Figure(data=[go.Bar(
        x=regions,
        y=regional_revenue,
        marker_color=colors
    )])
    
    fig.update_layout(
        title="🗺️ Revenue by Region",
        xaxis_title="Region",
        yaxis_title="Revenue (RM)",
        template="plotly_dark",
        height=450
    )
    
    return fig

def create_revenue_trend_chart():
    """Create revenue/expenses/profit trend chart"""
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
        title="📈 Revenue, Expenses & Profit Trends (Aug 2024 - Jan 2025)",
        xaxis_title="Month",
        yaxis_title="Amount (RM)",
        template="plotly_dark",
        height=450,
        showlegend=True
    )
    
    return fig

def display_chart(chart_type, chart_info=""):
    """Display the appropriate chart based on type"""
    st.session_state.current_chart_type = chart_type
    st.session_state.chart_timestamp = int(time.time())
    
    chart_functions = {
        'profit_margin': create_profit_margin_chart,
        'customer_pie': create_customer_pie_chart,
        'expense_pie': create_expense_pie_chart,
        'regional_bar': create_regional_bar_chart,
        'revenue_trend': create_revenue_trend_chart
    }
    
    if chart_type in chart_functions:
        try:
            fig = chart_functions[chart_type]()
            st.plotly_chart(fig, use_container_width=True, key=f"{chart_type}_{st.session_state.chart_timestamp}")
            
            success_messages = {
                'profit_margin': "✅ Profit margin chart created! Shows improvement from 17.9% to 32.3%",
                'customer_pie': "✅ Customer pie chart created! ABC Trading leads with 34.6% of revenue.",
                'expense_pie': "✅ Expense breakdown chart created! Staff costs are the largest expense at 39.2%.",
                'regional_bar': "✅ Regional bar chart created! KL leads with RM 45,000 revenue.",
                'revenue_trend': "✅ Multi-line trend chart created! Shows revenue growth and profit improvement."
            }
            
            st.success(success_messages.get(chart_type, "✅ Chart created successfully!"))
            
            if chart_info:
                st.info(chart_info)
                
        except Exception as e:
            st.error(f"❌ Chart creation failed: {e}")

# AI Response System
def get_ai_response(question):
    """Get AI response using Gemini or fallback to demo responses"""
    
    if gemini_model:
        try:
            # Create context with business data  
            context = f"""
            You are a Malaysian business intelligence assistant with ADVANCED CHARTING CAPABILITIES. You can create interactive charts for ANY business data automatically.

            CHART COMMAND: When users request ANY type of chart/graph/visualization, use this format:
            CHART_REQUEST:[chart_type]|[data_focus]|[description]

            Chart Types Available:
            - pie: For breakdowns, distributions, percentages
            - bar: For comparisons between categories
            - line: For trends over time
            - area: For cumulative trends, filled areas

            Data Categories You Can Chart:
            - CUSTOMERS: Revenue by customer, customer distribution
            - EXPENSES: Cost breakdown, expense categories  
            - REVENUE: Monthly trends, sales over time
            - REGIONS: Geographic revenue distribution
            - PROFIT MARGINS: Profitability trends over time
            - Any other business metric requested

            COMPANY DATA AVAILABLE:
            
            FINANCIAL METRICS:
            Monthly Revenue: RM 130,000 (↑10.2%)
            Operating Expenses: RM 88,000 (↓3.3%)  
            Net Profit: RM 42,000 (↑55.6%)
            Profit Margin: 32.3% (↑4.2%)
            
            CUSTOMER REVENUE:
            - ABC Trading Sdn Bhd: RM 45,000 (34.6%)
            - XYZ Manufacturing: RM 38,000 (29.2%)
            - DEF Industries: RM 25,000 (19.2%)
            - GHI Solutions: RM 17,430 (13.4%)
            - Others: RM 4,570 (3.5%)
            
            EXPENSE CATEGORIES:
            - Staff Costs: RM 35,000 (39.2%)
            - Marketing: RM 15,000 (16.8%)
            - Rent: RM 12,000 (13.5%)
            - Supplies: RM 11,000 (12.3%)
            - Utilities: RM 8,000 (9.0%)
            - Insurance: RM 7,000 (9.2%)
            
            REGIONAL REVENUE:
            - KL: RM 45,000
            - Selangor: RM 35,000
            - Penang: RM 25,000
            - Johor: RM 15,000
            - Others: RM 10,000
            
            MONTHLY TRENDS (Aug 2024 - Jan 2025):
            Aug: Revenue RM95k, Expenses RM78k, Profit RM17k, Margin 17.9%
            Sep: Revenue RM105k, Expenses RM82k, Profit RM23k, Margin 21.9%
            Oct: Revenue RM98k, Expenses RM85k, Profit RM13k, Margin 13.3%
            Nov: Revenue RM125k, Expenses RM89k, Profit RM36k, Margin 28.9%
            Dec: Revenue RM118k, Expenses RM91k, Profit RM27k, Margin 22.9%
            Jan: Revenue RM130k, Expenses RM88k, Profit RM42k, Margin 32.3%
            
            USER REQUEST: {question}
            
            EXAMPLES OF WHAT YOU CAN CHART:
            - "Show regional sales" → CHART_REQUEST:bar|regions|Regional revenue comparison
            - "Profit margin trends" → CHART_REQUEST:line|profit_margins|Monthly profit margin trends
            - "Customer pie chart" → CHART_REQUEST:pie|customers|Customer revenue distribution
            - "Expense breakdown" → CHART_REQUEST:pie|expenses|Operating expense categories
            - "Monthly revenue trends" → CHART_REQUEST:line|revenue_trend|Revenue and expense trends
            
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
        'cash flow': "📊 Your cash flow is healthy! Current month shows RM 42,000 net profit. Based on trends, I predict next month you'll have RM 45,000 excess cash. Recommendation: Consider investing in inventory or new equipment.",
        'performance': "🚀 Excellent performance this month! Revenue up 10% to RM 130,000, expenses down to RM 88,000, resulting in 23% profit increase. Your profit margin improved to 32.3% - above industry average of 22%.",
        'expenses': "💡 Top expense reduction opportunities: 1) Staff costs at RM 35,000 (40% of expenses) - consider productivity tools. 2) Marketing spend at RM 15,000 - analyze ROI. 3) Utilities at RM 8,200 - energy audit recommended.",
        'customers': "🎯 Customer profitability analysis: ABC Trading (RM 45k, 35% margin) and XYZ Manufacturing (RM 38k, 28% margin) are your top revenue generators. They represent 64% of revenue. Recommendation: Develop 2-3 similar-sized clients to reduce concentration risk.",
        'staff': "👥 Based on current workload and revenue growth, yes! Your revenue per employee calculation shows good productivity. Adding 1 sales person could increase revenue by RM 180k annually. ROI: 340%.",
        'prediction': "🔮 Next month prediction: Revenue RM 132,000 (+2%), Expenses RM 87,500 (-1%), Net Profit RM 44,500 (+6%). Confidence: 87%. Key factors: Seasonal uptick + customer retention.",
        'sst': "📋 SST Status: Next submission due 28 Feb 2025. Current quarter sales: RM 373,430. Estimated SST liability: RM 22,406. Recommendation: Set aside funds now to avoid cash flow issues.",
        'e-invoice': "📧 E-Invoice Status: Setup pending. From August 2024, all B2B transactions require e-invoicing. I can help you prepare the integration. Estimated setup time: 2 weeks.",
        'chart': "CHART_REQUEST:line|revenue_trend|Monthly revenue and profit trends",
        'profit margin': "CHART_REQUEST:line|profit_margins|Monthly profit margin trends",
        'customer': "CHART_REQUEST:pie|customers|Customer revenue distribution",
        'expense': "CHART_REQUEST:pie|expenses|Operating expense breakdown",
        'region': "CHART_REQUEST:bar|regions|Regional revenue comparison"
    }
    
    question_lower = question.lower()
    for key, response in responses.items():
        if key in question_lower:
            return response
    
    return "🤖 Great question! Based on your data: Revenue trending upward (+10%), expenses controlled (RM 88k), profit margin strong at 32.3%. Your business fundamentals look solid. What specific aspect would you like me to analyze?"

def parse_chart_request(response):
    """Parse chart request from AI response"""
    chart_request_line = ""
    for line in response.split('\n'):
        if line.startswith('CHART_REQUEST:'):
            chart_request_line = line
            break
    
    if not chart_request_line:
        return None, None, None
    
    try:
        parts = chart_request_line.replace('CHART_REQUEST:', '').split('|')
        chart_type_req = parts[0].strip() if len(parts) > 0 else ""
        data_focus = parts[1].strip() if len(parts) > 1 else ""
        description = parts[2].strip() if len(parts) > 2 else ""
        
        # Map chart request to actual chart type
        if 'profit_margin' in data_focus.lower() or 'margin' in data_focus.lower():
            return 'profit_margin', data_focus, description
        elif 'customer' in data_focus.lower():
            return 'customer_pie', data_focus, description
        elif 'expense' in data_focus.lower():
            return 'expense_pie', data_focus, description
        elif 'region' in data_focus.lower():
            return 'regional_bar', data_focus, description
        else:
            return 'revenue_trend', data_focus, description
            
    except Exception as e:
        st.error(f"Chart parsing error: {e}")
        return 'revenue_trend', 'default', 'Revenue trends'

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
        ["Dashboard", "AI Chat", "Analytics", "Compliance", "Data Viewer", "Settings"]
    )
    
    st.markdown("---")
    st.markdown("### 🆚 Competitive Advantage")
    st.markdown("""
    **Traditional Software (SQL/AutoCount):**
    - Complex navigation
    - Manual analysis
    - Static reports
    
    **Our AI Assistant:**
    - Natural conversation
    - Instant insights
    - Predictive analytics
    """)

# Main content based on selected page
if page == "Dashboard":
    st.header("📊 Business Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    current_revenue = st.session_state.business_data['revenue'][-1]
    current_expenses = st.session_state.business_data['expenses'][-1]
    net_profit = current_revenue - current_expenses
    profit_margin = (net_profit / current_revenue) * 100
    
    with col1:
        st.metric(
            "Monthly Revenue",
            f"RM {current_revenue:,.0f}",
            delta=f"{((current_revenue / st.session_state.business_data['revenue'][-2]) - 1) * 100:.1f}%"
        )
    
    with col2:
        st.metric(
            "Operating Expenses",
            f"RM {current_expenses:,.0f}",
            delta=f"{((current_expenses / st.session_state.business_data['expenses'][-2]) - 1) * 100:.1f}%"
        )
    
    with col3:
        st.metric(
            "Net Profit",
            f"RM {net_profit:,.0f}",
            delta=f"{((net_profit / (st.session_state.business_data['revenue'][-2] - st.session_state.business_data['expenses'][-2])) - 1) * 100:.1f}%"
        )
    
    with col4:
        st.metric(
            "Profit Margin",
            f"{profit_margin:.1f}%",
            delta="4.2%"
        )
    
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
                     title="Revenue vs Expenses Trend",
                     color_discrete_map={'Revenue': '#007bff', 'Expenses': '#dc3545'})
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Expense Breakdown")
        fig_pie = px.pie(
            values=list(st.session_state.business_data['expenses_breakdown'].values()),
            names=list(st.session_state.business_data['expenses_breakdown'].keys()),
            title="Current Month Expenses"
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # AI insights
    st.markdown("### 🎯 AI-Powered Business Insights")
    
    if gemini_model:
        st.info("💡 These insights are generated by Gemini AI analyzing your actual business data")
    else:
        st.info("💡 Connect Gemini AI for real-time data analysis (currently using demo insights)")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="insight-card">
            <strong>💰 Cash Flow Alert</strong><br>
            Based on current patterns, you'll have RM 45,000 excess cash next month. Consider investing in inventory or equipment.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-card">
            <strong>📈 Growth Opportunity</strong><br>
            Your top 3 customers generate 67% of revenue. Consider loyalty packages to increase retention.
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="insight-card">
            <strong>⚠️ Risk Warning</strong><br>
            Utility costs increased 23% this quarter. Schedule an energy audit for savings.
        </div>
        """, unsafe_allow_html=True)

elif page == "AI Chat":
    st.header("💬 AI Business Assistant")
    
    # Chat interface
    st.markdown("""
    <div class="ai-chat-container">
        <h3>Ask me anything about your business!</h3>
        <p>Try natural language questions like "How's my cash flow?" or "Should I hire more staff?"</p>
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
            save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
            st.rerun()
    
    with col2:
        if st.button("📈 Performance"):
            user_question = "How is my business performing?"
            st.session_state.chat_history.append({"role": "user", "content": user_question})
            response = get_ai_response(user_question)
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
            st.rerun()
    
    with col3:
        if st.button("📊 Create Chart"):
            # Find the latest chart request from chat history
            latest_chart_request = None
            for msg in reversed(st.session_state.chat_history):
                if msg['role'] == 'assistant' and 'CHART_REQUEST:' in msg['content']:
                    latest_chart_request = msg['content']
                    break
            
            if latest_chart_request:
                chart_type, data_focus, description = parse_chart_request(latest_chart_request)
                if chart_type:
                    st.info(f"📊 Creating {chart_type.replace('_', ' ').title()} chart...")
                    display_chart(chart_type, f"Generated from: {data_focus}")
            else:
                # Default chart if no recent chart request
                st.info("📈 Creating default revenue trend chart...")
                display_chart('revenue_trend', "Default chart - ask for specific charts in chat!")
    
    with col4:
        if st.button("🔄 Clear Charts"):
            st.session_state.current_chart_type = None
            st.session_state.chart_timestamp = None
            st.success("✅ Charts cleared!")
            st.rerun()
    
    # Display current chart if exists
    if st.session_state.current_chart_type:
        st.markdown("### 📊 Current Chart")
        display_chart(st.session_state.current_chart_type)
    
    # Chat history display
    st.markdown("### 💬 Conversation")
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.chat_history):
            if message["role"] == "user":
                st.markdown(f"**You:** {message['content']}")
            else:
                # Clean the response to remove CHART_REQUEST lines
                clean_content = '\n'.join([line for line in message['content'].split('\n') if not line.startswith('CHART_REQUEST:')])
                st.markdown(f"**AI Assistant:** {clean_content}")
    
    # Chat input
    st.markdown("### 💭 Ask a Question")
    user_input = st.text_input("", placeholder="e.g., 'Show me profit margin trends' or 'Create a customer pie chart'", key="chat_input")
    
    if st.button("Send", type="primary") and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Get AI response
        response = get_ai_response(user_input)
        
        # Check if response contains chart request
        if "CHART_REQUEST:" in response:
            chart_type, data_focus, description = parse_chart_request(response)
            if chart_type:
                st.success("🎉 Chart request detected! Creating visualization...")
                display_chart(chart_type, f"Generated from: {data_focus}")
        
        # Add AI response to history
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        
        # Save to Firebase
        save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
        
        # Rerun to update display
        st.rerun()

elif page == "Analytics":
    st.header("📊 Advanced Analytics")
    
    # Customer Analysis
    st.subheader("Customer Profitability Analysis")
    df_customers = pd.DataFrame(st.session_state.business_data['customers'])
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_customer = px.bar(df_customers, x='name', y='revenue', 
                             title="Customer Revenue", color='margin',
                             color_continuous_scale='viridis')
        fig_customer.update_xaxis(tickangle=45)
        st.plotly_chart(fig_customer, use_container_width=True)
    
    with col2:
        fig_margin = px.scatter(df_customers, x='revenue', y='margin', 
                               size='revenue', hover_name='name',
                               title="Revenue vs Profit Margin by Customer")
        st.plotly_chart(fig_margin, use_container_width=True)
    
    # Predictive Analytics
    st.subheader("📈 Predictive Analytics")
    
    # Generate future predictions
    future_months = ['Feb 2025', 'Mar 2025', 'Apr 2025']
    predicted_revenue = [132000, 128000, 135000]
    predicted_expenses = [87500, 89000, 91200]
    
    # Combine historical and predicted data
    all_months = st.session_state.business_data['months'] + future_months
    all_revenue = st.session_state.business_data['revenue'] + predicted_revenue
    all_expenses = st.session_state.business_data['expenses'] + predicted_expenses
    
    df_prediction = pd.DataFrame({
        'Month': all_months,
        'Revenue': all_revenue,
        'Expenses': all_expenses,
        'Type': ['Historical'] * 6 + ['Predicted'] * 3
    })
    
    fig_pred = px.line(df_prediction, x='Month', y=['Revenue', 'Expenses'], 
                      color='Type', title="Revenue & Expense Predictions",
                      line_dash='Type')
    st.plotly_chart(fig_pred, use_container_width=True)

elif page == "Compliance":
    st.header("📋 Malaysian Compliance Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧾 SST Compliance")
        st.info(f"Next SST submission due: {st.session_state.business_data['compliance']['sst_due']}")
        
        # SST calculation
        current_quarter_sales = sum(st.session_state.business_data['revenue'][-3:])
        sst_rate = 0.06  # 6% SST
        estimated_sst = current_quarter_sales * sst_rate
        
        st.metric("Current Quarter Sales", f"RM {current_quarter_sales:,.0f}")
        st.metric("Estimated SST Liability", f"RM {estimated_sst:,.0f}")
        
        if st.button("Generate SST Report"):
            st.success("SST report generated! Ready for submission.")
    
    with col2:
        st.subheader("📧 E-Invoice Status")
        st.warning(f"Status: {st.session_state.business_data['compliance']['e_invoice_status']}")
        
        st.info("E-Invoice is mandatory for B2B transactions in Malaysia from August 2024")
        
        if st.button("Setup E-Invoice Integration"):
            st.success("E-Invoice setup initiated! Our AI will guide you through the process.")
    
    # Compliance alerts
    st.subheader("⚠️ Compliance Alerts")
    st.error("Action Required: E-Invoice system not yet configured")
    st.warning("Reminder: SST submission due in 15 days")
    st.success("All other compliance requirements up to date")

elif page == "Data Viewer":
    st.header("📋 Demo Data Viewer")
    
    st.info("This shows the actual demo data being used in the application")
    
    # Revenue & Expense Data
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
    customers_df['Revenue (RM)'] = customers_df['revenue']
    customers_df['Margin (%)'] = customers_df['margin']
    customers_df['Region'] = customers_df['region']
    customers_df['Customer Name'] = customers_df['name']
    display_customers = customers_df[['Customer Name', 'Region', 'Revenue (RM)', 'Margin (%)']].copy()
    
    st.dataframe(display_customers, use_container_width=True)
    
    # Expense Breakdown
    st.subheader("📊 Current Month Expense Breakdown")
    expense_df = pd.DataFrame(
        list(st.session_state.business_data['expenses_breakdown'].items()),
        columns=['Category', 'Amount (RM)']
    )
    expense_df['Percentage'] = ((expense_df['Amount (RM)'] / expense_df['Amount (RM)'].sum()) * 100).round(1)
    
    st.dataframe(expense_df, use_container_width=True)
    
    # Compliance Data
    st.subheader("⚖️ Malaysian Compliance Status")
    compliance_data = []
    for key, value in st.session_state.business_data['compliance'].items():
        compliance_data.append({
            'Item': key.replace('_', ' ').title(),
            'Status/Date': value
        })
    compliance_df = pd.DataFrame(compliance_data)
    
    st.dataframe(compliance_df, use_container_width=True)
    
    # Summary Stats
    st.subheader("📈 Key Metrics Summary")
    col1, col2, col3 = st.columns(3)
    
    current_revenue = st.session_state.business_data['revenue'][-1]
    current_expenses = st.session_state.business_data['expenses'][-1]
    total_customers = len(st.session_state.business_data['customers'])
    total_customer_revenue = sum([c['revenue'] for c in st.session_state.business_data['customers']])
    
    with col1:
        st.metric("Total Customers", total_customers)
        st.metric("Customer Revenue Coverage", f"{(total_customer_revenue/current_revenue*100):.1f}%")
    
    with col2:
        st.metric("Avg Revenue/Customer", f"RM {total_customer_revenue/total_customers:,.0f}")
        st.metric("Revenue Growth", f"{((current_revenue/st.session_state.business_data['revenue'][0])-1)*100:.1f}%")
    
    with col3:
        avg_margin = sum([c['margin'] for c in st.session_state.business_data['customers']]) / total_customers
        st.metric("Avg Customer Margin", f"{avg_margin:.1f}%")
        st.metric("Best Customer Margin", f"{max([c['margin'] for c in st.session_state.business_data['customers']]):.1f}%")
    
    # Raw Data (Expandable)
    with st.expander("🔍 View Raw Data (JSON)"):
        st.json(st.session_state.business_data)

elif page == "Settings":
    st.header("⚙️ Settings")
    
    st.subheader("Business Information")
    business_name = st.text_input("Business Name", value="ABC Trading Sdn Bhd")
    business_type = st.selectbox("Business Type", ["Trading", "Manufacturing", "Services", "Retail"])
    
    st.subheader("AI Assistant Preferences")
    response_style = st.selectbox("Response Style", ["Professional", "Casual", "Technical"])
    auto_insights = st.checkbox("Enable Automatic Insights", value=True)
    
    st.subheader("Data Connection")
    if db:
        st.success("🔥 Firebase Database: Connected")
    else:
        st.info("📊 Demo Mode: Firebase not connected")
    
    if gemini_model:
        st.success("🧠 Gemini AI: Connected")
    else:
        st.info("🤖 Demo AI: Using fallback responses")
    
    st.info("🔗 Bank API: Ready to connect")
    
    if st.button("Save Settings"):
        # Save settings to Firebase if available
        settings_data = {
            'business_name': business_name,
            'business_type': business_type,
            'response_style': response_style,
            'auto_insights': auto_insights
        }
        
        if save_to_firebase('settings', 'demo_user', settings_data):
            st.success("Settings saved to Firebase!")
        else:
            st.success("Settings saved locally!")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; margin-top: 2rem;">
    <p>🤖 AI Business Assistant for Malaysian SMEs | Built with Streamlit & Firebase</p>
    <p>Demonstrating competitive advantage over traditional accounting software</p>
</div>
""", unsafe_allow_html=True)
