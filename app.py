import streamlit as st
import plotly.graph_objects as go
import numpy as np

if __name__ == "__main__":
    st.set_page_config(page_title="245 Cubes PAD Space (Single Slice Viewer)", layout="wide")

st.title("🧊 PAD Space - Single Slice Inspector")
st.markdown("""
- **Single Slice View:** Ek baar mein sirf ek selected slice ($D$, $V$, ya $A$) display hogi.
""")

arousal_bins = [-1.00, -0.71, -0.43, -0.14, 0.14, 0.43, 0.71, 1.00]
valence_bins = [-1.00, -0.71, -0.43, -0.14, 0.14, 0.43, 0.71, 1.00]
dominance_bins = [-1.00, -0.60, -0.20, 0.20, 0.60, 1.00]

EMOTION_COLORS = {
    "happy": "#28A745",   # Green (105)
    "neutral": "#6C757D", # Grey (35)
    "sadness": "#007BFF", # Blue (54)
    "angry": "#DC3545"    # Red (51)
}

def get_cube_emotion(ai, vi, zi):
    if vi >= 4:
        return "happy"
    if vi == 3:
        return "neutral"
    if zi <= 1:
        return "sadness"
    elif zi == 2:
        return "sadness" if ai <= 2 else "angry"
    elif zi == 3:
        return "sadness" if ai == 0 else "angry"
    else:
        return "angry"

# Sidebar Controls
st.sidebar.header("⚙️ View Options & Inputs")
view_mode = st.sidebar.radio("Display Mode", ["Full 3D Space (All 245 Cubes)", "Single Slice View"])

split_axis = "Dominance (Z)"
selected_slice_idx = 0

if view_mode == "Single Slice View":
    split_axis = st.sidebar.selectbox("Choose Axis to Slice", ["Dominance (Z)", "Valence (Y)", "Arousal (X)"])
    if split_axis == "Dominance (Z)":
        max_idx = 5
        labels = [f"D{i+1}: {dominance_bins[i]} to {dominance_bins[i+1]}" for i in range(5)]
    elif split_axis == "Valence (Y)":
        max_idx = 7
        labels = [f"V{i+1}: {valence_bins[i]} to {valence_bins[i+1]}" for i in range(7)]
    else:
        max_idx = 7
        labels = [f"A{i+1}: {arousal_bins[i]} to {arousal_bins[i+1]}" for i in range(7)]
        
    chosen_label = st.sidebar.selectbox("Select Slice", labels)
    selected_slice_idx = labels.index(chosen_label)

st.sidebar.markdown("---")
st.sidebar.subheader("📍 Input Vector Point (V, A, D)")
in_a = st.sidebar.number_input("Arousal (X)", min_value=-1.0, max_value=1.0, value=0.2, step=0.05, key="ordering_arousal")
in_v = st.sidebar.number_input("Valence (Y)", min_value=-1.0, max_value=1.0, value=-0.5, step=0.05, key="ordering_valence")
in_d = st.sidebar.number_input("Dominance (Z)", min_value=-1.0, max_value=1.0, value=0.0, step=0.05, key="ordering_dominance")

def find_bin_index(val, bins):
    for i in range(len(bins) - 1):
        if bins[i] <= val <= bins[i+1]:
            return i
    return len(bins) - 2 if val >= bins[-1] else 0

target_a_idx = find_bin_index(in_a, arousal_bins)
target_v_idx = find_bin_index(in_v, valence_bins)
target_z_idx = find_bin_index(in_d, dominance_bins)

primary_emotion = get_cube_emotion(target_a_idx, target_v_idx, target_z_idx)

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
            x0, x1 = arousal_bins[ai], arousal_bins[ai+1]
            y0, y1 = valence_bins[vi], valence_bins[vi+1]
            z0, z1 = dominance_bins[zi], dominance_bins[zi+1]
            
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
    
    # Calculate percentages across all 245 centers
    all_centers = []
    for ai in range(7):
        for vi in range(7):
            for zi in range(5):
                emo = get_cube_emotion(ai, vi, zi)
                x0, x1 = arousal_bins[ai], arousal_bins[ai+1]
                y0, y1 = valence_bins[vi], valence_bins[vi+1]
                z0, z1 = dominance_bins[zi], dominance_bins[zi+1]
                all_centers.append((emo, (x0+x1)/2, (y0+y1)/2, (z0+z1)/2))

    cat_collected = {emo: [] for emo in EMOTION_COLORS.keys()}
    for emo, cx, cy, cz in all_centers:
        cat_collected[emo].append(np.sqrt((in_a - cx)**2 + (in_v - cy)**2 + (in_d - cz)**2))
        
    emotion_dists = {emo: min(dists) if dists else 3.0 for emo, dists in cat_collected.items()}

    sigma = 0.4
    weights = {emo: np.exp(-dist / sigma) for emo, dist in emotion_dists.items()}
    total_w = sum(weights.values())
    percentages = {emo: float(weights[emo] / total_w) * 100 for emo in weights}
    
    st.markdown("---")
    st.subheader("📈 **Emotion Percentages:**")
    
    formatted_percentages = {emo: round(p, 2) for emo, p in percentages.items()}
    st.json({"emotion_percentages": formatted_percentages})
    
    for emo, pct in formatted_percentages.items():
        st.write(f"**{emo.capitalize()}:** `{pct}%`")
        st.progress(float(pct / 100.0))