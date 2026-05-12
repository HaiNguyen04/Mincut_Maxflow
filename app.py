import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
import os

# ==========================================
# 1. CẤU HÌNH GIAO DIỆN STREAMLIT
# ==========================================
st.set_page_config(page_title="Ứng dụng giải bài toán MinCut-MaxFlow", layout="wide")

st.markdown("""
<style>
    /* CỐ ĐỊNH LIGHT MODE - Ghi đè biến hệ thống Streamlit */
    :root {
        color-scheme: light !important;
    }
    
    [data-theme="dark"] {
        --st-color-background: #F8FAFC !important;
        --st-color-text: #1E293B !important;
        --st-color-secondary-background: #F1F5F9 !important;
    }

    /* Nền tổng thể của App */
    .stApp { 
        background: linear-gradient(135deg, #F8FAFC 0%, #E2E8F0 100%) !important; 
        font-family: 'Inter', sans-serif; 
        color: #1E293B !important;
    }
    
    /* Ép màu chữ cho toàn bộ các phần tử văn bản */
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp span, .stApp label {
        color: #1E293B !important;
    }

    /* Container chính dạng Card 3D */
    .block-container {
        max-width: 1400px !important;
        margin: 2rem auto !important;
        background-color: rgba(255, 255, 255, 0.85) !important;
        backdrop-filter: blur(12px);
        padding: 2.5rem !important;
        border-radius: 24px;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.05);
        border: 1px solid rgba(255,255,255,0.6);
    }
    
    /* Text Gradient cho Tiêu đề */
    h1 { 
        text-align: center; margin-bottom: 0.2rem; font-size: 2.5rem; font-weight: 800;
        background: -webkit-linear-gradient(45deg, #1E293B, #3B82F6);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .subtitle { text-align: center; color: #64748B !important; margin-bottom: 1.5rem; font-size: 1.1rem; font-weight: 500;}
    
    /* Tùy chỉnh Radio buttons */
    .stRadio > div { 
        flex-direction: row; justify-content: center; gap: 30px; 
        background: #F1F5F9 !important; padding: 10px; border-radius: 50px; 
        display: inline-flex; margin: 0 auto; 
    }
    
    /* Kết quả dạng Card Custom */
    .result-card { background: white !important; padding: 20px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); border-left: 5px solid; height: 100%; }
    .card-maxflow { border-color: #3B82F6; }
    .card-phi { border-color: #10B981; }
    .card-psi { border-color: #EF4444; }
    .res-title { font-size: 14px; color: #64748B !important; text-transform: uppercase; font-weight: 700; margin-bottom: 8px;}
    .res-value { font-size: 24px; color: #1E293B !important; font-weight: 800; }
    
    @media (max-width: 768px) {
        .block-container { padding: 1rem !important; margin: 0 !important; border-radius: 0; box-shadow: none; }
        h1 { font-size: 1.8rem; }
    }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>Ứng dụng giải bài toán MinCut-MaxFlow</h1>", unsafe_allow_html=True)

# UI Chọn chế độ Đồ thị
col_mode1, col_mode2, col_mode3 = st.columns([1, 1, 1])
with col_mode2:
    graph_mode = st.radio(
        "Chế độ mô phỏng:",
        ["Có hướng", "Vô hướng"],
        horizontal=True,
        label_visibility="collapsed"
    )

st.markdown("<div class='subtitle'>Một bài tập lớn môn Kỹ thuật ra quyết định về phần mềm giải bài toán MaxFlow – MinCut trực quan giúp người dùng tạo, chỉnh sửa và phân tích đồ thị mạng luồng một cách dễ dàng. Ứng dụng hỗ trợ đồ thị có hướng/vô hướng, tính toán tự động Max Flow – Min Cut và hiển thị kết quả trực quan theo thời gian thực. </div>", unsafe_allow_html=True)

# ==========================================
# 2. FRONTEND GRAPH EDITOR (JS & CSS NÂNG CAO)
# ==========================================
HTML_EDITOR_CODE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; margin: 0; padding: 0; overflow: hidden; background: transparent; touch-action: none; }
        
        /* Canvas nền Blueprint chấm bi */
        #editor-wrapper { 
            position: relative; width: 100%; height: 650px; 
            background-color: #F8FAFC;
            background-image: radial-gradient(#CBD5E1 1px, transparent 1px);
            background-size: 24px 24px;
            border-radius: 20px; 
            border: 2px solid #E2E8F0;
            overflow: hidden; 
            box-shadow: inset 0 0 30px rgba(0,0,0,0.02);
        }
        #cy { position: absolute; top: 0; left: 0; right: 0; bottom: 0; outline: none; }
        
        /* --- NÚT BẤM DẠNG PILL --- */
        .btn { 
            padding: 10px 20px; border: none; border-radius: 50px; font-weight: 700; 
            cursor: pointer; font-size: 14px; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex; align-items: center; gap: 8px;
        }
        .btn:hover { transform: translateY(-2px) scale(1.02); }
        .btn:active { transform: translateY(0) scale(0.98); }
        
        .btn-solve { background: linear-gradient(135deg, #3B82F6, #2563EB); color: white; box-shadow: 0 8px 20px rgba(59, 130, 246, 0.3); }
        .btn-solve:hover { box-shadow: 0 12px 25px rgba(59, 130, 246, 0.4); }
        
        .btn-clear { background: white; color: #EF4444; border: 2px solid #FECACA; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .btn-clear:hover { background: #FEF2F2; border-color: #FCA5A5; }

        .btn-undo { background: white; color: #475569; border: 2px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
        .btn-undo:hover { background: #F1F5F9; border-color: #CBD5E1; color: #1E293B; }

        /* --- NÚT MODAL OK --- */
        .btn-modal-ok { width:100%; padding:14px; border:none; border-radius:12px; background:#3B82F6; color:white; cursor:pointer; font-weight:700; font-size:16px; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); transition:0.2s; }
        .btn-modal-ok:hover { background:#2563EB; box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6); transform: translateY(-2px); }
        .modal-show { transform:scale(1) !important; opacity:1 !important; }

        /* --- TOOLBARS --- */
        #toolbar { position: absolute; top: 20px; left: 20px; z-index: 10; display: flex; gap: 12px; align-items: center; }
        .toolbar-divider { width: 2px; height: 24px; background: #E2E8F0; margin: 0 5px; border-radius: 2px; }
        
        /* --- SIDEBAR PANEL (FIXED RIGHT) --- */
        #status-panel { 
            position: absolute; top: 20px; right: 20px; z-index: 10; 
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(12px); 
            border-radius: 20px; padding: 25px 20px; border: 1px solid #E2E8F0; 
            display: flex; flex-direction: column; gap: 18px; align-items: stretch;
            box-shadow: -10px 10px 30px rgba(0,0,0,0.05);
            width: 220px; max-height: 600px; overflow-y: auto;
        }
        .status-item { display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #1E293B; font-weight: 700; }
        .metric-label { color: #64748B; font-weight: 500; }
        .status-badge { width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 5px; }
        .bg-source { background: #10B981; box-shadow: 0 0 10px #10B981; }
        .bg-sink { background: #EF4444; box-shadow: 0 0 10px #EF4444; }

        /* Vùng kết quả phụ trong side panel */
        #side-result-box { margin-top: 10px; padding-top: 15px; border-top: 1px solid #eee; display: none; }
        .side-res-val { font-size: 20px; color: #3B82F6; font-weight: 800; text-align: center; }

        #viewport-controls { position: absolute; bottom: 20px; left: 20px; z-index: 10; display: flex; background: white; border-radius: 50px; box-shadow: 0 8px 25px rgba(0,0,0,0.1); border: 1px solid #E2E8F0; padding: 4px; gap: 2px;}
        .vp-btn { width: 40px; height: 40px; border-radius: 50%; border: none; background: transparent; cursor: pointer; font-size: 18px; color: #475569; font-weight: bold; transition: 0.2s; display: flex; justify-content: center; align-items: center;}
        .vp-btn:hover { background: #F1F5F9; color: #1E293B; }

        /* --- TOAST & PANELS --- */
        #help-panel {
            position: absolute; top: 80px; left: 20px; z-index: 1000; width: 320px; 
            background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(15px);
            border-radius: 20px; padding: 24px; box-shadow: 0 20px 50px rgba(0,0,0,0.15); border: 1px solid rgba(255,255,255,0.8);
            display: none; opacity: 0; transform: translateX(-20px); transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); pointer-events: none;
        }
        #help-panel.show { display: block; opacity: 1; transform: translateX(0); pointer-events: auto; }
        #help-panel h3 { margin: 0 0 15px 0; font-size: 16px; color: #0F172A; display: flex; align-items: center; gap: 8px; border-bottom: 2px solid #F1F5F9; padding-bottom: 10px;}
        #help-panel ul { list-style: none; padding: 0; margin: 0; }
        #help-panel li { margin-bottom: 15px; font-size: 13px; color: #475569; display: flex; align-items: center; gap: 12px; font-weight: 500;}
        .help-icon { background: #F8FAFC; color: #3B82F6; padding: 6px; border-radius: 8px; font-size: 16px; font-weight: 800; border: 1px solid #E2E8F0; width: 32px; height: 32px; display: flex; justify-content: center; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
        .btn-got-it { width: 100%; background: #F1F5F9; color: #334155; border: none; padding: 12px; border-radius: 12px; font-weight: 700; cursor: pointer; margin-top: 10px; transition: 0.2s; }
        .btn-got-it:hover { background: #E2E8F0; color: #0F172A; }

        #toast-container { position: absolute; bottom: 20px; right: 250px; z-index: 9999; display: flex; flex-direction: column-reverse; gap: 10px; pointer-events: none; max-width: 320px; }
        .toast { padding: 14px 20px; border-radius: 14px; font-size: 14px; font-weight: 600; box-shadow: 0 15px 35px rgba(0,0,0,0.1); display: flex; align-items: flex-start; gap: 12px; opacity: 0; transform: translateY(20px); transition: 0.4s cubic-bezier(0.4, 0, 0.2, 1); pointer-events: auto; background: white; border-left: 6px solid #64748B;}
        .toast.show { opacity: 1; transform: translateY(0); }
        .toast.warning { border-left-color: #F59E0B; background: #FFFBEB; color: #92400E; }
        .toast.error   { border-left-color: #EF4444; background: #FEF2F2; color: #991B1B; }
        .toast.success { border-left-color: #10B981; background: #ECFDF5; color: #065F46; }

        /* --- NODE TOOLBAR (FLOATING ACTIONS) --- */
        #node-toolbar { position: absolute; display: none; z-index: 25; background: rgba(255,255,255,0.95); backdrop-filter: blur(8px); border-radius: 50px; box-shadow: 0 15px 40px rgba(0,0,0,0.15); border: 1px solid #E2E8F0; padding: 6px; gap: 6px; transform: translate(-50%, -100%); margin-top: -20px; transition: top 0.1s, left 0.1s;}
        .nt-btn { width: 44px; height: 44px; border: none; background: white; border-radius: 50%; cursor: pointer; font-size: 18px; display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 10px rgba(0,0,0,0.05); transition: 0.2s;}
        .nt-btn:hover { transform: scale(1.1); box-shadow: 0 8px 15px rgba(0,0,0,0.1); }
        
        .nt-btn-del { color: #EF4444; background: #FEF2F2; }
        .nt-btn-del:hover { background: #DC2626 !important; color: white !important; }

        /* --- INLINE EDITORS --- */
        .inline-container { position: absolute; display: none; z-index: 100; transform: translate(-50%, -50%); }
        .editor-box { display: flex; align-items: center; gap: 8px; background: white; padding: 6px; border-radius: 50px; box-shadow: 0 10px 30px rgba(59, 130, 246, 0.3); border: 2px solid #3B82F6; animation: popIn 0.2s ease;}
        @keyframes popIn { 0% { transform: scale(0.8); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
        .inline-input { text-align: center; background: transparent; border: none; font-weight: 800; font-size: 16px; outline: none; color: #1E293B; width: 45px;}
        
        /* Spin buttons (+/-) */
        .spin-btn { width: 36px; height: 36px; border-radius: 50%; border: none; background: #F1F5F9; color: #1E293B; font-weight: 800; font-size: 20px; cursor: pointer; display: flex; justify-content: center; align-items: center; transition: 0.2s; padding: 0; margin: 0;}
        .spin-btn:active { background: #3B82F6; color: white; }

        .btn-edge-del { background: #FEF2F2; color: #EF4444; border: none; width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; font-size: 16px; transition: 0.2s;}
        .btn-edge-del:hover { background: #DC2626; color: white; }

        @media (max-width: 768px) {
            #toolbar { bottom: 20px; top: auto; left: 50%; transform: translateX(-50%); width: 95%; background: white; border-radius: 20px; padding: 10px; justify-content: center; flex-wrap: wrap;}
            .toolbar-divider { display: none; }
            #status-panel { display: none; } /* Mobile ẩn sidebar để tránh chật */
            #help-panel { width: calc(100% - 40px); left: 20px; top: 120px;}
            #viewport-controls { bottom: 90px; right: 10px; left: auto; flex-direction: column; border-radius: 20px;}
        }
    </style>
</head>
<body>
    <div id="editor-wrapper">
        <div id="cy"></div>
        <div id="toast-container"></div>
        
        <div id="toolbar">
            <button class="btn btn-solve" onclick="sendToPython()">🚀 Giải bài toán</button>
            <button class="btn btn-clear" onclick="toggleHelp()" style="background:white; color:#3B82F6; border: 2px solid #BFDBFE;">💡 Hướng dẫn</button>
            <button class="btn btn-clear" onclick="showConfirm()">🔄 Xóa đồ thị</button>
            <div class="toolbar-divider"></div>
            <button class="btn btn-undo" onclick="undo()" title="Hoàn tác (Ctrl+Z)">↶ Undo</button>
            <button class="btn btn-undo" onclick="redo()" title="Làm lại (Ctrl+Y)">↷ Redo</button>
        </div>

        <!-- Help Panel -->
        <div id="help-panel">
            <h3>📘 Hướng dẫn sử dụng</h3>
            <ul>
                <li><span class="help-icon">➕</span> Kéo nhánh mới từ Node</li>
                <li><span class="help-icon">⇄</span> Nối 2 Node có sẵn</li>
                <li><span class="help-icon">✏️</span> Bấm vào số trên Cạnh để sửa</li>
                <li><span class="help-icon">🟢</span> Đặt làm Nguồn (Source)</li>
                <li><span class="help-icon">🔴</span> Đặt làm Đích (Sink)</li>
                <li><span class="help-icon">❌</span> Xóa Node hoặc Cạnh</li>
            </ul>
            <button class="btn-got-it" onclick="toggleHelp()">Tuyệt vời, tôi đã hiểu!</button>
        </div>

        <!-- Status Panel - MOVED TO RIGHT -->
        <div id="status-panel">
            <div style="font-size: 11px; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px;">Thống kê</div>
            <div class="status-item"><span class="metric-label">Nodes:</span> <span id="count-nodes" style="color:#3B82F6">1</span></div>
            <div class="status-item"><span class="metric-label">Edges:</span> <span id="count-edges" style="color:#8B5CF6">0 / 0</span></div>
            
            <div style="font-size: 11px; font-weight: 800; color: #94A3B8; text-transform: uppercase; margin-bottom: 5px; margin-top: 10px;">Cấu hình</div>
            <div class="status-item">
                <span class="metric-label"><span class="status-badge bg-source"></span>Source</span>
                <span id="txt-source" style="color: #10B981">--</span>
            </div>
            <div class="status-item">
                <span class="metric-label"><span class="status-badge bg-sink"></span>Sink</span>
                <span id="txt-sink" style="color: #EF4444">--</span>
            </div>

            <div id="side-result-box">
                <div style="font-size: 11px; font-weight: 800; color: #3B82F6; text-transform: uppercase; margin-bottom: 5px;">Kết quả Flow</div>
                <div class="side-res-val" id="res-val-side">0</div>
            </div>
        </div>
        
        <!-- POPUP MODAL HỆ THỐNG -->
        <div id="result-modal-overlay" style="position:absolute; top:0; left:0; right:0; bottom:0; background:rgba(15,23,42,0.4); backdrop-filter:blur(8px); z-index:9000; display:none; align-items:center; justify-content:center;">
            <div id="result-modal" style="background:white; border-radius:24px; padding:30px; width:340px; text-align:center; box-shadow:0 30px 60px rgba(0,0,0,0.3); transform:scale(0.9); opacity:0; transition:all 0.3s cubic-bezier(0.4, 0, 0.2, 1);">
                <div id="modal-icon" style="font-size:40px; margin-bottom:10px;"></div>
                <h3 id="modal-title" style="margin:0 0 15px 0; font-size:20px; font-weight:800; color:#0F172A;"></h3>
                <div id="modal-body" style="color:#475569; font-size:15px; line-height:1.6; margin-bottom: 25px; text-align:left; background: #F8FAFC; padding: 15px; border-radius: 12px; border: 1px solid #E2E8F0;"></div>
                <button class="btn-modal-ok" onclick="closeResultModal()">OK!</button>
            </div>
        </div>

        <div id="confirm-overlay" style="position:absolute; top:0; left:0; right:0; bottom:0; background:rgba(15,23,42,0.4); backdrop-filter:blur(4px); z-index:90; display:none"></div>
        <div id="confirm-modal" style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); background:white; border-radius:24px; padding:30px; width:340px; z-index:100; display:none; text-align:center; box-shadow:0 30px 60px rgba(0,0,0,0.3);">
            <div style="font-size:40px; margin-bottom:10px;">⚠️</div>
            <h3 style="margin:0 0 10px 0; font-size:20px; font-weight:800; color:#0F172A;">Làm mới đồ thị?</h3>
            <p style="color:#475569; font-size:14px; line-height:1.5;">Mọi dữ liệu vẽ sẽ bị xóa. Hệ thống sẽ khôi phục về trạng thái Node khởi tạo.</p>
            <div style="display:flex; gap:12px; margin-top:25px">
                <button onclick="hideConfirm()" style="flex:1; padding:12px; border:none; border-radius:12px; background:#F1F5F9; color:#475569; cursor:pointer; font-weight:700">Hủy bỏ</button>
                <button onclick="executeReset()" style="flex:1; padding:12px; border:none; border-radius:12px; background:#EF4444; color:white; cursor:pointer; font-weight:700; box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4);">Đồng ý Xóa</button>
            </div>
        </div>

        <div id="node-toolbar">
            <button class="nt-btn" onclick="addBranch()" title="Phân nhánh mới">➕</button>
            <button class="nt-btn" onclick="startLinkMode()" title="Nối dây">⇄</button>
            <button class="nt-btn" onclick="openNodeEditor()" title="Sửa tên">✏️</button>
            <button class="nt-btn" onclick="setRole('source')" title="Nguồn">🟢</button>
            <button class="nt-btn" onclick="setRole('sink')" title="Đích">🔴</button>
            <button class="nt-btn nt-btn-del" onclick="deleteNode()" title="Xóa Node">❌</button>
        </div>

        <div class="inline-container" id="edge-input-container">
            <div class="editor-box">
                <button class="spin-btn" onclick="stepValue(-1)">−</button>
                <input type="number" class="inline-input" id="edge-input" min="1">
                <button class="spin-btn" onclick="stepValue(1)">+</button>
                <div style="width: 1px; height: 24px; background: #E2E8F0; margin: 0 2px;"></div>
                <button class="btn-edge-del" onclick="deleteEdge()" title="Xóa cạnh">❌</button>
            </div>
        </div>
        <div class="inline-container" id="node-input-container">
            <div class="editor-box">
                <input type="text" class="inline-input" id="node-input" style="width:70px">
            </div>
        </div>

        <div id="viewport-controls">
            <button class="vp-btn" onclick="cy.zoom(cy.zoom() + 0.15)">➕</button>
            <button class="vp-btn" onclick="cy.zoom(cy.zoom() - 0.15)">➖</button>
            <button class="vp-btn" onclick="handleFocusView()">◎</button>
        </div>
        <div id="link-hint" style="position:absolute; bottom:80px; left:50%; transform:translateX(-50%); background:#10B981; color:white; padding:10px 24px; border-radius:50px; font-size:14px; font-weight:600; display:none; z-index:20; box-shadow: 0 10px 30px rgba(16, 185, 129, 0.4);">
            ⇄ Hãy Click vào Node đích (hoặc nhấn ESC để hủy)
        </div>
    </div>

    <script>
        // ==========================================
        // KHỞI TẠO CYTOSCAPE
        // ==========================================
        let cy = cytoscape({
            container: document.getElementById('cy'),
            layout: { name: 'preset' },
            wheelSensitivity: 0.15,
            minZoom: 0.1, maxZoom: 2.5,
            style: [
                { selector: 'node', style: { 
                    'shape': 'ellipse', 'width': 50, 'height': 50,
                    'background-color': '#FFFFFF', 'border-width': 3, 'border-color': '#94A3B8', 
                    'label': 'data(label)', 'color': '#0F172A', 'font-weight': '800', 'font-size': '16px', 
                    'text-valign': 'center', 'text-halign': 'center', 'z-index': 20,
                    'shadow-blur': 15, 'shadow-color': '#CBD5E1', 'shadow-opacity': 0.6, 'shadow-offset-y': 5,
                    'transition-property': 'background-color, border-color, shadow-color, width, height', 'transition-duration': '0.3s'
                } },
                { selector: 'node:active', style: { 'overlay-opacity': 0 } },
                { selector: 'node[role="source"]', style: { 
                    'background-color': '#ECFDF5', 'border-color': '#10B981', 'color': '#065F46',
                    'shadow-color': '#10B981', 'shadow-opacity': 0.5, 'shadow-blur': 20
                } },
                { selector: 'node[role="sink"]', style: { 
                    'background-color': '#FEF2F2', 'border-color': '#EF4444', 'color': '#991B1B',
                    'shadow-color': '#EF4444', 'shadow-opacity': 0.5, 'shadow-blur': 20
                } },
                { selector: 'edge', style: { 
                    'width': 4, 'line-color': '#CBD5E1', 'target-arrow-color': '#CBD5E1', 'target-arrow-shape': 'triangle', 
                    'curve-style': 'bezier', 'control-point-step-size': 50, 
                    'label': 'data(capacityLabel)', 'font-size': '14px', 'font-weight': '800', 'color': '#1E293B',
                    'text-background-color': '#ffffff', 'text-background-opacity': 1, 'text-background-padding': '6px',
                    'text-background-shape': 'roundrectangle', 'text-border-width': 2, 'text-border-color': '#E2E8F0', 'text-rotation': 'autorotate',
                    'transition-property': 'line-color, target-arrow-color, width, text-border-color', 'transition-duration': '0.3s'
                } },
                { selector: 'edge.flowing', style: { 
                    'line-color': '#3B82F6', 'target-arrow-color': '#3B82F6', 'width': 6, 'text-border-color': '#3B82F6' 
                } },
                { selector: 'edge.saturated', style: { 
                    'line-color': '#EF4444', 'target-arrow-color': '#EF4444', 'width': 6, 'text-border-color': '#EF4444' 
                } },
                { selector: 'edge.mincut', style: { 
                    'line-style': 'dashed', 'line-color': '#8B5CF6', 'target-arrow-color': '#8B5CF6', 'width': 8, 'text-border-color': '#8B5CF6' 
                } },
                { selector: '.editing', style: { 'text-opacity': 0, 'text-background-opacity': 0, 'text-border-opacity': 0 } }
            ]
        });

        // ==========================================
        // HISTORY STATE LOGIC (CTRL+Z / CTRL+Y)
        // ==========================================
        let stateHistory = [];
        let historyIndex = -1;

        function saveState() {
            if (historyIndex < stateHistory.length - 1) {
                stateHistory = stateHistory.slice(0, historyIndex + 1);
            }
            stateHistory.push(cy.elements().jsons());
            historyIndex++;
        }

        function undo() {
            if (historyIndex > 0) {
                historyIndex--;
                cy.elements().remove();
                cy.add(stateHistory[historyIndex]);
                resetUIState();
            }
        }

        function redo() {
            if (historyIndex < stateHistory.length - 1) {
                historyIndex++;
                cy.elements().remove();
                cy.add(stateHistory[historyIndex]);
                resetUIState();
            }
        }

        function resetUIState() {
            editingEdge = null; editingNode = null;
            document.getElementById('edge-input-container').style.display = 'none';
            document.getElementById('node-input-container').style.display = 'none';
            nodeToolbar.style.display = 'none';
            updateStatusPanel();
            updateMetrics(window.currentGraphMode);
        }

        // Bắt sự kiện phím tắt (chặn input)
        window.addEventListener('keydown', function(e) {
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'z') {
                e.preventDefault();
                if (e.shiftKey) redo(); else undo();
            } else if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
                e.preventDefault();
                redo();
            }
        });

        // ==========================================
        // APP LOGIC
        // ==========================================
        let nodeCounter = 1;
        let selectedNode = null; let isLinking = false; let isInitialized = false;
        let editingEdge = null; let editingNode = null;
        const nodeToolbar = document.getElementById('node-toolbar');
        const helpPanel = document.getElementById('help-panel');

        function getNextNodeLabel() {
            let label = nodeCounter.toString();
            while (!cy.nodes(`[label="${label}"]`).empty()) { nodeCounter++; label = nodeCounter.toString(); }
            return label;
        }

        function toggleHelp() {
            if (!helpPanel.classList.contains('show')) {
                helpPanel.style.display = 'block';
                setTimeout(() => helpPanel.classList.add('show'), 10);
            } else {
                helpPanel.classList.remove('show');
                setTimeout(() => helpPanel.style.display = 'none', 300);
            }
        }

        function showToast(msg, type='warning') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `toast ${type}`;
            let icon = type==='success' ? '✅' : (type==='error' ? '❌' : '⚠️');
            toast.innerHTML = `<span style="font-size:18px">${icon}</span> <div>${msg}</div>`;
            container.prepend(toast);
            setTimeout(() => toast.classList.add('show'), 10);
            setTimeout(() => { if(toast.parentNode) { toast.classList.remove('show'); setTimeout(()=>toast.remove(), 400); } }, 3500);
        }

        function showResultModal(type, data) {
            const overlay = document.getElementById('result-modal-overlay');
            const modal = document.getElementById('result-modal');
            const icon = document.getElementById('modal-icon');
            const title = document.getElementById('modal-title');
            const body = document.getElementById('modal-body');
            
            if(type === 'success') {
                icon.innerHTML = '✅';
                title.innerHTML = 'ĐÃ GIẢI XONG, KẾT QUẢ:';
                title.style.color = '#10B981';
                body.innerHTML = `
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px;"><strong>Max Flow:</strong> <span style="font-weight:800; color:#3B82F6;">${data.maxflow}</span></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px;"><strong>Min Cut:</strong> <span style="font-weight:800; color:#8B5CF6;">${data.mincut}</span></div>
                    <div style="display:flex; justify-content:space-between; margin-bottom:8px; border-bottom: 1px solid #E2E8F0; padding-bottom: 4px;"><strong>Source:</strong> <span>${data.source_lbl}</span></div>
                    <div style="display:flex; justify-content:space-between;"><strong>Sink:</strong> <span>${data.sink_lbl}</span></div>
                `;
            } else {
                icon.innerHTML = '❌';
                title.innerHTML = 'LỖI THUẬT TOÁN';
                title.style.color = '#EF4444';
                body.innerHTML = `<div style="text-align:center; color:#991B1B; font-weight:600;">${data.error}</div>`;
            }
            
            overlay.style.display = 'flex';
            setTimeout(() => { modal.classList.add('modal-show'); }, 10);
        }

        function closeResultModal() {
            const overlay = document.getElementById('result-modal-overlay');
            const modal = document.getElementById('result-modal');
            modal.classList.remove('modal-show');
            setTimeout(() => { overlay.style.display = 'none'; }, 300);
        }

        function checkDuplicateEdge(sourceId, targetId, isUndirected) {
            if (!cy.edges(`[source="${sourceId}"][target="${targetId}"]`).empty()) return true;
            if (isUndirected && !cy.edges(`[source="${targetId}"][target="${sourceId}"]`).empty()) return true;
            return false;
        }

        function updateMetrics(mode) {
            const n = cy.nodes().length;
            const e = cy.edges().length;
            const maxE = (mode === "Vô hướng") ? (n * (n - 1) / 2) : (n * (n - 1));
            document.getElementById('count-nodes').innerText = n;
            document.getElementById('count-edges').innerText = e + " / " + (n < 2 ? 0 : maxE);
        }

        function findEmptyPosition(parentPos) {
            const offsets = [{x:220, y:0}, {x:220, y:120}, {x:220, y:-120}, {x:440, y:0}, {x:0, y:180}];
            for (let o of offsets) {
                let cx = parentPos.x + o.x, cy_pos = parentPos.y + o.y;
                let isOccupied = cy.nodes().some(node => Math.sqrt(Math.pow(node.position('x') - cx, 2) + Math.pow(node.position('y') - cy_pos, 2)) < 120);
                if (!isOccupied) return { x: cx, y: cy_pos };
            }
            return { x: parentPos.x + 240 + (Math.random()*60), y: parentPos.y + (Math.random()*150 - 75) };
        }

        function showConfirm() { document.getElementById('confirm-overlay').style.display = 'block'; document.getElementById('confirm-modal').style.display = 'block'; nodeToolbar.style.display='none'; }
        function hideConfirm() { document.getElementById('confirm-overlay').style.display = 'none'; document.getElementById('confirm-modal').style.display = 'none'; }
        
        function executeReset() {
            hideConfirm(); cy.elements().remove(); nodeCounter = 1;
            let n = cy.add({ group: 'nodes', data: { id: 'n1', label: '1', role: 'none' }, position: { x: 0, y: 0 } });
            cy.center(n); cy.zoom(0.85); updateStatusPanel(); 
            updateMetrics(window.currentGraphMode);
            document.getElementById('side-result-box').style.display = 'none';
            showToast("Bản vẽ đã được làm sạch", "success");
            saveState(); // LƯU LỊCH SỬ
        }

        function handleFocusView() { cy.fit(cy.elements(), 120); if(cy.zoom() > 1) cy.zoom(1); cy.center(); }
        
        function updateStatusPanel() {
            let src = 'Chưa chọn', snk = 'Chưa chọn';
            cy.nodes().forEach(n => {
                if(n.data('role') === 'source') src = n.data('label');
                if(n.data('role') === 'sink') snk = n.data('label');
            });
            document.getElementById('txt-source').innerText = src;
            document.getElementById('txt-sink').innerText = snk;
        }

        function updatePositions() {
            if(selectedNode && nodeToolbar.style.display === 'flex') {
                let pos = selectedNode.renderedPosition();
                nodeToolbar.style.left = pos.x + 'px'; nodeToolbar.style.top = (pos.y - 10) + 'px';
            }
            if(editingEdge) {
                let mid = editingEdge.renderedMidpoint();
                document.getElementById('edge-input-container').style.left = mid.x + 'px';
                document.getElementById('edge-input-container').style.top = mid.y + 'px';
            }
            if(editingNode) {
                let pos = editingNode.renderedPosition();
                document.getElementById('node-input-container').style.left = pos.x + 'px';
                document.getElementById('node-input-container').style.top = pos.y + 'px';
            }
        }

        function stepValue(step) {
            let inp = document.getElementById('edge-input');
            let v = parseInt(inp.value);
            if(isNaN(v)) v = 1;
            v += step;
            if(v < 1) v = 1;
            inp.value = v;
        }

        cy.on('tap', 'node', function(e){
            let targetId = e.target.id();
            if(isLinking) {
                if(targetId === selectedNode.id()) return;
                const isUndirected = window.currentGraphMode === "Vô hướng";
                if (checkDuplicateEdge(selectedNode.id(), targetId, isUndirected)) {
                    showToast("Kết nối này đã tồn tại trên đồ thị", "warning");
                    isLinking = false; document.getElementById('link-hint').style.display='none'; return;
                }
                let newE = cy.add({ group: 'edges', data: { id: 'e'+Date.now(), source: selectedNode.id(), target: targetId, capacity: 10, capacityLabel: '10' } });
                isLinking = false; document.getElementById('link-hint').style.display='none';
                updateMetrics(window.currentGraphMode); openEdgeEditor(newE);
                saveState(); // LƯU LỊCH SỬ
                return;
            }
            commitAll(); selectedNode = e.target; nodeToolbar.style.display = 'flex'; updatePositions();
        });

        cy.on('tap', 'edge', function(e){ commitAll(); nodeToolbar.style.display='none'; openEdgeEditor(e.target); });
        cy.on('tap', function(e){ if(e.target === cy) { commitAll(); nodeToolbar.style.display='none'; isLinking=false; document.getElementById('link-hint').style.display='none'; } });
        cy.on('pan zoom position', updatePositions);

        function openEdgeEditor(edge) {
            editingEdge = edge; edge.addClass('editing');
            let inp = document.getElementById('edge-input');
            inp.value = edge.data('capacity');
            document.getElementById('edge-input-container').style.display = 'block';
            updatePositions(); setTimeout(() => { inp.focus(); inp.select(); }, 50);
        }

        function openNodeEditor() {
            editingNode = selectedNode; editingNode.addClass('editing');
            nodeToolbar.style.display='none';
            let inp = document.getElementById('node-input');
            inp.value = editingNode.data('label');
            document.getElementById('node-input-container').style.display = 'block';
            updatePositions(); setTimeout(() => { inp.focus(); inp.select(); }, 50);
        }

        function deleteEdge() {
            if(editingEdge) {
                editingEdge.remove(); editingEdge = null;
                document.getElementById('edge-input-container').style.display = 'none';
                updateMetrics(window.currentGraphMode); showToast("Đã xóa cạnh", "success");
                saveState(); // LƯU LỊCH SỬ
            }
        }

        function deleteNode() {
            if (cy.nodes().length <= 1) { showToast("Graph phải giữ lại ít nhất 1 node", "warning"); return; }
            selectedNode.remove(); nodeToolbar.style.display = 'none'; updateStatusPanel();
            updateMetrics(window.currentGraphMode); showToast("Đã xóa node", "success");
            saveState(); // LƯU LỊCH SỬ
        }

        function commitAll() {
            let changed = false;
            if(editingEdge) {
                let v = parseInt(document.getElementById('edge-input').value);
                if(isNaN(v) || v < 0) { showToast("Dung lượng không hợp lệ", "error"); }
                else { 
                    if (editingEdge.data('capacity') !== v) {
                        editingEdge.data('capacity', v); editingEdge.data('capacityLabel', v.toString());
                        changed = true;
                    }
                }
                editingEdge.removeClass('editing'); editingEdge = null;
                document.getElementById('edge-input-container').style.display = 'none';
            }
            if(editingNode) {
                let val = document.getElementById('node-input').value.trim();
                if(val && cy.nodes(`[label="${val}"]`).empty() && editingNode.data('label') !== val) { 
                    editingNode.data('label', val); 
                    changed = true;
                }
                editingNode.removeClass('editing'); editingNode = null;
                document.getElementById('node-input-container').style.display = 'none';
                updateStatusPanel();
            }
            if(changed) saveState(); // LƯU LỊCH SỬ KHI CÓ EDIT
        }

        document.getElementById('edge-input').addEventListener('keydown', (e) => { if(e.key === 'Enter') commitAll(); });
        document.getElementById('node-input').addEventListener('keydown', (e) => { if(e.key === 'Enter') commitAll(); });

        function addBranch() {
            let label = getNextNodeLabel(); let pos = findEmptyPosition(selectedNode.position());
            let newNode = cy.add({ group: 'nodes', data: { id: 'n'+Date.now(), label: label, role: 'none' }, position: pos });
            let newEdge = cy.add({ group: 'edges', data: { id: 'e'+Date.now(), source: selectedNode.id(), target: newNode.id(), capacity: 10, capacityLabel: '10' } });
            selectedNode = newNode; updatePositions(); updateMetrics(window.currentGraphMode); openEdgeEditor(newEdge);
            saveState(); // LƯU LỊCH SỬ
        }

        function startLinkMode() { isLinking = true; nodeToolbar.style.display='none'; document.getElementById('link-hint').style.display='block'; }
        
        function setRole(r) { 
            cy.nodes().forEach(n => { if(n.data('role') === r) n.data('role', 'none'); }); 
            selectedNode.data('role', r); nodeToolbar.style.display='none'; updateStatusPanel(); 
            saveState(); // LƯU LỊCH SỬ
        }

        function sendToPython() {
            commitAll();
            let nodes = [], edges = [], src = null, snk = null;
            cy.nodes().forEach(n => {
                nodes.push({ id: n.id(), label: n.data('label'), role: n.data('role'), x: n.position('x'), y: n.position('y') });
                if(n.data('role') === 'source') src = n.id();
                if(n.data('role') === 'sink') snk = n.id();
            });
            cy.edges().forEach(e => { edges.push({ id: e.id(), source: e.data('source'), target: e.data('target'), capacity: e.data('capacity') }); });
            if(nodes.length < 2) { showToast("Vẽ thêm ít nhất 1 node nữa nhé", "warning"); return; }
            if(!src || !snk) { showToast("Bạn chưa chọn Nguồn (Source) hoặc Đích (Sink)!", "error"); return; }
            const data = { nodes, edges, source: src, sink: snk, ts: Date.now() };
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setComponentValue", value: data }, "*");
        }

        window.addEventListener("message", (event) => {
            if (event.data.type !== "streamlit:render") return;
            window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:setFrameHeight", height: 680 }, "*");
            const args = event.data.args;
            window.currentGraphMode = args.graph_mode || "Có hướng";
            
            const isUndirected = window.currentGraphMode === "Vô hướng";
            cy.style().selector('edge').style({ 'target-arrow-shape': isUndirected ? 'none' : 'triangle' }).update();
            updateMetrics(window.currentGraphMode);

            if (!isInitialized) {
                setTimeout(() => {
                    cy.resize();
                    if (args.initial_graph && args.initial_graph.nodes && args.initial_graph.nodes.length > 0) {
                        args.initial_graph.nodes.forEach(n => cy.add({ data: { id: n.id, label: n.label, role: n.role }, position: { x: n.x, y: n.y } }));
                        args.initial_graph.edges.forEach(e => cy.add({ data: { id: e.id, source: e.source, target: e.target, capacity: e.capacity, capacityLabel: e.capacity.toString() } }));
                        handleFocusView();
                    } else {
                        let n = cy.add({ group: 'nodes', data: { id: 'n1', label: '1', role: 'none' }, position: { x: 0, y: 0 } });
                        cy.center(n); cy.zoom(0.85);
                    }
                    updateStatusPanel(); updateMetrics(window.currentGraphMode);
                    saveState(); // LƯU TRẠNG THÁI KHỞI TẠO ĐẦU TIÊN CHO LỊCH SỬ
                }, 100);
                isInitialized = true;
            }
            if (args.results && !args.results.error) {
                // Update side panel result
                document.getElementById('side-result-box').style.display = 'block';
                document.getElementById('res-val-side').innerText = args.results.maxflow;

                cy.edges().forEach(e => {
                    let d = args.results.flow_data[e.id()];
                    if(d) {
                        e.data('capacityLabel', d.flow + '/' + e.data('capacity'));
                        e.removeClass('flowing saturated residual mincut');
                        if(d.flow > 0 && d.flow < e.data('capacity')) e.addClass('flowing');
                        else if(d.flow >= e.data('capacity')) e.addClass('saturated');
                        else e.addClass('residual');
                        if(d.is_mincut) e.addClass('mincut');
                    }
                });
                showToast("Mô phỏng luồng thành công!", "success");
                showResultModal('success', args.results); // HIỂN THỊ MODAL KẾT QUẢ THÀNH CÔNG
            } else if (args.results?.error) { 
                showToast(args.results.error, "error"); 
                showResultModal('error', args.results); // HIỂN THỊ MODAL LỖI
            }
        });
        window.parent.postMessage({ isStreamlitMessage: true, type: "streamlit:componentReady", apiVersion: 1 }, "*");
    </script>
</body>
</html>
"""

# ==========================================
# 3. STREAMLIT LOGIC & BACKEND
# ==========================================
COMPONENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cyto_frontend_build")
os.makedirs(COMPONENT_DIR, exist_ok=True)
with open(os.path.join(COMPONENT_DIR, "index.html"), "w", encoding="utf-8") as f:
    f.write(HTML_EDITOR_CODE)

graph_editor = components.declare_component("graph_editor", path=COMPONENT_DIR)

if "current_graph" not in st.session_state:
    st.session_state.current_graph = { "nodes": [{"id": "n1", "label": "1", "role": "none", "x": 0, "y": 0}], "edges": [] }
if "computation_results" not in st.session_state: st.session_state.computation_results = None
if "last_ts" not in st.session_state: st.session_state.last_ts = None

graph_data = graph_editor(
    initial_graph=st.session_state.current_graph,
    results=st.session_state.computation_results,
    graph_mode=graph_mode,
    key="interactive_editor_v10"
)

if graph_data:
    current_ts = graph_data.get("ts")
    if current_ts and current_ts != st.session_state.last_ts:
        st.session_state.last_ts = current_ts
        st.session_state.current_graph = graph_data
        
        src_id, snk_id = str(graph_data["source"]), str(graph_data["sink"])
        id_to_label = {n["id"]: n["label"] for n in graph_data["nodes"]}
        G = nx.DiGraph()
        for n in graph_data["nodes"]: G.add_node(n["id"])
        for e in graph_data["edges"]:
            u, v, cap = str(e["source"]), str(e["target"]), int(e["capacity"])
            G.add_edge(u, v, capacity=cap, id=e["id"])
            if graph_mode == "Vô hướng":
                G.add_edge(v, u, capacity=cap)

        try:
            if not nx.has_path(G, src_id, snk_id): raise ValueError(f"Không có đường đi từ node {id_to_label[src_id]} đến {id_to_label[snk_id]}")
            flow_val, flow_dict = nx.maximum_flow(G, src_id, snk_id)
            cut_val, partition = nx.minimum_cut(G, src_id, snk_id)
            reachable, non_reachable = partition
            flow_res = { e_attr["id"]: { "flow": flow_dict[u][v], "is_mincut": (u in reachable and v in non_reachable) } for u, v, e_attr in G.edges(data=True) if "id" in e_attr }
            st.session_state.computation_results = { 
                "maxflow": flow_val, 
                "mincut": cut_val, 
                "phi": [id_to_label[n] for n in reachable], 
                "psi": [id_to_label[n] for n in non_reachable], 
                "flow_data": flow_res,
                "source_lbl": id_to_label[src_id],
                "sink_lbl": id_to_label[snk_id]
            }
        except Exception as e:
            st.session_state.computation_results = {"error": str(e)}
        st.rerun()

# ==========================================
# 4. HIỂN THỊ KẾT QUẢ DẠNG CARD (STREAMLIT)
# ==========================================
if st.session_state.computation_results and "maxflow" in st.session_state.computation_results:
    res = st.session_state.computation_results
    st.markdown("---")
    st.markdown(f"<h3 style='text-align:center; color:#1E293B;'>📊 KẾT QUẢ PHÂN TÍCH CHI TIẾT</h3><br>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 1.5, 1.5])
    
    with c1:
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #3B82F6">
            <div class="card-label">Lưu lượng cực đại (Max Flow)</div>
            <div class="card-val" style="color: #3B82F6; font-size:24px;">{res["maxflow"]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #10B981">
            <div class="card-label">Tập lát cát Φ (Nguồn)</div>
            <div class="card-val">{'{ ' + ', '.join(sorted(res['phi'])) + ' }'}</div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="result-card" style="border-left-color: #EF4444">
            <div class="card-label">Tập lát cát Ψ (Đích)</div>
            <div class="card-val">{'{ ' + ', '.join(sorted(res['psi'])) + ' }'}</div>
        </div>
        """, unsafe_allow_html=True)
