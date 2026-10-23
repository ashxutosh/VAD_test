import streamlit as st
import plotly.graph_objects as go
from logic import (
    AROUSAL_BINS,
    DOMINANCE_BINS,
    EMOTION_COLORS,
    VALENCE_BINS,
    classify_point,
    get_cube_emotion,
    get_emotion_percentages,
)

st.title("🧊 VAD Space - Single Slice Inspector")
st.page_link("pages/logic.py", label="View VAD Logic", icon="📘", width="content")


# Sidebar Controls
st.sidebar.header("⚙️ View Options & Inputs")
view_mode = st.sidebar.radio("Display Mode", ["Full 3D Space (All 245 Cubes)", "Single Slice View"])

split_axis = "Dominance (Z)"
selected_slice_idx = 0

if view_mode == "Single Slice View":
    split_axis = st.sidebar.selectbox("Choose Axis to Slice", ["Dominance (Z)", "Valence (Y)", "Arousal (X)"])
    if split_axis == "Dominance (Z)":
        max_idx = 5
        labels = [f"D{i+1}: {DOMINANCE_BINS[i]} to {DOMINANCE_BINS[i+1]}" for i in range(5)]
    elif split_axis == "Valence (Y)":
        max_idx = 7
        labels = [f"V{i+1}: {VALENCE_BINS[i]} to {VALENCE_BINS[i+1]}" for i in range(7)]
    else:
        max_idx = 7
        labels = [f"A{i+1}: {AROUSAL_BINS[i]} to {AROUSAL_BINS[i+1]}" for i in range(7)]
        
    chosen_label = st.sidebar.selectbox("Select Slice", labels)
    selected_slice_idx = labels.index(chosen_label)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Input Vector Point (V, A, D)")
in_a = st.sidebar.number_input("Arousal (X)", min_value=-1.0, max_value=1.0, value=0.2, step=0.05, key="ordering_arousal")
in_v = st.sidebar.number_input("Valence (Y)", min_value=-1.0, max_value=1.0, value=-0.5, step=0.05, key="ordering_valence")
in_d = st.sidebar.number_input("Dominance (Z)", min_value=-1.0, max_value=1.0, value=0.0, step=0.05, key="ordering_dominance")

classification = classify_point(in_a, in_v, in_d)
target_a_idx = classification.arousal_index
target_v_idx = classification.valence_index
target_z_idx = classification.dominance_index
primary_emotion = classification.emotion

# Build Single Mesh Traces based on mode
fig = go.Figure()

# Bright Glowing Axes
fig.add_trace(go.Scatter3d(x=[-1, 1], y=[0, 0], z=[0, 0], mode='lines', line=dict(color='#FF1493', width=8), name='Arousal (X)'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[-1, 1], z=[0, 0], mode='lines', line=dict(color='#00FF00', width=8), name='Valence (Y)'))
fig.add_trace(go.Scatter3d(x=[0, 0], y=[0, 0], z=[-1, 1], mode='lines', line=dict(color='#00FFFF', width=8), name='Dominance (Z)'))

cat_mesh_data = {
    "happy": {"x": [], "y": [], "z": [], "i": [], "j": [], "k": [], "centers": []},
    "neutral": {"x": [], "y": [], "z": [], "i": [], "j": [], "k": [], "centers": []},
    "sadness": {"x": [], "y": [], "z": [], "i": [], "j": [], "k": [], "centers": []},
    "angry": {"x": [], "y": [], "z": [], "i": [], "j": [], "k": [], "centers": []}
}

for ai in range(7):
    for vi in range(7):
        for zi in range(5):
            # Filter for single slice view
            if view_mode == "Single Slice View":
                if split_axis == "Dominance (Z)" and zi != selected_slice_idx: continue
                if split_axis == "Valence (Y)" and vi != selected_slice_idx: continue
                if split_axis == "Arousal (X)" and ai != selected_slice_idx: continue
                
            emo = get_cube_emotion(ai, vi, zi)
            x0, x1 = AROUSAL_BINS[ai], AROUSAL_BINS[ai+1]
            y0, y1 = VALENCE_BINS[vi], VALENCE_BINS[vi+1]
            z0, z1 = DOMINANCE_BINS[zi], DOMINANCE_BINS[zi+1]
            
            cat_mesh_data[emo]["centers"].append(((x0+x1)/2, (y0+y1)/2, (z0+z1)/2))
            
            vx = [x0, x1, x1, x0, x0, x1, x1, x0]
            vy = [y0, y0, y1, y1, y0, y0, y1, y1]
            vz = [z0, z0, z0, z0, z1, z1, z1, z1]
            
            cat_mesh_data[emo]["x"].extend(vx)
            cat_mesh_data[emo]["y"].extend(vy)
            cat_mesh_data[emo]["z"].extend(vz)
            
            base = len(cat_mesh_data[emo]["x"]) - 8
            tri_i = [0, 0, 4, 4, 0, 0, 1, 1, 3, 3, 2, 2]
            tri_j = [1, 2, 5, 6, 3, 4, 5, 6, 2, 7, 6, 7]
            tri_k = [2, 3, 6, 7, 4, 7, 6, 2, 7, 6, 7, 3]
            
            cat_mesh_data[emo]["i"].extend([base + idx for idx in tri_i])
            cat_mesh_data[emo]["j"].extend([base + idx for idx in tri_j])
            cat_mesh_data[emo]["k"].extend([base + idx for idx in tri_k])

for emo, d in cat_mesh_data.items():
    if d["x"]:
        fig.add_trace(go.Mesh3d(
            x=d["x"], y=d["y"], z=d["z"],
            i=d["i"], j=d["j"], k=d["k"],
            color=EMOTION_COLORS[emo],
            opacity=0.35,
            name=f"{emo.capitalize()}",
            showlegend=True
        ))

# Prominent Glowing Point
fig.add_trace(go.Scatter3d(
    x=[in_a], y=[in_v], z=[in_d],
    mode='markers+text',
    marker=dict(size=14, color='#FFEA00', symbol='diamond', line=dict(color='#000000', width=2.5)),
    text=["<b>Input Point</b>"], textposition="top center", name="Input Point"
))

fig.update_layout(
    scene=dict(
        xaxis=dict(title='Arousal (X)', range=[-1.1, 1.1]),
        yaxis=dict(title='Valence (Y)', range=[-1.1, 1.1]),
        zaxis=dict(title='Dominance (Z)', range=[-1.1, 1.1]),
        aspectmode='cube', camera=dict(eye=dict(x=1.6, y=1.6, z=1.3))
    ),
    margin=dict(l=0, r=0, b=0, t=30), height=700
)

col1, col2 = st.columns([2.8, 1])

with col1:
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("📊 Output & Proximity Logic")
    st.info(f"**Target Vector:**\n- **Arousal (X):** `{in_a:.2f}`\n- **Valence (Y):** `{in_v:.2f}`\n- **Dominance (Z):** `{in_d:.2f}`")
    
    st.success(f"🏆 **Primary Emotion:** `{primary_emotion.upper()}`")
    st.write(f"*(Sub-cube Index -> Arousal:A{target_a_idx+1}, Valence:V{target_v_idx+1}, Dominance:D{target_z_idx+1})*")
    
    percentages = get_emotion_percentages(in_a, in_v, in_d)
    
    st.markdown("---")
    st.subheader("📈 **Emotion Percentages:**")
    
    formatted_percentages = {emo: round(p, 2) for emo, p in percentages.items()}
    st.json({"emotion_percentages": formatted_percentages})
    
    for emo, pct in formatted_percentages.items():
        st.write(f"**{emo.capitalize()}:** `{pct}%`")
        st.progress(float(pct / 100.0))