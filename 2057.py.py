import streamlit as st

st.set_page_config(
    page_title="F2057 防倾倒测试预判工具",
    layout="wide"
)

st.title("柜类产品 F2057 防倾倒测试预判工具")

st.warning("本工具仅用于设计阶段预判，不能替代正式实验室测试。")

# =========================
# 1. 产品基础信息
# =========================

st.header("1. 产品基础信息")

product_name = st.text_input("产品名称", value="五斗柜")

col1, col2, col3, col4 = st.columns(4)

with col1:
    width = st.number_input("柜体宽度 mm", min_value=1.0, value=800.0)

with col2:
    depth = st.number_input("柜体深度 mm", min_value=1.0, value=400.0)

with col3:
    height = st.number_input("柜体高度 mm", min_value=1.0, value=1000.0)

with col4:
    weight = st.number_input("整柜重量 kg", min_value=1.0, value=30.0)

safety_factor = st.number_input(
    "安全系数",
    min_value=1.0,
    value=1.2,
    step=0.1
)

closed_volume_dm3 = width * depth * height / 1_000_000

st.write(f"封闭存储体积约为：**{closed_volume_dm3:.2f} dm³**")

# =========================
# 2. F2057 适用性判断
# =========================

st.header("2. 是否属于 F2057 测试范围")

is_height_ok = height >= 686
is_weight_ok = weight >= 13.6
is_volume_ok = closed_volume_dm3 >= 90.6

col1, col2, col3 = st.columns(3)

with col1:
    st.write("高度 ≥ 686mm：", "✅ 是" if is_height_ok else "❌ 否")

with col2:
    st.write("重量 ≥ 13.6kg：", "✅ 是" if is_weight_ok else "❌ 否")

with col3:
    st.write("封闭存储体积 ≥ 90.6dm³：", "✅ 是" if is_volume_ok else "❌ 否")

is_f2057_applicable = is_height_ok and is_weight_ok and is_volume_ok

if is_f2057_applicable:
    st.error("该产品属于 ASTM F2057-23 衣物储存柜测试范围，需要进行防倾倒测试。")
else:
    st.success("该产品可能不属于 ASTM F2057-23 强制测试范围，但仍建议做稳定性风险评估。")

# =========================
# 3. 水平动态力测试
# =========================

st.header("3. 模拟水平动态力测试")

force_n = 44
force_height = min(height, 1422)

gravity_n = weight * 9.8
half_depth_m = depth / 2 / 1000

overturn_moment = force_n * (force_height / 1000)
resisting_moment = gravity_n * half_depth_m

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("水平拉力", f"{force_n} N")

with col2:
    st.metric("施力高度", f"{force_height:.0f} mm")

with col3:
    st.metric("安全系数", f"{safety_factor:.1f}")

st.write(f"倾覆力矩：**{overturn_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")
st.write(f"考虑安全系数后的所需抗倾覆力矩：**{overturn_moment * safety_factor:.2f} N·m**")

horizontal_pass = resisting_moment >= overturn_moment * safety_factor

if horizontal_pass:
    st.success("水平动态力测试预判：风险较低")
else:
    st.error("水平动态力测试预判：风险较高，柜体可能倾倒")

# =========================
# 4. 模拟衣服荷重测试
# =========================

st.header("4. 模拟衣服荷重测试")

drawer_count = st.number_input(
    "抽屉数量",
    min_value=0,
    max_value=20,
    value=3,
    step=1
)

total_loaded_weight = 0.0
drawer_data = []

for i in range(int(drawer_count)):
    st.subheader(f"抽屉 {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        dw = st.number_input(
            f"抽屉 {i + 1} 内宽 mm",
            min_value=1.0,
            value=700.0,
            key=f"dw_{i}"
        )

    with col2:
        dd = st.number_input(
            f"抽屉 {i + 1} 内深 mm",
            min_value=1.0,
            value=300.0,
            key=f"dd_{i}"
        )

    with col3:
        dh = st.number_input(
            f"抽屉 {i + 1} 内高 mm",
            min_value=1.0,
            value=120.0,
            key=f"dh_{i}"
        )

    drawer_volume_dm3 = dw * dd * dh / 1_000_000
    loaded_weight = drawer_volume_dm3 * 0.136

    total_loaded_weight += loaded_weight

    drawer_data.append({
        "index": i + 1,
        "width": dw,
        "depth": dd,
        "height": dh,
        "volume_dm3": drawer_volume_dm3,
        "loaded_weight": loaded_weight
    })

    st.write(f"该抽屉体积：**{drawer_volume_dm3:.2f} dm³**")
    st.write(f"该抽屉模拟衣服荷重：**{loaded_weight:.2f} kg**")

st.write(f"所有抽屉模拟衣服总荷重：**{total_loaded_weight:.2f} kg**")

if total_loaded_weight > weight * 0.3:
    st.warning("模拟衣服荷重相对整柜重量较大，建议关注抽屉全部打开后的稳定性。")
else:
    st.success("模拟衣服荷重占比较低。")

# =========================
# 5. 儿童荷重测试
# =========================

st.header("5. 模拟地毯上儿童体重反应测试")

child_weight = 27.22
child_force_n = child_weight * 9.8

drawer_extension = st.number_input(
    "最危险抽屉拉出距离 mm",
    min_value=0.0,
    value=300.0
)

child_overturn_moment = child_force_n * (drawer_extension / 1000)
child_resisting_moment = resisting_moment

st.write(f"儿童荷重：**{child_weight:.2f} kg**")
st.write(f"儿童荷重造成的倾覆力矩：**{child_overturn_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{child_resisting_moment:.2f} N·m**")
st.write(f"考虑安全系数后的所需抗倾覆力矩：**{child_overturn_moment * safety_factor:.2f} N·m**")

child_pass = child_resisting_moment >= child_overturn_moment * safety_factor

if child_pass:
    st.success("儿童荷重测试预判：风险较低")
else:
    st.error("儿童荷重测试预判：风险较高，柜体可能倾倒")

# =========================
# 6. 精确优化建议计算
# =========================

st.header("6. 综合判断与精确优化建议")

required_moment_horizontal = overturn_moment * safety_factor
required_moment_child = child_overturn_moment * safety_factor
required_moment = max(required_moment_horizontal, required_moment_child)

current_resisting_moment = resisting_moment

required_depth_m = required_moment / gravity_n * 2
required_depth_mm = required_depth_m * 1000
extra_depth_mm = max(0, required_depth_mm - depth)

required_weight_kg = required_moment / (9.8 * half_depth_m)
extra_weight_kg = max(0, required_weight_kg - weight)

max_drawer_extension_m = current_resisting_moment / (child_force_n * safety_factor)
max_drawer_extension_mm = max_drawer_extension_m * 1000
reduce_extension_mm = max(0, drawer_extension - max_drawer_extension_mm)

max_force_height_m = current_resisting_moment / (force_n * safety_factor)
max_force_height_mm = max_force_height_m * 1000
lower_force_height_mm = max(0, force_height - max_force_height_mm)

risk_points = []

if is_f2057_applicable:
    risk_points.append("属于 F2057 测试范围")

if not horizontal_pass:
    risk_points.append("水平动态力测试风险高")

if not child_pass:
    risk_points.append("儿童荷重测试风险高")

if total_loaded_weight > weight * 0.3:
    risk_points.append("抽屉模拟衣服荷重较大")

if len(risk_points) == 0:
    st.success("综合风险：低")
elif len(risk_points) <= 2:
    st.warning("综合风险：中")
else:
    st.error("综合风险：高")

st.subheader("风险点")

if risk_points:
    for item in risk_points:
        st.write(f"- {item}")
else:
    st.write("暂无明显高风险点。")

st.subheader("优化建议：精确估算")

if current_resisting_moment >= required_moment:
    st.success("当前参数下，按安全系数计算，稳定性余量基本足够。")
else:
    st.error("当前参数下，稳定性不足。以下方案任选一种或组合使用：")

    st.write(f"### 方案 1：增加柜体深度")
    st.write(f"柜体深度至少增加约 **{extra_depth_mm:.0f} mm**")
    st.write(f"当前深度：**{depth:.0f} mm**")
    st.write(f"建议深度：**{required_depth_mm:.0f} mm 以上**")

    st.write(f"### 方案 2：增加整柜重量")
    st.write(f"整柜重量至少增加约 **{extra_weight_kg:.1f} kg**")
    st.write(f"当前重量：**{weight:.1f} kg**")
    st.write(f"建议重量：**{required_weight_kg:.1f} kg 以上**")

    if reduce_extension_mm > 0:
        st.write(f"### 方案 3：限制抽屉拉出距离")
        st.write(f"最危险抽屉拉出距离至少减少约 **{reduce_extension_mm:.0f} mm**")
        st.write(f"当前拉出距离：**{drawer_extension:.0f} mm**")
        st.write(f"建议最大拉出距离：**{max_drawer_extension_mm:.0f} mm 以内**")

    if lower_force_height_mm > 0:
        st.write(f"### 方案 4：降低水平拉力作用点")
        st.write(f"水平拉力作用点高度至少降低约 **{lower_force_height_mm:.0f} mm**")
        st.write(f"当前施力高度：**{force_height:.0f} mm**")
        st.write(f"建议施力高度：**{max_force_height_mm:.0f} mm 以下**")

    st.write("### 方案 5：组合优化")
    st.write("建议优先组合使用：增加柜深、增加底部配重、限制抽屉最大拉出距离、降低高位抽屉或门板拉手位置。")

# =========================
# 7. 报告摘要
# =========================

st.header("7. 测试预判报告摘要")

report = f"""
产品名称：{product_name}

柜体尺寸：
- 宽度：{width:.0f} mm
- 深度：{depth:.0f} mm
- 高度：{height:.0f} mm
- 重量：{weight:.1f} kg
- 封闭存储体积：{closed_volume_dm3:.2f} dm³

F2057 适用性：
- 高度 ≥ 686mm：{"是" if is_height_ok else "否"}
- 重量 ≥ 13.6kg：{"是" if is_weight_ok else "否"}
- 封闭存储体积 ≥ 90.6dm³：{"是" if is_volume_ok else "否"}
- 是否属于测试范围：{"是" if is_f2057_applicable else "否"}

测试预判：
- 水平动态力测试：{"通过预判" if horizontal_pass else "风险较高"}
- 儿童荷重测试：{"通过预判" if child_pass else "风险较高"}
- 模拟衣服总荷重：{total_loaded_weight:.2f} kg

综合风险点：
{chr(10).join(["- " + item for item in risk_points]) if risk_points else "- 暂无明显高风险点"}

精确优化建议：
- 建议柜体深度：{required_depth_mm:.0f} mm 以上
- 需要增加深度：{extra_depth_mm:.0f} mm
- 建议整柜重量：{required_weight_kg:.1f} kg 以上
- 需要增加重量：{extra_weight_kg:.1f} kg
- 建议最大抽屉拉出距离：{max_drawer_extension_mm:.0f} mm 以内
- 需要减少抽屉拉出距离：{reduce_extension_mm:.0f} mm
- 建议水平拉力作用点高度：{max_force_height_mm:.0f} mm 以下
- 需要降低作用点高度：{lower_force_height_mm:.0f} mm

说明：
本结果仅用于设计阶段预判，不能替代 ASTM F2057-23 正式实验室测试。
"""

st.text_area("报告内容", report, height=500)

st.download_button(
    label="下载测试预判报告 TXT",
    data=report,
    file_name=f"{product_name}_F2057_测试预判报告.txt",
    mime="text/plain"
)