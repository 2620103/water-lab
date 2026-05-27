import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물 분자 배열 및 상태 변화 시뮬레이션", page_icon="💧", layout="centered")

# 나눔고딕 폰트 설정 (그래프 한글 깨짐 방지)
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

st.title("💧 물 분자 배열 및 상태 변화 시뮬레이션")
st.markdown("온도 조절 슬라이더를 움직여 **얼음, 물, 수증기** 속 분자들의 3D 배열과 움직임을 관찰해 보세요!")

st.divider()

# --- 사이드바 조작 ---
st.sidebar.header("🎛️ 실험 조작 패널")
temp_slider = st.sidebar.slider("온도 설정 (°C)", -20, 120, -5, 1)

# --- 상태 계산 로직 ---
def get_status_from_temp(t):
    if t <= 0:
        return "SOLID", "🧊 얼음 (고체)"
    elif t <= 100:
        return "LIQUID", "💧 물 (액체)"
    else:
        return "GAS", "💨 수증기 (기체)"

state_key, state_desc = get_status_from_temp(temp_slider)

# --- 결과 표시 ---
col1, col2 = st.columns(2)
col1.metric("🌡️ 현재 온도", f"{temp_slider} °C")
col2.info(f"**현재 물질의 상태:** {state_desc}")

st.divider()

# --- 3D 물 분자 배열 그리기 ---
st.subheader("🔬 3D 현미경으로 본 분자 배열")

# 매직 넘버: 분자 개수
num_molecules = 60

# 랜덤 씨드를 고정해서 온도가 바뀔 때 분자들이 갑자기 다른 위치로 순간이동하지 않도록 방지
np.random.seed(42)
base_x = np.random.rand(num_molecules) * 10
base_y = np.random.rand(num_molecules) * 10
base_z = np.random.rand(num_molecules) * 10

# 상태별 분자 배치 가공
if state_key == "SOLID":
    # 고체: 규칙적인 격자 모양에 가깝게 강제 정렬하고 미세한 진동만 추가
    grid_size = int(np.ceil(num_molecules ** (1/3)))
    _x, _y, _z = np.meshgrid(np.linspace(2, 8, grid_size), np.linspace(2, 8, grid_size), np.linspace(2, 8, grid_size))
    x = _x.flatten()[:num_molecules] + np.random.normal(0, 0.1, num_molecules)
    y = _y.flatten()[:num_molecules] + np.random.normal(0, 0.1, num_molecules)
    z = _z.flatten()[:num_molecules] + np.random.normal(0, 0.1, num_molecules)
    color = "#4FC3F7"  # 시원한 하늘색 (얼음)
    size = 150
elif state_key == "LIQUID":
    # 액체: 바닥 쪽에 불규칙하게 모여있음 (중력 효과 반영)
    x = base_x
    y = base_y
    z = base_z * 0.4 + np.random.normal(0, 0.2, num_molecules)  # 아래쪽에 찰랑거림
    color = "#2196F3"  # 파란색 (물)
    size = 120
else:
    # 기체: 사방으로 멀리 퍼지고 활발하게 날아다님
    x = np.random.rand(num_molecules) * 20 - 5
    y = np.random.rand(num_molecules) * 20 - 5
    z = np.random.rand(num_molecules) * 20 - 5
    color = "#B0BEC5"  # 흐릿한 회색 (수증기)
    size = 60

# Matplotlib 3D 그래프 그리기
fig = plt.figure(figsize=(8, 6))
ax = fig.add_subplot(111, projection='3d')  # 👈 오타 완벽 수정!

# 3D 공간에 분자들(점) 찍기
ax.scatter(x, y, z, s=size, c=color, edgecolors='white', alpha=0.8)

# 그래프 스타일 및 축 제한 (공간 고정)
ax.set_title(f"{state_desc} 내부의 3D 분자 구조", fontsize=12, fontweight='bold')
ax.set_xlim(-5, 15)
ax.set_ylim(-5, 15)
ax.set_zlim(-5, 15)
ax.set_xlabel("X축")
ax.set_ylabel("Y축")
ax.set_zlabel("Z축")

st.pyplot(fig)

st.divider()

# --- 중학생용 눈눈높이 설명 설명 ---
with st.expander("📖 중학생 눈높이 상태 변화 설명"):
    st.markdown(f"""
    ### 현재 상태: {state_desc}
    * **🧊 고체 (얼음):** 3D 스크린을 보세요! 분자들이 위아래, 좌우로 규칙적인 격자 모양을 이루며 예쁘게 모여있죠? 서로 꽉 붙잡고 있어서 제자리에서만 살짝 덜덜 떨고 있어요.
    * **💧 액체 (물):** 규칙적인 모양이 깨지고, 분자들이 아래쪽 바닥에 모여서 서로 미끄러지듯 움직이고 있어요. 자유롭게 다닐 수 있어서 '흐르는 성질'이 생깁니다.
    * **💨 기체 (수증기):** 분자들 사이의 거리가 엄청나게 멀어진 게 보이시나요? 서로 잡고 있던 손을 완전히 놓고 3D 공간 전체로 사방팔방 퍼져나갑니다!
    """)
