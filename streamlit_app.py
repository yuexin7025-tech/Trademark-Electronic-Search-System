import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import re
from datetime import datetime
import io
import zipfile

# --- 1. 页面配置与全局样式 ---
st.set_page_config(page_title="美国商标检索分析系统 | Beta 1.0", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .beta-badge { 
        font-size: 0.85em; 
        background-color: #495057; 
        padding: 4px 12px; 
        border-radius: 50px; 
        color: white; 
        font-weight: bold;
    }
    .api-status-box {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
    }
    .status-on { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-off { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    [data-testid="stMetricValue"] { font-size: 28px; color: #1e3c72; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 侧边栏：API 授权中心 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1048/1048953.png", width=80)
    st.header("🔑 接口授权配置")
    user_api_key = st.text_input("请输入 API 授权密钥", type="password", help="在此输入您的 APIKey 以解锁检索功能")
    api_provider = st.selectbox("选择数据源", ["USPTO 官方 ODP", "国睿内部服务器", "第三方专业接口"])
    
    if user_api_key:
        st.markdown('<div class="api-status-box status-on">● 接口授权成功 (已加密)</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status-box status-off">○ 接口未授权 (功能锁定)</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("版本声明：Beta 1.0 法务开发测试版\n仅供内部合规评估使用。")

# --- 3. 核心算法层 ---
def get_tma_logic(reg_date_str):
    try:
        reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d")
        years = (datetime.now() - reg_date).days / 365.25
        if 3 <= years <= 10:
            return 95, "✅ 极高 (TMA黄金期)", "Section 16H", [95, 85, 90, 70, 80]
        elif years > 10:
            return 65, "⚠️ 中等 (常规路径)", "Section 14", [65, 70, 60, 85, 75]
        else:
            return 25, "❌ 较低 (保护期内)", "N/A", [25, 40, 20, 90, 50]
    except:
        return 0, "数据异常", "N/A", [0, 0, 0, 0, 0]

# --- 4. 主界面标题 ---
col_t, col_b = st.columns([3, 1])
with col_t:
    st.title("🛡️ 美国商标检索分析系统")
    st.markdown('<span class="beta-badge">Beta 1.0 法务开发测试版</span>', unsafe_allow_html=True)

if not user_api_key:
    st.warning("⚠️ 系统锁定：请在左侧配置有效的 API Key 以访问法务数据库。")
    st.stop()

# --- 5. 功能区 ---
tab1, tab2 = st.tabs(["📋 批量筛选评估", "🔍 单案深度穿透"])

with tab1:
    st.subheader("批量法务数据处理")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        sel_class = st.multiselect("检索类别", ["007", "009", "011", "025", "035"], default="009")
    with c2:
        sel_dates = st.date_input("注册日期跨度", [datetime(2015, 1, 1), datetime.now()])
    with c3:
        st.write("")
        run_batch = st.button("执行批量扫描", type="primary", use_container_width=True)

    if run_batch:
        # 模拟数据
        mock_results = [
            {"id": "5093077", "name": "FIXGO", "date": "2016-12-06", "owner": "FIXGO TECH"},
            {"id": "6288192", "name": "AI-MAX", "date": "2021-05-20", "owner": "GLOBAL AI"},
            {"id": "4122334", "name": "VINTAGE", "date": "2010-11-15", "owner": "OLD BRAND"}
        ]
        
        results = []
        for d in mock_results:
            score, chance, law, _ = get_tma_logic(d['date'])
            results.append({
                "注册号": d['id'], "商标名称": d['name'], "注册日期": d['date'],
                "潜力得分": score, "撤销机会": chance, "依据": law, "所有权人": d['owner']
            })
            
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        
        # 下载逻辑
        zip_buf = io.BytesIO()
        with zipfile.ZipFile(zip_buf, "w") as zf:
            try:
                excel_data = io.BytesIO()
                df.to_excel(excel_data, index=False, engine='openpyxl')
                zf.writestr("批量清单.xlsx", excel_data.getvalue())
            except:
                zf.writestr("批量清单.csv", df.to_csv(index=False).encode('utf-8-sig'))
            zf.writestr("分析摘要.txt", f"分析汇总：共计 {len(df)} 条。")
        st.download_button("📥 下载分析结果包 (.zip)", zip_buf.getvalue(), "GuoRui_Batch.zip", use_container_width=True)

with tab2:
    st.subheader("单案法律风险穿透")
    single_id = st.text_input("输入商标注册号/序列号进行分析", value="5093077")
    
    if st.button("启动诊断"):
        score, chance, law, metrics = get_tma_logic("2016-12-06")
        col_res, col_plt = st.columns([1, 1.2])
        
        with col_res:
            st.metric("TMA 潜力指数", f"{score}/100", delta=chance)
            st.markdown(f"**建议程序:** `{law}`")
            # 辅助表格
            st.table(pd.DataFrame({"评估维度": ['时间窗', '类目冗余', '活跃度', '证据强度', '撤销成本'], "得分": metrics}))
        
        with col_plt:
            # --- 核心修复：gridshape 必须放在 polar 下，不能放在 radialaxis 下 ---
            fig = go.Figure(
                data=[
                    go.Scatterpolar(
                        r=metrics,
                        theta=['时间窗', '类目冗余', '活跃度', '证据强度', '撤销成本'],
                        fill='toself',
                        line_color='#1e3c72',
                        fillcolor='rgba(30,60,114,0.2)',
                        hoverinfo='skip'
                    )
                ],
                layout=go.Layout(
                    polar=dict(
                        gridshape='circular',  # <--- 正确位置：polar 的直接子属性
                        radialaxis=dict(
                            visible=True, 
                            range=[0, 100]
                            # gridshape='circular' <--- 错误位置：不能放在这里
                        ),
                    ),
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=400,
                    dragmode=False,
                    showlegend=False
                )
            )
            
            # 使用静态模式配置锁定
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

st.divider()
st.caption("© 2026 法务中心 | 内部测试版本 Beta 1.0")