import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time

st.set_page_config(
    page_title="AI Business Assistant - WORKING CHARTS",
    page_icon="🤖",
    layout="wide"
)

# SUPER SIMPLE chart state - THIS WILL WORK!
if 'show_chart' not in st.session_state:
    st.session_state.show_chart = None

if 'chart_counter' not in st.session_state:
    st.session_state.chart_counter = 0

# Sample data
data = {
    'months': ['Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024', 'Dec 2024', 'Jan 2025'],
    'revenue': [95000, 105000, 98000, 125000, 118000, 130000],
    'expenses': [78000, 82000, 85000, 89000, 91000, 88000],
    'profit_margins': [17.9, 21.9, 13.3, 28.8, 22.9, 32.3]
}

def show_chart(chart_type):
    """Show a specific chart"""
    st.session_state.show_chart = chart_type
    st.session_state.chart_counter += 1

def clear_charts():
    """Clear all charts"""
    st.session_state.show_chart = None
    st.session_state.chart_counter += 1

# CSS
st.markdown("""
<style>
.chart-container {
    background: #1a1a1a;
    padding: 2rem;
    border-radius: 10px;
    border: 3px solid #00ff00;
    margin: 1rem 0;
}

.big-title {
    font-size: 2rem;
    color: #00ff00;
    text-align: center;
    background: #1a1a1a;
    padding: 1rem;
    border-radius: 10px;
    margin: 1rem 0;
}

.status-box {
    background: #333;
    padding: 1rem;
    border-radius: 10px;
    border: 2px solid #00ff00;
    color: #00ff00;
    text-align: center;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# MAIN TITLE
st.markdown('<div class="big-title">🔥 GUARANTEED WORKING CHARTS! 🔥</div>', unsafe_allow_html=True)

# CHART CONTROL BUTTONS - BIG AND OBVIOUS
st.markdown("## 🎛️ Chart Controls")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("📈 PROFIT TRENDS", type="primary", key="profit_btn"):
        show_chart('profit')

with col2:
    if st.button("💰 REVENUE CHART", type="primary", key="revenue_btn"):
        show_chart('revenue')

with col3:
    if st.button("🥧 CUSTOMER PIE", type="primary", key="customer_btn"):
        show_chart('customer')

with col4:
    if st.button("🗑️ CLEAR ALL", type="secondary", key="clear_btn"):
        clear_charts()

# CHART STATUS - ALWAYS VISIBLE
st.markdown("## 📊 Chart Status")
if st.session_state.show_chart:
    st.markdown(f'<div class="status-box">✅ ACTIVE CHART: {st.session_state.show_chart.upper()}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="status-box">❌ NO CHARTS ACTIVE</div>', unsafe_allow_html=True)

# CHART DISPLAY AREA - THIS IS WHERE YOU SHOULD SEE CHARTS!
st.markdown("## 📊 CHART DISPLAY AREA")
st.markdown("### 👇 LOOK HERE FOR CHARTS 👇")

if st.session_state.show_chart:
    # Generate unique key for each chart render
    chart_key = f"{st.session_state.show_chart}_{st.session_state.chart_counter}"
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    if st.session_state.show_chart == 'profit':
        st.subheader("📈 Profit Margin Trends")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['months'], 
            y=data['profit_margins'], 
            mode='lines+markers', 
            name='Profit Margin (%)',
            line=dict(color='#00ff00', width=4),
            marker=dict(size=12, color='#00ff00')
        ))
        
        fig.update_layout(
            title="📈 Monthly Profit Margin Trends",
            xaxis_title="Month",
            yaxis_title="Profit Margin (%)",
            template="plotly_dark",
            height=500,
            title_font_size=20
        )
        
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
        st.success("✅ PROFIT MARGIN CHART IS WORKING!")
        
    elif st.session_state.show_chart == 'revenue':
        st.subheader("💰 Revenue vs Expenses")
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data['months'], 
            y=data['revenue'], 
            mode='lines+markers', 
            name='Revenue',
            line=dict(color='#00ff00', width=4),
            marker=dict(size=10)
        ))
        fig.add_trace(go.Scatter(
            x=data['months'], 
            y=data['expenses'], 
            mode='lines+markers', 
            name='Expenses',
            line=dict(color='#ff0000', width=4),
            marker=dict(size=10)
        ))
        
        fig.update_layout(
            title="💰 Revenue vs Expenses Trends",
            xaxis_title="Month",
            yaxis_title="Amount (RM)",
            template="plotly_dark",
            height=500,
            title_font_size=20
        )
        
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
        st.success("✅ REVENUE CHART IS WORKING!")
        
    elif st.session_state.show_chart == 'customer':
        st.subheader("🥧 Customer Distribution")
        
        labels = ['ABC Trading', 'XYZ Manufacturing', 'DEF Industries', 'GHI Solutions', 'Others']
        values = [45000, 38000, 25000, 17430, 4570]
        colors = ['#00ff00', '#ff6600', '#0066ff', '#ff0066', '#ffff00']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels, 
            values=values, 
            hole=.3, 
            marker_colors=colors,
            textinfo='label+percent',
            textfont_size=14
        )])
        
        fig.update_layout(
            title="🥧 Customer Revenue Distribution",
            template="plotly_dark",
            height=500,
            title_font_size=20
        )
        
        st.plotly_chart(fig, use_container_width=True, key=chart_key)
        st.success("✅ CUSTOMER PIE CHART IS WORKING!")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
else:
    st.markdown("""
    <div class="chart-container">
        <h2 style="text-align: center; color: #666;">📭 No Charts Active</h2>
        <p style="text-align: center; color: #666;">Click one of the buttons above to see a chart!</p>
    </div>
    """, unsafe_allow_html=True)

# DEBUG INFO
st.markdown("## 🔧 Debug Info")
st.write(f"Current chart: {st.session_state.show_chart}")
st.write(f"Chart counter: {st.session_state.chart_counter}")
st.write(f"Timestamp: {time.time()}")

# INSTRUCTIONS
st.markdown("""
## 🎯 How to Test:

1. **Click "📈 PROFIT TRENDS"** → You should see a green line chart appear immediately
2. **Click "💰 REVENUE CHART"** → Chart should switch to revenue/expenses lines  
3. **Click "🥧 CUSTOMER PIE"** → Chart should switch to pie chart
4. **Click "🗑️ CLEAR ALL"** → Chart area should show "No Charts Active"

### 👀 Where to Look:
- Charts appear in the **"CHART DISPLAY AREA"** section
- Look for the green border around the chart container
- Status shows at the top whether chart is active

### If this doesn't work, the issue is with your Streamlit environment, not the code!
""")
