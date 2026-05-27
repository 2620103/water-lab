import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물의 상태 변화 실험실", page_icon="💧", layout="centered")

st.title("💧 물의 가열 곡선 및 상태 변화 가상 실험실")
st.markdown("""
이 실험실에서는 얼음에 열에너지를 공급할 때 온도가 어떻게 변하는지 관찰할 수 있습니다.
상태가 변하는 구간(**0°C 융해 구간**, **100°C 기화 구간**)에서 온도가 일정하게 유지되는 현상을 눈으로 확인해 보세요!
""")

st.divider()

# --- 사이드바: 조작 패널 ---
st.sidebar.header("🎛️ 실험 조작 패널")

# 1. 물의 질량 (g)
mass = st.sidebar.slider("물의 질량 (g)", min_value=10, max_value=100, value=50, step=10)

# 2. 공급한 열에너지 (kJ)
# 질량에 따라 필요한 최대 에너지가 달라지므로 유동적으로 맥스값 설정
max_energy = int(mass * 3.0)  
energy = st.sidebar.slider("공급한 열에너지 (kJ)", min_value=0.0, max_value=float(max_energy), value=0.0, step=1.0)

# --- 물의 물리적 상수 (단위: J/g 또는 J/g°C) ---
c_ice = 2.09       # 얼음의 비열
H_fusion = 334     # 융해열 (얼음 -> 물)
c_water = 4.184    # 물의 비열
H_vap = 2260       # 기화열 (물 -> 수증기)
c_steam = 2.01     # 수증기의 비열

# --- 에너지에 따른 온도 및 상태 계산 함수 ---
def calc_temp_and_phase(e_total_kj, m):
    e_total = e_total_kj * 1000 # kJ -> J 변환
    
    # 각 구간별 한계 에너지 계산
    e1 = m * c_ice * 20                         # -20°C에서 0°C 얼음까지 필요한 에너지
    e2 = e1 + (m * H_fusion)                    # 0°C 얼음이 모두 녹을 때까지 필요한 에너지
    e3 = e2 + (m * c_water * 100)               # 0°C 물이 100°C 물이 될 때까지 필요한 에너지
    e4 = e3 + (m * H_vap)                       # 100°C 물이 모두 수증기가 될 때까지 필요한_에너지
    
    if e_total <= e1:
        temp = -20 + e_total / (m * c_ice)
        phase = "🧊 고체 (얼음)"
    elif e_total <= e2:
        temp = 0.0
        phase = "🧊+💧 고체와 액체의 공존 (얼음이 녹는 중)"
    elif e_total <= e3:
        temp = 0.0 + (e_total - e2) / (m * c_water)
        phase = "💧 액체 (물)"
    elif e_total <= e4:
        temp = 100.0
        phase = "💧+💨 액체와 기체의 공존 (물이 끓는 중)"
    else:
        temp = 100 + (e_total - e4) / (m * c_steam)
        phase = "💨 기체 (수증기)"
        
    return temp, phase, [e1/1000, e2/1000, e3/1000, e4/1000]

# 현재 상태 계산
current_temp, current_phase, milestones = calc_temp_and_phase(energy, mass)

# --- 결과 디스플레이 ---
col1, col2, col3 = st.columns(3)
col1.metric("⚖️ 물의 질량", f"{mass} g")
col2.metric("🔥 공급된 에너지", f"{energy} kJ")
col3.metric("🌡️ 현재 온도", f"{current_temp:.0f}°C" if current_temp == 0 or current_temp == 100 else f"{current_temp:.1f}°C")

# 현재 상태 시각적 알림
st.info(f"**현재 물질의 상태:** {current_phase}")

st.divider()

# --- 가열 곡선 그래프 그리기 ---
st.subheader("📈 물의 가열 곡선 그래프")

# 그래프용 데이터 포인트 생성
e_axis = np.linspace(0, max_energy, 500)
t_axis = [calc_temp_and_phase(e, mass)[0] for e in e_axis]

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(e_axis, t_axis, color="#4FC3F7", linewidth=2.5, label="Heating Curve")
# 현재 위치를 빨간 점으로 표시
ax.scatter(energy, current_temp, color="#E53935", s=120, zorder=5, label="Current Point")

# 그래프 주요 구간 텍스트 표시
ax.text(milestones[0]/2, -10, "Ice", fontsize=9, ha='center', color='gray')
ax.text((milestones[0]+milestones[1])/2, 8, "Melting", fontsize=9, ha='center', color='gray')
ax.text((milestones[1]+milestones[2])/2, 50, "Water", fontsize=9, ha='center', color='gray')
ax.text((milestones[2]+milestones[3])/2, 108, "Boiling", fontsize=9, ha='center', color='gray')

# 그래프 스타일링
ax.set_title("Water Heating Curve Simulation", fontsize=12, fontweight='bold')
ax.set_xlabel("Added Thermal Energy (kJ)", fontsize=10)
ax.set_ylabel("Temperature (°C)", fontsize=10)
ax.set_xlim(0, max_energy)
ax.set_ylim(-25, 130)
ax.axhline(0, color='black', linestyle='--', alpha=0.3)
ax.axhline(100, color='black', linestyle='--', alpha=0.3)
ax.grid(True, linestyle="--", alpha=0.5)
ax.legend()

st.pyplot(fig)

st.divider()

# --- 이론 설명 창 ---
with st.expander("📚 물의 가열 곡선 속 과학 원리"):
    st.markdown("""
    ### 💡 왜 에너지를 주는데 온도가 안 오르는 구간이 있나요?
    그래프를 보면 **0°C**와 **100°C**에서 수평 기어가는 구간이 있습니다. 이때 공급된 열에너지는 온도를 올리는 데 쓰이지 않고, **물질의 상태를 변화(분자 사이의 결합을 끊음)**시키는 데 전부 소모되기 때문입니다.
    
    * **융해열 (Heat of Fusion):** 0°C에서 얼음이 물로 변할 때 필요한 에너지입니다.
    * **기화열 (Heat of Vaporization):** 100°C에서 물이 수증기로 변할 때 필요한 에너지입니다. 물은 수소 결합을 하고 있어 기화열이 다른 물질에 비해 매우 큽니다.
    
    ### 🧪 열량 공식
    * **온도가 변할 때 (기울어진 구간):** $Q = m \cdot c \cdot \Delta T$ (열량 = 질량 × 비열 × 온도변화)
    * **상태가 변할 때 (평평한 구간):** $Q = m \cdot H$ (열량 = 질량 × 잠열)
    """)
