import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import streamlit.components.v1 as components
from mpl_toolkits.mplot3d import Axes3D

# --- 페이지 기본 설정 ---
st.set_page_config(page_title="물 분자 배열 및 상태 변화 시뮬레이션", page_icon="💧", layout="wide")

# 나눔고딕 폰트 설정 (그래프용)
plt.rc('font', family='NanumGothic')
plt.rcParams['axes.unicode_minus'] = False

st.title("💧 물 분자 배열 및 상태 변화 시뮬레이션")
st.markdown("온도를 조절하여 물, 얼음, 수증기 속 분자들의 배열과 움직임을 관찰하고, 각 상태의 특징을 3D 그림으로 확인해 보세요!")

# --- 사이드바 조작 ---
st.sidebar.header("🎛️ 실험 패널")
temp_slider = st.sidebar.slider("온도 (°C)", -20, 120, -5, 1)

# --- 상태 계산 로직 (간단한 모델) ---
def get_status_from_temp(t):
    if t <= 0:
        return "SOLID", "🧊 얼음 (고체)"
    elif t <= 100:
        return "LIQUID", "💧 물 (액체)"
    else:
        return "GAS", "💨 수증기 (기체)"

state_key, state_desc = get_status_from_temp(temp_slider)

# --- 결과 표시 ---
st.sidebar.markdown(f"**현재 온도:** {temp_slider:.1f}°C")
st.sidebar.info(f"**현재 상태:** {state_desc}")

# --- 3D 물 분자 배열 및 상태 그림 ---
st.subheader("🔬 물 분자 배열 및 상태 그림 (3D)")

# 3D 그래프 생성
fig = plt.figure(figsize=(10, 8))
ax = fig.add_撥bplot(111, project='3d')

# 분자 개수 및 좌표 설정 (예시)
num_molecules = 50
x = np.random.rand(num_molecules) * 10
y = np.random.rand(num_molecules) * 10
z = np.random.rand(num_molecules) * 10

# 분자 크기 설정 (온도에 따라 변화)
s = np.full(num_molecules, 100)
if state_key == "SOLID":
    s = s * 2  # 얼음 분자는 크기가 커짐 (예시)
elif state_key == "GAS":
    s = s / 2  # 수증기 분자는 크기가 작아짐 (예시)

# 분자 색상 설정 (온도에 따라 변화)
color = plt.cm.plasma(temp_slider / 140)  # 온도에 따라 색상 변화 (예시)

# 상태별 분자 움직임 (간단한 모델)
if state_key == "SOLID":
    # 고체: 제자리 진동 (예시)
    x += np.random.normal(0, 0.1, num_molecules)
    y += np.random.normal(0, 0.1, num_molecules)
    z += np.random.normal(0, 0.1, num_molecules)
elif state_key == "GAS":
    # 기체: 빠르게 움직임 (예시)
    x += np.random.normal(0, 1, num_molecules)
    y += np.random.normal(0, 1, num_molecules)
    z += np.random.normal(0, 1, num_molecules)

# 3D 산점도 그리기
scatter = ax.scatter(x, y, z, s=s, c=color, alpha=0.5)

# 축 라벨 및 타이틀 설정
ax.set_xlabel("X")
ax.set_ylabel("Y")
ax.set_zlabel("Z")
ax.set_title(f"{state_desc} 분자 배열 및 움직임")

# 스트림릿에 그래프 표시
st.pyplot(fig)

st.divider()

# --- 중학생용 설명 ---
with st.expander("📖 중학생 눈높이 상태 변화 설명"):
    st.markdown(f"""
    ### 현재 상태: {state_desc}
    * **🧊 고체 (얼음):** 위 그림을 보세요! 분자들이 규칙적으로 딱딱 붙어있죠? 제자리에서 **진동**만 하고 있어요. 얼음은 단단하고 모양이 변하지 않아요.
    * **💧 액체 (물):** 분자들이 서로 조금씩 떨어져서 **자유롭게 자리바꿈**을 해요. 그래서 흐를 수 있는 거예요. 물은 부피는 일정하지만 모양은 그릇에 따라 변해요.
    * **💨 기체 (수증기):** 분자들이 서로 아주 멀리 떨어져서 **엄청나게 빠른 속도**로 날아다녀요! 수증기는 모양과 부피가 일정하지 않고 공간을 가득 채워요.
    """)
