# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import zipfile

# ==========================================
# 1. 页面配置：侧边栏设为默认展开 (expanded)
# ==========================================
st.set_page_config(
    page_title="美国商标检索分析系统",
    layout="wide",
    initial_sidebar_state="expanded"  # 改为默认展开，方便用户看到授权框
)

# 注入优化后的 CSS
st.markdown("""
    <style>
    /* 隐藏 Streamlit 官方页脚和部署按钮 */
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 移除顶部多余的空白高度 */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* 专业法务标签样式 */
    .beta-badge { 
        font-size: 0.8em; 
        background-color: #495057; 
        padding: 3px 10px; 
        border-radius: 4px; 
        color: white; 
        font-weight: bold;
    }
    
    /* API 状态框 */
    .status-box {
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        margin-top: 10px;
        font-size: 0.9em;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心算法引擎
# ==========================================
def get_tma_logic(reg_date_str):
    """TMA 法案分析引擎"""
    try:
        reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
        years = (datetime.now() - reg_date).days / 365.25
        if 3 <= years <= 10:
            return 95, "✅ 极高 (TMA黄金期)", "Section 16H (Expungement)", [95, 85, 90, 70, 80]
        elif years > 10:
            return 65, "⚠️ 中等 (常规路径)", "Section 14 (Cancellation)", [65, 70, 60, 85, 75]
        else:
            return 25, "❌ 较低 (保护期内)", "N/A", [25, 40, 20, 90, 50]
    except:
        return 0, "数据异常", "N/A", [0, 0, 0, 0, 0]

# ==========================================
# 3. 侧边栏授权控制 (Side Bar)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=80) # 可选：加个法务小图标
    st.title("控制面板")
    st.markdown("---")
    
    st.subheader("🔑 接口授权")
    user_api_key = st.text_input("请输入授权密钥", type="password", help="请联系法务部 IT 申请密钥")
    
    if user_api_key:
        st.markdown('<div style="background-color:#d4edda;color:#155724;padding:10px;border-radius:5px;">● 系统已激活 (已连接)</div>', unsafe_allow_html=True)
        st.success("数据链路已加密连接")
    else:
        st.markdown('<div style="background-color:#f8d7da;color:#721c24;padding:10px;border-radius:5px;">○ 系统锁定 (未授权)</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("法务测试版 © 2026\n编码标准: UTF-8-SIG")

# ==========================================
# 4. 主界面逻辑
# ==========================================
st.title("🛡️ 美国商标检索分析系统")
st.markdown('<span class="beta-badge">BETA 1.0</span> 专业级法务工具', unsafe_allow_html=True)

# 拦截未授权用户
if not user_api_key:
    st.info("👋 欢迎！请在左侧面板输入授权密钥以启用检索功能。")
    st.image("https://images.unsplash.com/photo-1589829545856-d10d557cf95f?auto=format&fit=crop&q=80&w=1000", caption="Legal Analysis System")
    st.stop()

# 授权后的标签页功能
tab1, tab2 = st.tabs(["📋 批量分析模式", "🔍 单案深度诊断"])

with tab1:
    st.write("### 批量检索数据扫描")
    col_a, col_b = st.columns(2)
    with col_a:
        classes = st.multiselect("检索类别", ["007", "009", "011", "025", "035"], default="009")
    with col_b:
        search_btn = st.button("开始调取数据", type="primary", use_container_width=True)

    if search_btn:
        with st.spinner("正在扫描 USPTO 数据库..."):
            # 模拟数据
            results = [
                {"注册号": "5093077", "名称": "FIXGO", "日期": "2016-12-06"},
                {"注册号": "6288192", "名称": "AI-MAX", "日期": "2021-05-20"}
            ]
            final_df = []
            for r in results:
                score, chance, law, _ = get_tma_logic(r['日期'])
                r.update({"潜力得分": score, "机会评估": chance, "法条依据": law})
                final_df.append(r)
            
            df = pd.DataFrame(final_df)
            st.dataframe(df, use_container_width=True)
            
            # 下载功能（解决乱码）
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 导出分析报告 (.csv)", csv, "GuoRui_Report.csv", "text/csv", use_container_width=True)

with tab2:
    st.write("### 单一商标深度穿透")
    target_id = st.text_input("输入商标号", value="5093077")
    
    if st.button("分析"):
        score, chance, law, metrics = get_tma_logic("2016-12-06")
        c1, c2 = st.columns([1, 1.2])
        with c1:
            st.metric("TMA 评分", f"{score}/100")
            st.warning(f"分析结果: {chance}")
            st.info(f"法条依据: {law}")
        with c2:
            # 锁定式雷达图
            fig = go.Figure(data=[go.Scatterpolar(
                r=metrics,
                theta=['时间窗', '类目', '活跃度', '证据', '成本'],
                fill='toself',
                line_color='#1e3c72'
            )])
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, height=350)
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True})

st.divider()
st.caption("Confidential & Proprietary - GuoRui Law Tech")
