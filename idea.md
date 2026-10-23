# 🧠 3D Emotion Space Mapping (VAD Model)
### Technical Specification & Calculation Logic

---

## 1. 3D Space & Spatial Division

Hum **Valence (V)**, **Arousal (A)**, aur **Dominance (D)** ko $[-1.00, +1.00]$ ke 3D Coordinate Space mein Mapping kar rahe hain. Is poore space ko **245 sub-cubes** mein divide kiya gaya hai:

* **X-Axis (Arousal - $A$):** 7 Grids ($A_1$ se $A_7$)
  * **Cut-points:** `[-1.00, -0.71, -0.43, -0.14, +0.14, +0.43, +0.71, +1.00]`
* **Y-Axis (Valence - $V$):** 7 Grids ($V_1$ se $V_7$)
  * **Cut-points:** `[-1.00, -0.71, -0.43, -0.14, +0.14, +0.43, +0.71, +1.00]`
* **Z-Axis (Dominance - $D$):** 5 Grids ($D_1$ se $D_5$)
  * **Cut-points:** `[-1.00, -0.60, -0.20, +0.20, +0.60, +1.00]`

$$\text{Total Sub-cubes} = 7 (A) \times 7 (V) \times 5 (D) = \mathbf{245 \text{ Cubes}}$$

---

## 2. Color & Emotion Mapping Rules

Har cube ko uske $(A, V, D)$ spatial index ke basis par ek primary emotion aur color assigned hai:

### A. Happy (Green) — **105 Cubes**
* **Condition:** Positive Valence Zone ($V_5, V_6, V_7$) — Range: $+0.14$ se $+1.00$
* **Calculation:** $7 \text{ (Arousal)} \times 3 \text{ (Valence)} \times 5 \text{ (Dominance)} = \mathbf{105 \text{ cubes}}$

### B. Neutral (Grey) — **35 Cubes**
* **Condition:** Neutral Valence Zone ($V_4$) — Range: $-0.14$ se $+0.14$
* **Calculation:** $7 \text{ (Arousal)} \times 1 \text{ (Valence)} \times 5 \text{ (Dominance)} = \mathbf{35 \text{ cubes}}$

---

### Negative Valence Zone ($V_1, V_2, V_3$)
Negative Valence region (Range: $-1.00$ se $-0.14$) ko Dominance ($D$) aur Arousal ($A$) ke combination se **Sadness** aur **Angry** mein break kiya jata hai:

### C. Sadness (Blue) — **54 Cubes**
* **$D_1, D_2$:** Saare $A$ ($1\dots7$) aur $V$ ($1\dots3$) $\rightarrow 7 \times 3 \times 2 = \mathbf{42 \text{ cubes}}$
* **$D_3$:** Low Arousal ($A_1 \dots A_3$) aur $V$ ($1\dots3$) $\rightarrow 3 \times 3 \times 1 = \mathbf{9 \text{ cubes}}$
* **$D_4$:** Extremely Low Arousal ($A_1$) aur $V$ ($1\dots3$) $\rightarrow 1 \times 3 \times 1 = \mathbf{3 \text{ cubes}}$
* **$D_5$:** $\mathbf{0 \text{ cubes}}$
* **Total Sadness:** $42 + 9 + 3 = \mathbf{54 \text{ cubes}}$

### D. Angry (Red) — **51 Cubes**
* **$D_1, D_2$:** $\mathbf{0 \text{ cubes}}$
* **$D_3$:** Medium/High Arousal ($A_4 \dots A_7$) aur $V$ ($1\dots3$) $\rightarrow 4 \times 3 \times 1 = \mathbf{12 \text{ cubes}}$
* **$D_4$:** Higher Arousal ($A_2 \dots A_7$) aur $V$ ($1\dots3$) $\rightarrow 6 \times 3 \times 1 = \mathbf{18 \text{ cubes}}$
* **$D_5$:** Saare Arousal ($A_1 \dots A_7$) aur $V$ ($1\dots3$) $\rightarrow 7 \times 3 \times 1 = \mathbf{21 \text{ cubes}}$
* **Total Angry:** $12 + 18 + 21 = \mathbf{51 \text{ cubes}}$

> **Sanity Check:** $105 \text{ (Happy)} + 35 \text{ (Neutral)} + 54 \text{ (Sadness)} + 51 \text{ (Angry)} = \mathbf{245 \text{ Total Cubes}}$

---

## 3. Point Placement & Emotion Distribution Algorithm

Jab system ko ek Input Vector Point $(V, A, D)$ milta hai (Jaise: $A=0.20, V=-0.50, D=0.00$):

### Step 1: Primary Emotion Identification
* Direct lookup se check kiya jata hai ki point $245$ me se kis exact sub-cube me land kar raha hai.
* Us sub-cube ki label/color hi user ka **Primary Emotion** banta hai.

### Step 2: Continuous Probability Distribution (Softmax)
Point se har emotion category ke cluster centers ki distance calculate karke % distribution banaya jata hai:

1. **Euclidean Distance Calculate karein:**
   $$d_i = \sqrt{(V - V_i)^2 + (A - A_i)^2 + (D - D_i)^2}$$
2. **Softmax Weighting:**
   $$\text{Weight}_i = e^{-\frac{d_i}{\sigma}}$$
   *(Jahan $\sigma$ ek scaling factor/temperature parameter hai jo sharpness control karta hai).*
3. **Normalize (100% Scale):**
   $$\text{Percentage}_i = \left( \frac{\text{Weight}_i}{\sum \text{Weight}} \right) \times 100$$

*Example Output:* **Sadness:** $65\%$, **Neutral:** $15\%$, **Happy:** $10\%$, **Angry:** $10\%$

---

## 4. UI / UX & Visual Rendering Design

* **Translucent Mesh:** Cubes ki opacity $\mathbf{0.35}$ rakhi gayi hai taaki 3D interior structure aur overlapping bounds visible hon.
* **Slice Inspector Mode:** Multi-axis slicing ($A, V, D$) ka feature jo kisi bhi specific 2D cross-section layer ko solo view karne deta hai.
* **Neon Coordinate Axes:** Bright $X, Y, Z$ axes clear orientation guide ke liye.
* **Input Marker:** High-contrast **Yellow Diamond** shape target vector point ko highlight karne ke liye.