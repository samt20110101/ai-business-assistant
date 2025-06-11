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

# Initialize Firebase connection
db = init_firebase()

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
    # Try to load from Firebase first
    user_id = "demo_user"  # In real app, this would be actual user ID
    saved_chat = load_from_firebase('chat_histories', user_id)
    
    if saved_chat and 'messages' in saved_chat:
        st.session_state.chat_history = saved_chat['messages']
    else:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "👋 Hello! I'm your AI Business Assistant. I can analyze your finances, predict trends, and provide recommendations. Try asking me anything about your business!"}
        ]

if 'business_data' not in st.session_state:
    # Try to load from Firebase first
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

# Main header
st.markdown("""
<div class="main-header">
    <h1>🤖 AI Business Assistant</h1>
    <p>Smart Financial Intelligence for Malaysian SMEs</p>
    <div class="demo-badge">LIVE DEMO - Natural Language Business Intelligence</div>
</div>
""", unsafe_allow_html=True)

# Show Firebase connection status
if db:
    st.sidebar.success("🔥 Firebase Connected")
else:
    st.sidebar.info("📊 Using Demo Data")

# Sidebar for navigation
with st.sidebar:
    st.title("🎛️ Navigation")
    page = st.selectbox(
        "Choose Section:",
        ["Dashboard", "AI Chat", "Analytics", "Compliance", "Settings"]
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
    
    # AI Insights
    st.markdown("### 🎯 AI-Powered Business Insights")
    
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
    
    # AI Response System
    def get_ai_response(question):
        responses = {
            'cash flow': "📊 Your cash flow is healthy! Current month shows RM 36,230 net profit. Based on trends, I predict next month you'll have RM 45,000 excess cash. Recommendation: Consider investing in inventory or new equipment.",
            'performance': "🚀 Excellent performance this month! Revenue up 12% to RM 125,430, expenses down 5%, resulting in 28% profit increase. Your profit margin improved to 28.9% - above industry average of 22%.",
            'expenses': "💡 Top expense reduction opportunities: 1) Utilities increased 23% (RM 8,200) - schedule energy audit. 2) Marketing spend could be optimized - current ROI is 3.2x. 3) Negotiate better supplier rates.",
            'customers': "🎯 Customer profitability analysis: ABC Trading (RM 45k, 35% margin) and DEF Industries (RM 25k, 42% margin) are your most valuable. They represent 56% of revenue. Recommendation: Develop 2-3 similar-sized clients to reduce concentration risk.",
            'staff': "👥 Based on current workload and revenue growth, yes! Your revenue per employee is RM 41,810 (above RM 35k benchmark). Adding 1 sales person could increase revenue by RM 180k annually. ROI: 340%.",
            'prediction': "🔮 Next month prediction: Revenue RM 132,000 (+5%), Expenses RM 87,500 (-2%), Net Profit RM 44,500 (+23%). Confidence: 87%. Key factors: Seasonal uptick + new client onboarding.",
            'sst': "📋 SST Status: Next submission due 28 Feb 2025. Current quarter sales: RM 368,430. Estimated SST liability: RM 22,106. Recommendation: Set aside funds now to avoid cash flow issues.",
            'e-invoice': "📧 E-Invoice Status: Setup pending. From August 2024, all B2B transactions require e-invoicing. I can help you prepare the integration. Estimated setup time: 2 weeks."
        }
        
        question_lower = question.lower()
        for key, response in responses.items():
            if key in question_lower:
                return response
        
        return "🤖 Great question! Based on your data: Revenue trending upward (+12%), expenses controlled (-5%), profit margin strong at 28.9%. Your business fundamentals look solid. What specific aspect would you like me to analyze?"
    
    # Chat interface
    st.markdown("""
    <div class="ai-chat-container">
        <h3>Ask me anything about your business!</h3>
        <p>Try natural language questions like "How's my cash flow?" or "Should I hire more staff?"</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick query buttons
    st.markdown("**Quick Queries:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💰 How's my cash flow?"):
            st.session_state.chat_history.append({"role": "user", "content": "How's my cash flow?"})
            response = get_ai_response("cash flow")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            # Save to Firebase
            save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
    
    with col2:
        if st.button("📈 Business performance?"):
            st.session_state.chat_history.append({"role": "user", "content": "How is my business performing?"})
            response = get_ai_response("performance")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
    
    with col3:
        if st.button("🎯 Top customers analysis?"):
            st.session_state.chat_history.append({"role": "user", "content": "Which customers are most profitable?"})
            response = get_ai_response("customers")
            st.session_state.chat_history.append({"role": "assistant", "content": response})
            save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
    
    # Chat history display
    st.markdown("### Conversation")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        else:
            st.markdown(f"**AI Assistant:** {message['content']}")
    
    # Chat input
    user_input = st.text_input("Ask your question:", placeholder="e.g., 'Should I reduce expenses?' or 'Predict next quarter revenue'")
    
    if st.button("Send") and user_input:
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        response = get_ai_response(user_input)
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        # Save to Firebase
        save_to_firebase('chat_histories', 'demo_user', {'messages': st.session_state.chat_history})
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
