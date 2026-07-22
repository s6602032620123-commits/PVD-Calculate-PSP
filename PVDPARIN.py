"""
PVD Design Calculator
======================
โปรแกรมออกแบบ Prefabricated Vertical Drains (PVD)
อ้างอิงตามเอกสารประกอบการสอน 020323304 Ground Improvement Technique
Assoc. Prof. Dr. Ittipon Meepon - KMUTNB

ทฤษฎีที่ใช้:
- Barron (1948) : Ur (radial consolidation)
- Terzaghi      : Uv (vertical consolidation)
- Carillo (1942): Uav (average / combined consolidation)
- Settlement    : Sfinal, St
- Sand Mat      : Resistance Index (L)
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="PVD Design Calculator", page_icon="🧱", layout="wide")

# ---------------------------------------------------------------
# Session state สำหรับส่งค่าต่อระหว่างหน้า (ให้ไหลลื่นเหมือนออกแบบจริง)
# ---------------------------------------------------------------
defaults = {
    "dw": 5.0, "de": 113.0, "n": 22.6, "Fn": 2.32,
    "Cr": 140.0, "L_index": 0.0
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ---------------------------------------------------------------
# ฟังก์ชันคำนวณหลัก (ตรงตามสูตรในสไลด์)
# ---------------------------------------------------------------
def calc_dw(a_mm, b_mm, method):
    """a = ความกว้าง (mm), b = ความหนา (mm)"""
    if method == "วิธีของ Hansbo":
        return 2 * (a_mm + b_mm) / np.pi
    else:  # Rixner
        return (a_mm + b_mm) / 2


def calc_de(S, pattern):
    """S = ระยะห่าง PVD, หน่วยเดียวกับที่ต้องการ de"""
    return 1.13 * S if pattern == "สี่เหลี่ยมจัตุรัส (Square)" else 1.05 * S


def calc_Fn(n):
    return (n ** 2 / (n ** 2 - 1)) * np.log(n) - (3 * n ** 2 - 1) / (4 * n ** 2)


def calc_Ur(Tr, Fn, L_index=0.0):
    """Ur ตามวิธี Barron, ถ้า L_index=0 คือไม่คิดผลจาก sand mat"""
    return 1 - np.exp(-8 * Tr / (Fn + 0.8 * L_index))


def calc_Uv(Tv):
    """Uv ตามทฤษฎี Terzaghi (Atkinson & Eldred, 1981)
    ใช้สูตรมาตรฐาน 2 ช่วง: U<=60% ใช้สูตรราก, U>60% ใช้สูตร log"""
    if Tv <= 0.286:
        Uv = np.sqrt(4 * Tv / np.pi)
    else:
        Uv = 1 - 10 ** (-(Tv + 0.085) / 0.933)
    return min(Uv, 0.999999)


def calc_Uav(Ur, Uv):
    """Carillo (1942)"""
    return 1 - (1 - Ur) * (1 - Uv)


def calc_Sfinal(H, Cc, e0, sigma0, delta_sigma):
    return H * (Cc / (1 + e0)) * np.log10((sigma0 + delta_sigma) / sigma0)


def calc_L_index(n, H, Hm, kc, km, B, dw):
    """ดัชนีความต้านทานของ Sand Mat -- ทุกความยาวต้องหน่วยเดียวกัน (H,Hm,B,dw)"""
    return (32 / np.pi ** 2) * (1 / n ** 2) * (H / Hm) * (kc / km) * (B / dw) ** 2


# =================================================================
# SIDEBAR - เมนูนำทาง
# =================================================================
st.sidebar.title("🧱 PVD Design Tool")
page = st.sidebar.radio(
    "เลือกขั้นตอนการออกแบบ",
    [
        "📘 หลักการ PVD",
        "1️⃣ หา dw, de, n",
        "2️⃣ คำนวณ Ur (Barron)",
        "3️⃣ คำนวณ Uv (Terzaghi)",
        "4️⃣ คำนวณ Uav (Carillo) และตรวจสอบ",
        "5️⃣ คำนวณการทรุดตัว (Settlement)",
        "6️⃣ Sand Mat (Resistance Index L)",
        "7️⃣ กราฟ Consolidation vs Time",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption("อ้างอิง: Barron (1948), Terzaghi, Carillo (1942)\nBergado et al. (1992)")

# =================================================================
# PAGE 0: หลักการ
# =================================================================
if page == "📘 หลักการ PVD":
    st.title("Prefabricated Vertical Drains (PVD)")
    st.markdown("""
Prefabricated Vertical Drains (PVD) หรือ **wick drain / strip drain** เป็นวิธีเร่งการอัดตัวคายน้ำ
(consolidation) ของดินเหนียวอ่อนอิ่มตัว โดยลดระยะทางที่น้ำต้องเดินทางออกจากดิน (drainage path)

**ขั้นตอนการออกแบบในโปรแกรมนี้**
1. หาขนาดสมมูลของ PVD (dw) และรัศมีอิทธิพล (de, n)
2. คำนวณระดับการอัดตัวคายน้ำในแนวรัศมี (Ur) ด้วยวิธี Barron
3. คำนวณระดับการอัดตัวคายน้ำในแนวดิ่ง (Uv) ด้วยทฤษฎี Terzaghi
4. รวมผลด้วยวิธี Carillo เป็น Uav แล้วตรวจสอบว่าเข้าเกณฑ์ที่ต้องการหรือไม่ (ปกติ ≥ 90%)
5. คำนวณค่าการทรุดตัวสุดท้าย (Sfinal) และการทรุดตัว ณ เวลาที่สนใจ (St)
6. ตรวจสอบผลกระทบของชั้นทรายรอง (Sand Mat) ต่อประสิทธิภาพการระบายน้ำ (Resistance Index, L)
7. ดูกราฟความสัมพันธ์ระหว่าง % Consolidation กับเวลา
    """)
    c1, c2 = st.columns(2)
    with c1:
        st.info("**Ur = 1 − exp(−8Tr / F(n))**\n\nวิธี Barron (1948)")
    with c2:
        st.info("**Uav = 1 − (1−Ur)(1−Uv)**\n\nวิธี Carillo (1942)")

# =================================================================
# PAGE 1: dw, de, n
# =================================================================
elif page == "1️⃣ หา dw, de, n":
    st.title("1️⃣ ขนาดสมมูลของ PVD และรัศมีอิทธิพล")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("ขนาดแผ่น PVD")
        a = st.number_input("ความกว้าง a (mm)", value=100.0, step=1.0)
        b = st.number_input("ความหนา b (mm)", value=5.0, step=0.5)
        method = st.selectbox("วิธีคำนวณ dw", ["วิธีของ Hansbo", "วิธีของ Rixner"])
        use_practical = st.checkbox("ใช้ dw = 5 cm ตามแนวปฏิบัติ (ผลจาก Shrinkage ของหน้าตัด)", value=True)

        if use_practical:
            dw = 5.0
        else:
            dw = calc_dw(a, b, method) / 10  # mm -> cm
        st.success(f"dw = {dw:.3f} cm")

    with col2:
        st.subheader("รูปแบบการติดตั้งและระยะห่าง")
        pattern = st.selectbox("รูปแบบ", ["สี่เหลี่ยมจัตุรัส (Square)", "สามเหลี่ยม (Triangular)"])
        S = st.number_input("ระยะห่าง S (m)", value=1.0, step=0.1, min_value=0.1)

        de = calc_de(S, pattern) * 100  # m -> cm (S in m, de formula uses S directly, then convert)
        # de จริง ๆ คำนวณจาก S หน่วยเดียวกับที่ต้องการ -> ให้เป็น cm
        de = calc_de(S * 100, pattern)  # S(cm)
        st.success(f"de = {de:.3f} cm")

        n = de / dw
        st.success(f"n = de / dw = {n:.3f}")

    st.markdown("---")
    st.subheader("ตัวประกอบระยะห่าง F(n) — Drain Spacing Factor")
    Fn = calc_Fn(n)
    st.latex(r"F(n) = \frac{n^2}{n^2-1}\ln(n) - \frac{3n^2-1}{4n^2}")
    st.success(f"F(n) = {Fn:.4f}")

    if st.button("💾 บันทึกค่า dw, de, n, F(n) เพื่อใช้ในหน้าถัดไป", type="primary"):
        st.session_state["dw"] = dw
        st.session_state["de"] = de
        st.session_state["n"] = n
        st.session_state["Fn"] = Fn
        st.toast("บันทึกค่าเรียบร้อย ไปหน้า 2 ได้เลย ✅")

    with st.expander("📋 ตารางเปรียบเทียบ (ลองเปลี่ยน S หลายค่า)"):
        S_list = [S - 0.2, S - 0.1, S, S + 0.1, S + 0.2]
        S_list = [s for s in S_list if s > 0]
        rows = []
        for s in S_list:
            de_i = calc_de(s * 100, pattern)
            n_i = de_i / dw
            Fn_i = calc_Fn(n_i)
            rows.append([s, de_i, n_i, n_i**2, Fn_i])
        df = pd.DataFrame(rows, columns=["S (m)", "de (cm)", "n", "n²", "F(n)"])
        st.dataframe(df.style.format(precision=3), use_container_width=True)

# =================================================================
# PAGE 2: Ur (Barron)
# =================================================================
elif page == "2️⃣ คำนวณ Ur (Barron)":
    st.title("2️⃣ ระดับการอัดตัวคายน้ำแนวรัศมี (Ur) — วิธี Barron")

    st.info(f"ใช้ค่าจากหน้าก่อนหน้า: de = {st.session_state['de']:.3f} cm, "
            f"n = {st.session_state['n']:.3f}, F(n) = {st.session_state['Fn']:.4f}")

    col1, col2 = st.columns(2)
    with col1:
        Cv = st.number_input("Cv — สปส. การอัดตัวคายน้ำแนวดิ่ง (cm²/day) [จาก Lab]", value=20.0)
        ratio = st.number_input("kr/kv (อัตราส่วนการซึมผ่านแนวรัศมี/แนวดิ่ง) — ทั่วไปกรุงเทพ 4–10", value=7.0)
        Cr = ratio * Cv
        st.success(f"Cr = (kr/kv) × Cv = {Cr:.2f} cm²/day")
    with col2:
        t = st.number_input("t — เวลาที่ต้องการ (วัน)", value=90.0)
        de = st.number_input("de (cm)", value=float(st.session_state["de"]))
        Fn = st.number_input("F(n)", value=float(st.session_state["Fn"]), format="%.4f")

    Tr = Cr * t / de ** 2
    st.latex(r"T_r = \frac{C_r \times t}{d_e^2}")
    st.success(f"Tr = {Tr:.4f}")

    Ur = calc_Ur(Tr, Fn)
    st.latex(r"U_r = 1 - \exp\left(\frac{-8T_r}{F(n)}\right)")
    st.metric("Ur (%)", f"{Ur*100:.2f} %")

    st.session_state["Cr"] = Cr
    st.session_state["Ur_value"] = Ur
    st.session_state["t_value"] = t

# =================================================================
# PAGE 3: Uv (Terzaghi)
# =================================================================
elif page == "3️⃣ คำนวณ Uv (Terzaghi)":
    st.title("3️⃣ ระดับการอัดตัวคายน้ำแนวดิ่ง (Uv) — ทฤษฎี Terzaghi")

    col1, col2 = st.columns(2)
    with col1:
        Cv = st.number_input("Cv (cm²/day)", value=20.0, key="cv_page3")
        t = st.number_input("t (วัน)", value=float(st.session_state.get("t_value", 90.0)), key="t_page3")
    with col2:
        Hd_m = st.number_input("Hd — ระยะทางไกลสุดที่น้ำระบายออกได้ในสนาม (m)", value=15.0,
                                help="กรณีระบายน้ำ 2 ทาง Hd = ครึ่งหนึ่งของความหนาชั้นดิน")
        Hd = Hd_m * 100  # m -> cm

    Tv = Cv * t / Hd ** 2
    st.latex(r"T_v = \frac{C_v \times t}{H_d^2}")
    st.success(f"Tv = {Tv:.6f}")

    Uv = calc_Uv(Tv)
    st.latex(r"U_v = \sqrt{\frac{4 T_v}{\pi}} \quad (U_v \le 60\%)")
    st.metric("Uv (%)", f"{Uv*100:.3f} %")

    if Uv > 0.6:
        st.warning("Uv เกิน 60% แล้ว — โปรแกรมสลับไปใช้สูตร log-form ของ Terzaghi โดยอัตโนมัติ")

    st.session_state["Uv_value"] = Uv

# =================================================================
# PAGE 4: Uav (Carillo) + ตรวจสอบ
# =================================================================
elif page == "4️⃣ คำนวณ Uav (Carillo) และตรวจสอบ":
    st.title("4️⃣ ระดับการอัดตัวคายน้ำเฉลี่ย (Uav) — วิธี Carillo")

    col1, col2 = st.columns(2)
    with col1:
        Ur = st.number_input("Ur (จากหน้า 2, เป็นสัดส่วน 0–1)",
                              value=float(st.session_state.get("Ur_value", 0.9667)), format="%.4f")
    with col2:
        Uv = st.number_input("Uv (จากหน้า 3, เป็นสัดส่วน 0–1)",
                              value=float(st.session_state.get("Uv_value", 0.018)), format="%.4f")

    Uav = calc_Uav(Ur, Uv)
    st.la
