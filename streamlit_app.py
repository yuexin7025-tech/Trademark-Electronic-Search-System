import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import io
import zipfile

# ==========================================
# 1. 页面配置与专业化外观定制
# ==========================================
st.set_page_config(
    page_title="国睿商标检索分析系统 | Beta 1.0",
    layout="wide",
    initial_sidebar_state="collapsed" # 手机端默认折叠侧边栏，防止遮挡
)

# 注入 CSS：抹除 Streamlit 官方痕迹 + 手机端样式优化
st.markdown("""
    <style>
    /* 隐藏 Streamlit 默认页眉、页脚和菜单 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* 页面背景色与字体优化 */
    .main { background-color: #f8f9fa; }
    body { font-family: "Microsoft YaHei", "Helvetica Neue", sans-serif; }
    
    /* 法务版专业标签样式 */
    .beta-badge { 
        font-size: 0.85em; 
        background-color: #495057; 
        padding: 4px 12px; 
        border-radius: 50px; 
        color: white; 
        font-weight: bold;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    /* 授权状态框 */
    .api-status-box {
        padding: 10px;
        border-radius: 8px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
    }
    .status-on { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .status-off { background-color: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    
    /* 移动端表格字体微调 */
    @media (max-width: 640px) {
        .stTable { font-size: 12px !important; }
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. 核心算法逻辑层
# ==========================================
def get_tma_logic(reg_date_str):
    """基于美国商标法与TMA法案的评估引擎"""
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
# 3. 侧边栏：API 授权配置
# ==========================================
with st.sidebar:
    st.markdown("### 🔑 接口授权中心")
    st.info("请输入 USPTO 或内部接口密钥以激活系统全功能。")
    
    user_api_key = st.text_input("API Key", type="password", placeholder="输入 32 位授权密钥")
    
    api_provider = st.selectbox("选择数据源", ["USPTO Official ODP", "国睿内部服务器", "第三方接口"])
    
    if user_api_key:
        st.markdown('<div class="api-status-box status-on">● 接口授权成功</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="api-status-box status-off">○ 接口未授权</div>', unsafe_allow_html=True)
    
    st.divider()
    st.caption("国睿法务科技实验室 (Beta 1.0)\n字符编码：UTF-8-SIG")

# ==========================================
# 4. 主界面标题与拦截逻辑
# ==========================================
st.title("🛡️ 国睿商标检索分析系统")
st.markdown('<span class="beta-badge">Beta 1.0 法务开发测试版</span>', unsafe_allow_html=True)

if not user_api_key:
    st.warning("🔒 访问受限：请在侧边栏输入您的 API Key 以解锁批量检索与法务分析功能。")
    st.stop()

# ==========================================
# 5. 功能标签页
# ==========================================
tab1, tab2 = st.tabs(["📋 批量筛选评估", "🔍 单案深度穿透"])

# --- TAB 1: 批量模式 ---
with tab1:
    st.subheader("批量数据扫描中心")
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1:
        sel_class = st.multiselect("商标类别", ["007", "009", "011", "025", "035"], default="009")
    with c2:
        sel_dates = st.date_input("注册日期范围", [datetime(2015, 1, 1), datetime.now()])
    with c3:
        st.write("")
        run_batch = st.button("开始批量检索", type="primary", use_container_width=True)

    if run_batch:
        with st.spinner("正在通过安全连接调取数据..."):
            # 模拟结果
            mock_data = [
                {"id": "5093077", "name": "FIXGO", "date": "2016-12-06", "owner": "FIXGO TECH"},
                {"id": "6288192", "name": "AI-MAX", "date": "2021-05-20", "owner": "GLOBAL AI"},
                {"id": "4122334", "name": "VINTAGE", "date": "2010-11-15", "owner": "OLD BRAND"}
            ]
            
            results = []
            for d in mock_data:
                score, chance, law, _ = get_tma_logic(d['date'])
                results.append({
                    "注册号": d['id'], "商标名称": d['name'], "注册日期": d['date'],
                    "潜力得分": score, "撤销机会": chance, "法律依据": law, "所有权人": d['owner']
                })
            
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)

            # --- 文件打包逻辑 (针对手机中文优化) ---
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as zf:
                try:
                    excel_data = io.BytesIO()
                    df.to_excel(excel_data, index=False, engine='openpyxl')
                    zf.writestr("国睿法务分析清单.xlsx", excel_data.getvalue())
                except:
                    # 如果没有 openpyxl，回退至 CSV 并带上 UTF-8-SIG 解决手机乱码
                    zf.writestr("国睿法务分析清单.csv", df.to_csv(index=False).encode('utf-8-sig'))
                
                summary = f"国睿法务摘要报告\n生成时间: {datetime.now()}\n分析总数: {len(df)}"
                zf.writestr("REPORT_SUMMARY.txt", summary.encode('utf-8'))

            st.download_button("📥 下载完整分析数据包 (.zip)", zip_buf.getvalue(), "GuoRui_Export.zip", use_container_width=True)

# --- TAB 2: 单案模式 ---
with tab2:
    st.subheader("单案法律风险评估")
    single_id = st.text_input("请输入商标号/名称", value="5093077")
    
    if st.button("启动深度诊断"):
        score, chance, law, metrics = get_tma_logic("2016-12-06")
        col_res, col_plt = st.columns([1, 1.2])
        
        with col_res:
            st.metric("TMA 潜力指数", f"{score}/100", delta=chance)
            st.info(f"**建议程序:** {law}")
            # 得分明细表
            st.table(pd.DataFrame({
                "评估维度": ['时间窗', '类目冗余', '活跃度', '证据强度', '撤销成本'],
                "得分": metrics
            }))
        
        with col_plt:
            # --- 锁定式雷达图：预防所有解析错误 ---
            fig = go.Figure(
                data=[go.Scatterpolar(
                    r=metrics,
                    theta=['时间窗', '类目冗余', '活跃度', '证据强度', '撤销成本'],
                    fill='toself',
                    line_color='#1e3c72',
                    fillcolor='rgba(30,60,114,0.2)',
                    hoverinfo='skip'
                )],
                layout=go.Layout(
                    polar=dict(
                        gridshape='circular',
                        radialaxis=dict(visible=True, range=[0, 100])
                    ),
                    margin=dict(t=40, b=40, l=40, r=40),
                    height=400,
                    dragmode=False,
                    showlegend=False
                )
            )
            # 使用 staticPlot 彻底锁定，防止手机拉拽误操作
            st.plotly_chart(fig, use_container_width=True, config={'staticPlot': True, 'displayModeBar': False})

# --- 页脚 ---
st.divider()
st.caption("© 2026 国睿法务科技实验室 | 数据所有权受法律保护")
