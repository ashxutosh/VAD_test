import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Page configuration
if __name__ == "__main__":
    st.set_page_config(page_title="3D Emotion Spatial Visualizer & Classifier", layout="wide")

st.title("🧠 3D Emotion Spatial Visualizer & Multi-Category Classifier (PAD Space)")
st.markdown("""
This interactive 3D application maps emotion spectrums into full **3D Bounding Spatial Volumes (Cuboids)** 
based on the **Valence-Arousal-Dominance (PAD)** model and calculates **categorical probabilities** using spatial distance proximity.
""")

# Default initial emotion ranges
DEFAULT_EMOTIONS = [
    {"id": 1, "name": "Anger (Hot anger/fury)", "category": "angry", "color": "#FF3333", "a_min": 0.25, "a_max": 1.0, "v_min": -1.0, "v_max": -0.25, "d_min": 0.25, "d_max": 1.0},
    {"id": 2, "name": "Contempt (Cold anger)", "category": "angry", "color": "#FF8C00", "a_min": -1.0, "a_max": 0.25, "v_min": -1.0, "v_max": -0.25, "d_min": 0.25, "d_max": 1.0},
    {"id": 3, "name": "Distress (Fear or anxiety)", "category": "sad", "color": "#9400D3", "a_min": 0.25, "a_max": 1.0, "v_min": -1.0, "v_max": -0.25, "d_min": -1.0, "d_max": -0.25},
    {"id": 4, "name": "Relaxed happiness", "category": "happy", "color": "#28A745", "a_min": -1.0, "a_max": 0.25, "v_min": 0.25, "v_max": 1.0, "d_min": -1.0, "d_max": 0.25},
    {"id": 5, "name": "Excited happiness (Joy)", "category": "happy", "color": "#00CED1", "a_min": 0.25, "a_max": 1.0, "v_min": 0.25, "v_max": 1.0, "d_min": -0.25, "d_max": 1.0},
    {"id": 6, "name": "Neutral", "category": "neutral", "color": "#808080", "a_min": -0.25, "a_max": 0.25, "v_min": -0.25, "v_max": 0.25, "d_min": -0.25, "d_max": 0.25},
    {"id": 7, "name": "Sadness", "category": "sad", "color": "#007BFF", "a_min": -1.0, "a_max": -0.25, "v_min": -1.0, "v_max": -0.25, "d_min": -1.0, "d_max": -0.25}
]

if "emotions" not in st.session_state:
    st.session_state.emotions = DEFAULT_EMOTIONS

# Sidebar Controls
st.sidebar.header("⚙️ Spatial Volume Configuration")

st.sidebar.subheader("📍 Input Vector Point (V, A, D)")
in_a = st.sidebar.number_input("Arousal (X)", min_value=-1.0, max_value=1.0, value=0.1, step=0.05)
in_v = st.sidebar.number_input("Valence (Y)", min_value=-1.0, max_value=1.0, value=-0.1, step=0.05)
in_d = st.sidebar.number_input("Dominance (Z)", min_value=-1.0, max_value=1.0, value=0.0, step=0.05)
show_planes = st.sidebar.checkbox("Show Orthogonal Slicing Planes", value=True)

st.sidebar.markdown("---")
st.sidebar.subheader("📐 Define Cubes & Ranges")

active_emotions = []
for i, emo in enumerate(st.session_state.emotions):
    with st.sidebar.expander(f"Cube [{emo['id']}]: {emo['name']}", expanded=False):
        c_name = st.text_input(f"Name #{emo['id']}", value=emo['name'], key=f"name_{i}")
        c_color = st.color_picker(f"Color #{emo['id']}", value=emo['color'], key=f"color_{i}")
        
        a_r = st.slider(f"Arousal Range (X) #{emo['id']}", -1.0, 1.0, (float(emo['a_min']), float(emo['a_max'])), 0.05, key=f"a_{i}")
        v_r = st.slider(f"Valence Range (Y) #{emo['id']}", -1.0, 1.0, (float(emo['v_min']), float(emo['v_max'])), 0.05, key=f"v_{i}")
        d_r = st.slider(f"Dominance Range (Z) #{emo['id']}", -1.0, 1.0, (float(emo['d_min']), float(emo['d_max'])), 0.05, key=f"d_{i}")
        
        active_emotions.append({
            "id": emo['id'], "name": c_name, "category": emo['category'], "color": c_color,
            "a_min": a_r[0], "a_max": a_r[1], "v_min": v_r[0], "v_max": v_r[1], "d_min": d_r[0], "d_max": d_r[1]
        })

def create_cuboid_mesh(emo):
    a0, a1 = emo['a_min'], emo['a_max']
    v0, v1 = emo['v_min'], emo['v_max']
    d0, d1 = emo['d_min'], emo['d_max']
    
    x = [a0, a1, a1, a0, a0, a1, a1, a0]
    y = [v0, v0, v1, v1, v0, v0, v1, v1]
    z = [d0, d0, d0, d0, d1, d1, d1, d1]
    
    i = [7, 0, 0, 0, 4, 4, 2, 6, 4, 0, 3, 7]
    j = [3, 4, 1, 2, 5, 6, 3, 7, 1, 1, 2, 6]
    k = [0, 7, 2, 3, 6, 7, 7, 2, 5, 4, 6, 2]
    
    mesh = go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color=emo['color'], opacity=0.25, name=f"Cube [{emo['id']}]: {emo['name']}", showlegend=True)
    
    lines_x = [a0, a1, a1, a0, a0, None, a0, a1, a1, a0, a0, None, a0, a0, None, a1, a1, None, a1, a1, None, a0, a0]
    lines_y = [v0, v0, v1, v1, v0, None, v0, v0, v1, v1, v0, None, v0, v0, None, v0, v0, None, v1, v1, None, v1, v1]
    lines_z = [d0, d0, d0, d0, d0, None, d1, d1, d1, d1, d1, None, d0, d1, None, d0, d1, None, d0, d1, None, d0, d1]
    
    wireframe = go.Scatter3d(x=lines_x, y=lines_y, z=lines_z, mode='lines', line=dict(color=emo['color'], width=4), showlegend=False)
    
    c_a, c_v, c_d = (a0 + a1)/2, (v0 + v1)/2, (d0 + d1)/2
    center_marker = go.Scatter3d(
        x=[c_a], y=[c_v], z=[c_d], mode='text+markers',
        marker=dict(size=14, color=emo['color'], line=dict(color='black', width=1)),
        text=[f"<b>{emo['id']}</b>"], textposition="middle center",
        textfont=dict(color='white', size=12, family="Arial Black"), showlegend=False
    )
    return [mesh, wireframe, center_marker]

# Build Main Figure
fig = go.Figure()

fig.add_trace(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='lines+text', line=dict(color='#0066FF', width=8), text=["-1", "1<br><b>Arousal (X)</b>"], textfont=dict(size=13, color='#0066FF'), showlegend=False))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode='lines+text', line=dict(color='#00AA00', width=8), text=["-1", "1<br><b>Valence (Y)</b>"], textfont=dict(size=13, color='#00AA00'), showlegend=False))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode='lines+text', line=dict(color='#FF0000', width=8), text=["-1", "1<br><b>Dominance (Z)</b>"], textfont=dict(size=13, color='#FF0000'), showlegend=False))

for emo in active_emotions:
    for trace in create_cuboid_mesh(emo):
        fig.add_trace(trace)

fig.add_trace(go.Scatter3d(
    x=[in_a], y=[in_v], z=[in_d], mode='markers+text',
    marker=dict(size=12, color='yellow', symbol='diamond', line=dict(color='black', width=2)),
    text=["<b>Input Point</b>"], textposition="top center", name="Input Point (V,A,D)", showlegend=True
))

if show_planes:
    fig.add_trace(go.Mesh3d(x=[in_a]*4, y=[-1, 1, 1, -1], z=[-1, -1, 1, 1], i=[0, 0], j=[1, 2], k=[2, 3], color='#0066FF', opacity=0.12, showlegend=False))
    fig.add_trace(go.Mesh3d(x=[-1, 1, 1, -1], y=[in_v]*4, z=[-1, -1, 1, 1], i=[0, 0], j=[1, 2], k=[2, 3], color='#00AA00', opacity=0.12, showlegend=False))
    fig.add_trace(go.Mesh3d(x=[-1, 1, 1, -1], y=[-1, -1, 1, 1], z=[in_d]*4, i=[0, 0], j=[1, 2], k=[2, 3], color='#FF0000', opacity=0.12, showlegend=False))

fig.update_layout(
    scene=dict(
        xaxis=dict(title='Arousal (X)', range=[-1.1, 1.1], backgroundcolor="white", gridcolor="#EEEEEE"),
        yaxis=dict(title='Valence (Y)', range=[-1.1, 1.1], backgroundcolor="white", gridcolor="#EEEEEE"),
        zaxis=dict(title='Dominance (Z)', range=[-1.1, 1.1], backgroundcolor="white", gridcolor="#EEEEEE"),
        aspectmode='cube', camera=dict(eye=dict(x=1.6, y=1.6, z=1.2))
    ),
    margin=dict(l=0, r=0, b=0, t=30), height=700
)

col_map, col_res = st.columns([3, 1])

with col_map:
    st.plotly_chart(fig, use_container_width=True)

with col_res:
    st.subheader("📊 Spatial & Categorical Output")
    st.info(f"**Target Vector:**\n- **Arousal (X):** `{in_a:.2f}`\n- **Valence (Y):** `{in_v:.2f}`\n- **Dominance (Z):** `{in_d:.2f}`")
    
    matches = []
    category_center_dists = {"angry": [], "happy": [], "neutral": [], "sad": []}
    
    for emo in active_emotions:
        in_a_range = emo['a_min'] <= in_a <= emo['a_max']
        in_v_range = emo['v_min'] <= in_v <= emo['v_max']
        in_d_range = emo['d_min'] <= in_d <= emo['d_max']
        
        center_a = (emo['a_min'] + emo['a_max']) / 2
        center_v = (emo['v_min'] + emo['v_max']) / 2
        center_d = (emo['d_min'] + emo['d_max']) / 2
        dist_to_center = np.sqrt(
            (in_a - center_a) ** 2
            + (in_v - center_v) ** 2
            + (in_d - center_d) ** 2
        )
        
        category_center_dists[emo['category']].append(dist_to_center)
        
        if in_a_range and in_v_range and in_d_range:
            matches.append(emo)
            
    if matches:
        st.success(f"✅ **Inside Cube [{matches[0]['id']}]: {matches[0]['name']}**")
    else:
        st.warning("⚠️ **Point in transition zone**")
        
    cat_dists = {cat: min(dists) if dists else 2.0 for cat, dists in category_center_dists.items()}
    sigma = 0.5
    weights = {cat: np.exp(-d / sigma) for cat, d in cat_dists.items()}
    total_w = sum(weights.values())
    cat_probs = {cat: float(weights[cat] / total_w) for cat in weights}
    
    st.markdown("---")
    st.subheader("🏷️ **Categorical Distribution:**")
    st.json({"category": cat_probs})
    
    for cat, prob in cat_probs.items():
        st.write(f"**{cat.capitalize()}:** `{prob * 100:.2f}%`")
        st.progress(prob)