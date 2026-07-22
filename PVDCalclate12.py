import math
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="PVD Design Calculator",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ โปรแกรมคำนวณการออกแบบ PVD")
st.caption(
    "คำนวณ Degree of Consolidation จาก Barron, Terzaghi และ Carillo "
    "สำหรับ Prefabricated Vertical Drains"
)

# -----------------------------
# Calculation functions
# -----------------------------
def equivalent_diameter(a_cm: float, b_cm: float, method: str) -> float:
    """Equivalent diameter of a band-shaped PVD in cm."""
    if method == "Hansbo":
        return 2.0 * (a_cm + b_cm) / math.pi
    return (a_cm + b_cm) / 2.0  # Rixner


def influence_diameter(spacing_m: float, pattern: str) -> float:
    """Diameter of influence zone in cm."""
    factor = 1.13 if pattern == "สี่เหลี่ยมจัตุรัส" else 1.05
    return factor * spacing_m * 100.0


def spacing_factor(n: float) -> float:
    """Barron drain-spacing factor F(n), without smear-zone effect."""
    if n <= 1:
        raise ValueError("ค่า n ต้องมากกว่า 1")
    n2 = n**2
    return (n2 / (n2 - 1.0)) * math.log(n) - ((3.0 * n2 - 1.0) / (4.0 * n2))


def radial_consolidation(Cr_cm2_day: float, t_day: float, de_cm: float, Fn: float):
    """Barron radial consolidation."""
    Tr = Cr_cm2_day * t_day / (de_cm**2)
    exp_term = math.exp(-8.0 * Tr / Fn)
    Ur = 1.0 - exp_term
    return Tr, exp_term, Ur


def vertical_consolidation(Cv_cm2_day: float, t_day: float, Hd_cm: float):
    """
    Terzaghi approximation used in the lecture:
    Uv = sqrt(4 Tv / pi), recommended for Uv <= 60%.
    """
    Tv = Cv_cm2_day * t_day / (Hd_cm**2)
    Uv = math.sqrt(max(0.0, 4.0 * Tv / math.pi))
    return Tv, min(Uv, 1.0)


def average_consolidation(Ur: float, Uv: float) -> float:
    """Carillo combined average consolidation."""
    return 1.0 - (1.0 - Ur) * (1.0 - Uv)


def calculate_row(
    spacing_m: float,
    pattern: str,
    a_cm: float,
    b_cm: float,
    dw_method: str,
    Cv_cm2_day: float,
    kh_kv_ratio: float,
    t_day: float,
    Hd_m: float,
):
    dw_cm = equivalent_diameter(a_cm, b_cm, dw_method)
    de_cm = influence_diameter(spacing_m, pattern)
    n = de_cm / dw_cm
    Fn = spacing_factor(n)
    Cr = kh_kv_ratio * Cv_cm2_day
    Tr, exp_term, Ur = radial_consolidation(Cr, t_day, de_cm, Fn)
    Tv, Uv = vertical_consolidation(Cv_cm2_day, t_day, Hd_m * 100.0)
    Uav = average_consolidation(Ur, Uv)

    return {
        "S (m)": spacing_m,
        "de (cm)": de_cm,
        "dw (cm)": dw_cm,
        "n": n,
        "F(n)": Fn,
        "Cr (cm²/day)": Cr,
        "Tr": Tr,
        "exp(-8Tr/Fn)": exp_term,
        "Ur (%)": Ur * 100.0,
        "Tv": Tv,
        "Uv (%)": Uv * 100.0,
        "Uav (%)": Uav * 100.0,
    }


# -----------------------------
# Sidebar inputs
# -----------------------------
with st.sidebar:
    st.header("ข้อมูลนำเข้า")

    pattern = st.selectbox(
        "รูปแบบการติดตั้ง PVD",
        ["สี่เหลี่ยมจัตุรัส", "สามเหลี่ยม"],
    )

    spacing_m = st.number_input(
        "ระยะห่าง PVD, S (m)",
        min_value=0.10,
        max_value=10.00,
        value=1.00,
        step=0.05,
    )

    st.subheader("ขนาดแผ่น PVD")
    b_mm = st.number_input(
        "ความกว้าง b (mm)",
        min_value=1.0,
        value=100.0,
        step=1.0,
    )
    a_mm = st.number_input(
        "ความหนา a (mm)",
        min_value=0.1,
        value=5.0,
        step=0.5,
    )
    dw_method = st.radio(
        "วิธีหาเส้นผ่านศูนย์กลางสมมูล dw",
        ["Rixner", "Hansbo"],
        horizontal=True,
    )

    st.subheader("คุณสมบัติดินและเวลา")
    Cv = st.number_input(
        "Cv (cm²/day)",
        min_value=0.0001,
        value=20.0,
        step=1.0,
        format="%.4f",
    )
    kh_kv = st.number_input(
        "อัตราส่วน kh/kv",
        min_value=0.01,
        value=7.0,
        step=0.5,
    )
    t_day = st.number_input(
        "เวลา t (day)",
        min_value=0.01,
        value=90.0,
        step=1.0,
    )
    soil_thickness_m = st.number_input(
        "ความหนาชั้นดินอ่อน H (m)",
        min_value=0.10,
        value=30.0,
        step=1.0,
    )
    drainage = st.radio(
        "สภาพการระบายน้ำแนวดิ่ง",
        ["ระบายสองทาง", "ระบายทางเดียว"],
    )

    target_percent = st.number_input(
        "เป้าหมาย Uav (%)",
        min_value=1.0,
        max_value=100.0,
        value=90.0,
        step=1.0,
    )

Hd_m = soil_thickness_m / 2.0 if drainage == "ระบายสองทาง" else soil_thickness_m
a_cm = a_mm / 10.0
b_cm = b_mm / 10.0

# -----------------------------
# Main result
# -----------------------------
try:
    result = calculate_row(
        spacing_m=spacing_m,
        pattern=pattern,
        a_cm=a_cm,
        b_cm=b_cm,
        dw_method=dw_method,
        Cv_cm2_day=Cv,
        kh_kv_ratio=kh_kv,
        t_day=t_day,
        Hd_m=Hd_m,
    )
except ValueError as exc:
    st.error(str(exc))
    st.stop()

st.subheader("ผลการคำนวณ")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Ur แนวรัศมี", f"{result['Ur (%)']:.2f}%")
c2.metric("Uv แนวดิ่ง", f"{result['Uv (%)']:.2f}%")
c3.metric("Uav เฉลี่ย", f"{result['Uav (%)']:.2f}%")
c4.metric(
    "ผลตรวจสอบ",
    "ผ่าน" if result["Uav (%)"] >= target_percent else "ไม่ผ่าน",
    f"เป้าหมาย {target_percent:.0f}%",
)

if result["Uv (%)"] > 60:
    st.warning(
        "ค่า Uv มากกว่า 60% ซึ่งอยู่นอกช่วงแนะนำของสมการประมาณ "
        "Uv = √(4Tv/π) ที่ใช้ในเอกสารประกอบการสอน"
    )

if result["Uav (%)"] >= target_percent:
    st.success(
        f"ระยะห่าง S = {spacing_m:.2f} m ให้ Uav = "
        f"{result['Uav (%)']:.2f}% ซึ่งผ่านเกณฑ์"
    )
else:
    st.error(
        f"ระยะห่าง S = {spacing_m:.2f} m ให้ Uav = "
        f"{result['Uav (%)']:.2f}% ซึ่งยังไม่ถึงเกณฑ์"
    )

detail_df = pd.DataFrame(
    {
        "รายการ": [
            "เส้นผ่านศูนย์กลางอิทธิพล de",
            "เส้นผ่านศูนย์กลางสมมูล dw",
            "อัตราส่วน n = de/dw",
            "Drain spacing factor F(n)",
            "Cr = (kh/kv)Cv",
            "Time factor แนวรัศมี Tr",
            "Time factor แนวดิ่ง Tv",
            "ระยะระบายน้ำไกลสุด Hd",
        ],
        "ค่า": [
            f"{result['de (cm)']:.3f} cm",
            f"{result['dw (cm)']:.3f} cm",
            f"{result['n']:.4f}",
            f"{result['F(n)']:.4f}",
            f"{result['Cr (cm²/day)']:.3f} cm²/day",
            f"{result['Tr']:.6f}",
            f"{result['Tv']:.6f}",
            f"{Hd_m:.3f} m",
        ],
    }
)
st.dataframe(detail_df, use_container_width=True, hide_index=True)

with st.expander("แสดงสมการที่ใช้"):
    st.latex(r"d_e = 1.13S \quad \mathrm{(square)}")
    st.latex(r"d_e = 1.05S \quad \mathrm{(triangular)}")
    st.latex(r"d_w = \frac{a+b}{2} \quad \mathrm{(Rixner)}")
    st.latex(r"d_w = \frac{2(a+b)}{\pi} \quad \mathrm{(Hansbo)}")
    st.latex(r"n = \frac{d_e}{d_w}")
    st.latex(
        r"F(n)=\frac{n^2}{n^2-1}\ln(n)-\frac{3n^2-1}{4n^2}"
    )
    st.latex(r"C_r=\left(\frac{k_h}{k_v}\right)C_v")
    st.latex(r"T_r=\frac{C_rt}{d_e^2}")
    st.latex(r"U_r=1-\exp\left(\frac{-8T_r}{F(n)}\right)")
    st.latex(r"T_v=\frac{C_vt}{H_d^2}")
    st.latex(r"U_v=\frac{\sqrt{4T_v}}{\pi}")
    st.latex(r"U_{av}=1-(1-U_r)(1-U_v)")

# -----------------------------
# Settlement calculator
# -----------------------------
st.divider()
st.subheader("คำนวณการทรุดตัว ณ เวลา t")

enable_settlement = st.checkbox("มีค่า Ultimate Settlement (Sfinal)")
if enable_settlement:
    Sfinal_m = st.number_input(
        "Ultimate Settlement, Sfinal (m)",
        min_value=0.0,
        value=1.0,
        step=0.05,
    )
    St_m = result["Uav (%)"] / 100.0 * Sfinal_m
    s1, s2 = st.columns(2)
    s1.metric("Sfinal", f"{Sfinal_m:.4f} m")
    s2.metric("Settlement ณ เวลา t", f"{St_m:.4f} m")
    st.latex(r"S_t=U_{av}\times S_{final}")

# -----------------------------
# Spacing comparison
# -----------------------------
st.divider()
st.subheader("ตารางเปรียบเทียบระยะห่าง PVD")

col_a, col_b, col_c = st.columns(3)
with col_a:
    s_min = st.number_input(
        "S เริ่มต้น (m)", min_value=0.10, value=0.60, step=0.05
    )
with col_b:
    s_max = st.number_input(
        "S สิ้นสุด (m)", min_value=0.10, value=1.50, step=0.05
    )
with col_c:
    s_step = st.number_input(
        "ช่วงเพิ่ม S (m)", min_value=0.01, value=0.10, step=0.01
    )

if s_max < s_min:
    st.error("S สิ้นสุดต้องไม่น้อยกว่า S เริ่มต้น")
else:
    spacings = []
    current = s_min
    while current <= s_max + 1e-9:
        spacings.append(round(current, 6))
        current += s_step

    rows = [
        calculate_row(
            spacing_m=s,
            pattern=pattern,
            a_cm=a_cm,
            b_cm=b_cm,
            dw_method=dw_method,
            Cv_cm2_day=Cv,
            kh_kv_ratio=kh_kv,
            t_day=t_day,
            Hd_m=Hd_m,
        )
        for s in spacings
    ]
    comparison_df = pd.DataFrame(rows)
    comparison_df["ผ่านเกณฑ์"] = comparison_df["Uav (%)"] >= target_percent

    display_columns = [
        "S (m)",
        "de (cm)",
        "dw (cm)",
        "n",
        "F(n)",
        "Tr",
        "Ur (%)",
        "Tv",
        "Uv (%)",
        "Uav (%)",
        "ผ่านเกณฑ์",
    ]
    st.dataframe(
        comparison_df[display_columns].style.format(
            {
                "S (m)": "{:.2f}",
                "de (cm)": "{:.2f}",
                "dw (cm)": "{:.2f}",
                "n": "{:.3f}",
                "F(n)": "{:.3f}",
                "Tr": "{:.5f}",
                "Ur (%)": "{:.2f}",
                "Tv": "{:.6f}",
                "Uv (%)": "{:.2f}",
                "Uav (%)": "{:.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    chart_df = comparison_df.set_index("S (m)")[
        ["Ur (%)", "Uv (%)", "Uav (%)"]
    ]
    st.line_chart(chart_df)

    passed = comparison_df[comparison_df["ผ่านเกณฑ์"]]
    if not passed.empty:
        max_spacing = passed["S (m)"].max()
        st.info(
            f"จากช่วงที่ทดลอง ระยะห่างมากที่สุดที่ยังผ่านเกณฑ์ "
            f"{target_percent:.0f}% คือประมาณ {max_spacing:.2f} m"
        )
    else:
        st.warning("ไม่มีระยะห่างในช่วงที่ทดลองผ่านเกณฑ์ที่กำหนด")

    csv_data = comparison_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "ดาวน์โหลดตารางผลคำนวณ CSV",
        data=csv_data,
        file_name="pvd_spacing_results.csv",
        mime="text/csv",
    )

st.divider()
st.caption(
    "หมายเหตุ: โปรแกรมนี้ทำตามสมการในเอกสารประกอบการสอน "
    "และยังไม่รวมผลของ smear zone, well resistance และข้อจำกัดเฉพาะโครงการ "
    "จึงควรให้วิศวกรปฐพีกลศาสตร์ตรวจสอบก่อนใช้ในการออกแบบจริง"
)
