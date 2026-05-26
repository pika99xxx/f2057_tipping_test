import streamlit as st

st.set_page_config(
    page_title="F2057 防倾倒测试预判工具",
    layout="wide"
)

st.title("柜类产品 F2057 防倾倒测试预判工具")
st.warning("本工具仅用于设计阶段预判，不能替代正式实验室测试。")


def calc_board_weight(length_mm, width_mm, thickness_mm, density_kg_m3):
    volume_m3 = length_mm * width_mm * thickness_mm / 1_000_000_000
    return volume_m3 * density_kg_m3


def calc_frame_weight(outer_length, outer_width, frame_width, thickness, density):
    inner_length = max(0, outer_length - 2 * frame_width)
    inner_width = max(0, outer_width - 2 * frame_width)

    outer_weight = calc_board_weight(outer_length, outer_width, thickness, density)
    inner_weight = calc_board_weight(inner_length, inner_width, thickness, density)

    return max(0, outer_weight - inner_weight)


# =========================
# 1. 产品基础信息
# =========================

st.header("1. 产品基础信息")

product_name = st.text_input("产品名称", value="五斗柜")

col1, col2, col3 = st.columns(3)

with col1:
    width = st.number_input("柜体外宽 mm", min_value=1.0, value=800.0)

with col2:
    depth = st.number_input("柜体外深 mm", min_value=1.0, value=400.0)

with col3:
    height = st.number_input("柜体外高 mm", min_value=1.0, value=1000.0)

safety_factor = st.number_input(
    "安全系数",
    min_value=1.0,
    value=1.2,
    step=0.1
)

closed_volume_dm3 = width * depth * height / 1_000_000
st.write(f"封闭存储体积约为：**{closed_volume_dm3:.2f} dm³**")


# =========================
# 2. 板件重量自动计算
# =========================

st.header("2. 板件重量自动计算")

material_density_map = {
    "PB板": 675,
    "MDF板-柜体/横条/门板/抽面/抽盒": 725,
    "MDF板-吸塑门板": 770,
    "MDF板-背板/抽屉底板": 700,
}

main_material = st.selectbox(
    "柜体主材料",
    ["PB板", "MDF板-柜体/横条/门板/抽面/抽盒"],
    index=0
)

density = material_density_map[main_material]

door_material = st.selectbox(
    "门板/抽面材料",
    [
        "同柜体主材料",
        "MDF板-柜体/横条/门板/抽面/抽盒",
        "MDF板-吸塑门板"
    ],
    index=0
)

if door_material == "同柜体主材料":
    door_density = density
else:
    door_density = material_density_map[door_material]

back_bottom_density = material_density_map["MDF板-背板/抽屉底板"]

st.write(f"柜体主材料密度：**{density} kg/m³**")
st.write(f"门板/抽面材料密度：**{door_density} kg/m³**")
st.write(f"背板/抽屉底板密度：**{back_bottom_density} kg/m³**")

col1, col2, col3, col4 = st.columns(4)

with col1:
    board_thickness = st.number_input("主体板厚 mm", min_value=1.0, value=15.0)

with col2:
    back_panel_thickness = st.number_input("背板厚度 mm", min_value=1.0, value=3.0)

with col3:
    drawer_panel_thickness = st.number_input("抽面板厚度 mm", min_value=1.0, value=15.0)

with col4:
    drawer_box_thickness = st.number_input("抽盒侧/后板厚度 mm", min_value=1.0, value=12.0)

bottom_frame_enabled = st.checkbox("底板是否使用加厚框", value=False)

bottom_frame_weight = 0

if bottom_frame_enabled:
    bottom_frame_width = st.number_input(
        "底板加厚框宽度 mm",
        min_value=45.0,
        max_value=60.0,
        value=50.0
    )

    bottom_frame_weight = calc_frame_weight(
        outer_length=width,
        outer_width=depth,
        frame_width=bottom_frame_width,
        thickness=board_thickness,
        density=density
    )

back_panel_width = max(0, width - 24)
back_panel_height = max(0, height - 1)

top_panel_weight = calc_board_weight(width, depth, board_thickness, density)
bottom_panel_weight = calc_board_weight(width, depth, board_thickness, density)
left_side_weight = calc_board_weight(height, depth, board_thickness, density)
right_side_weight = calc_board_weight(height, depth, board_thickness, density)

back_panel_weight = calc_board_weight(
    back_panel_width,
    back_panel_height,
    back_panel_thickness,
    back_bottom_density
)

basic_cabinet_weight = (
    top_panel_weight
    + bottom_panel_weight
    + left_side_weight
    + right_side_weight
    + back_panel_weight
    + bottom_frame_weight
)

st.subheader("基础柜体重量明细")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("顶板重量", f"{top_panel_weight:.2f} kg")
    st.metric("底板重量", f"{bottom_panel_weight:.2f} kg")

with col2:
    st.metric("左侧板重量", f"{left_side_weight:.2f} kg")
    st.metric("右侧板重量", f"{right_side_weight:.2f} kg")

with col3:
    st.metric("背板重量", f"{back_panel_weight:.2f} kg")
    st.metric("底板加厚框重量", f"{bottom_frame_weight:.2f} kg")

st.write(f"背板计算尺寸：**{back_panel_width:.0f} × {back_panel_height:.0f} × {back_panel_thickness:.0f} mm**")


# =========================
# 3. 抽屉重量计算
# =========================

st.header("3. 抽屉重量计算")

drawer_type = st.selectbox(
    "抽面形式",
    ["内嵌抽面", "外盖抽面"],
    index=0
)

drawer_count = st.number_input(
    "抽屉数量",
    min_value=0,
    max_value=20,
    value=3,
    step=1
)

total_drawer_structure_weight = 0.0
total_loaded_weight = 0.0

for i in range(int(drawer_count)):
    st.subheader(f"抽屉 {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        drawer_outer_width = st.number_input(
            f"抽屉 {i + 1} 外框宽度 mm",
            min_value=1.0,
            value=width - 30,
            key=f"drawer_outer_width_{i}"
        )

    with col2:
        drawer_outer_height = st.number_input(
            f"抽屉 {i + 1} 外框高度 mm",
            min_value=1.0,
            value=160.0,
            key=f"drawer_outer_height_{i}"
        )

    with col3:
        drawer_inner_depth = st.number_input(
            f"抽屉 {i + 1} 内深 mm",
            min_value=1.0,
            value=300.0,
            key=f"drawer_inner_depth_{i}"
        )

    if drawer_type == "内嵌抽面":
        drawer_front_width = max(0, drawer_outer_width - 6)
        drawer_front_height = max(0, drawer_outer_height - 6)
    else:
        drawer_front_width = max(0, drawer_outer_width - 2)
        drawer_front_height = max(0, drawer_outer_height - 3)

    drawer_inner_width = max(0, drawer_front_width - 2 * drawer_box_thickness)
    drawer_box_height = max(0, drawer_front_height - 30)

    drawer_front_weight = calc_board_weight(
        drawer_front_width,
        drawer_front_height,
        drawer_panel_thickness,
        door_density
    )

    drawer_back_weight = calc_board_weight(
        drawer_inner_width,
        drawer_box_height,
        drawer_box_thickness,
        density
    )

    drawer_left_weight = calc_board_weight(
        drawer_inner_depth,
        drawer_box_height,
        drawer_box_thickness,
        density
    )

    drawer_right_weight = calc_board_weight(
        drawer_inner_depth,
        drawer_box_height,
        drawer_box_thickness,
        density
    )

    drawer_bottom_weight = calc_board_weight(
        drawer_inner_width,
        drawer_inner_depth,
        3,
        back_bottom_density
    )

    single_drawer_structure_weight = (
        drawer_front_weight
        + drawer_back_weight
        + drawer_left_weight
        + drawer_right_weight
        + drawer_bottom_weight
    )

    drawer_volume_dm3 = (
        drawer_inner_width
        * drawer_inner_depth
        * drawer_box_height
        / 1_000_000
    )

    loaded_weight = drawer_volume_dm3 * 0.136

    total_drawer_structure_weight += single_drawer_structure_weight
    total_loaded_weight += loaded_weight

    st.write(f"抽面计算尺寸：**{drawer_front_width:.0f} × {drawer_front_height:.0f} mm**")
    st.write(f"抽盒内宽：**{drawer_inner_width:.0f} mm**")
    st.write(f"抽盒高度：**{drawer_box_height:.0f} mm**")
    st.write(f"抽面重量：**{drawer_front_weight:.2f} kg**")
    st.write(f"抽后板重量：**{drawer_back_weight:.2f} kg**")
    st.write(f"抽左侧板重量：**{drawer_left_weight:.2f} kg**")
    st.write(f"抽右侧板重量：**{drawer_right_weight:.2f} kg**")
    st.write(f"抽底板重量：**{drawer_bottom_weight:.2f} kg**")
    st.write(f"该抽屉结构总重量：**{single_drawer_structure_weight:.2f} kg**")
    st.write(f"该抽屉模拟衣服荷重：**{loaded_weight:.2f} kg**")


# =========================
# 4. 门板重量计算
# =========================

st.header("4. 门板重量计算")

door_enabled = st.checkbox("是否有门板", value=False)

total_door_weight = 0.0

if door_enabled:
    door_type = st.selectbox(
        "门板形式",
        ["内嵌门板", "外盖门板"],
        index=0
    )

    door_count = st.number_input(
        "门板数量",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )

    for i in range(int(door_count)):
        st.subheader(f"门板 {i + 1}")

        col1, col2 = st.columns(2)

        with col1:
            door_outer_width = st.number_input(
                f"门板 {i + 1} 外框宽度 mm",
                min_value=1.0,
                value=380.0,
                key=f"door_outer_width_{i}"
            )

        with col2:
            door_outer_height = st.number_input(
                f"门板 {i + 1} 外框高度 mm",
                min_value=1.0,
                value=600.0,
                key=f"door_outer_height_{i}"
            )

        if door_type == "内嵌门板":
            door_width = max(0, door_outer_width - 6)
            door_height = max(0, door_outer_height - 6)
        else:
            door_width = max(0, door_outer_width - 2)
            door_height = max(0, door_outer_height - 3)

        door_weight = calc_board_weight(
            door_width,
            door_height,
            board_thickness,
            door_density
        )

        total_door_weight += door_weight

        st.write(f"门板计算尺寸：**{door_width:.0f} × {door_height:.0f} mm**")
        st.write(f"门板重量：**{door_weight:.2f} kg**")


# =========================
# 5. 五金与额外重量
# =========================

st.header("5. 五金与额外重量")

col1, col2 = st.columns(2)

with col1:
    hardware_weight = st.number_input(
        "五金/滑轨/拉手/脚垫预估重量 kg",
        min_value=0.0,
        value=2.0
    )

with col2:
    extra_bottom_weight = st.number_input(
        "底部额外配重 kg",
        min_value=0.0,
        value=0.0
    )


weight = (
    basic_cabinet_weight
    + total_drawer_structure_weight
    + total_door_weight
    + hardware_weight
    + extra_bottom_weight
)

st.header("6. 整柜重量汇总")

st.metric("自动估算整柜重量", f"{weight:.2f} kg")

st.write(f"""
重量组成：
- 基础柜体板件：{basic_cabinet_weight:.2f} kg
- 抽屉结构：{total_drawer_structure_weight:.2f} kg
- 门板结构：{total_door_weight:.2f} kg
- 五金/滑轨/拉手/脚垫：{hardware_weight:.2f} kg
- 底部额外配重：{extra_bottom_weight:.2f} kg
""")


# =========================
# 7. F2057 适用性判断
# =========================

st.header("7. 是否属于 F2057 测试范围")

is_height_ok = height >= 686
is_weight_ok = weight >= 13.6
is_volume_ok = closed_volume_dm3 >= 90.6

is_f2057_applicable = is_height_ok and is_weight_ok and is_volume_ok

col1, col2, col3 = st.columns(3)

with col1:
    st.write("高度 ≥ 686mm：", "✅ 是" if is_height_ok else "❌ 否")

with col2:
    st.write("重量 ≥ 13.6kg：", "✅ 是" if is_weight_ok else "❌ 否")

with col3:
    st.write("封闭存储体积 ≥ 90.6dm³：", "✅ 是" if is_volume_ok else "❌ 否")

if is_f2057_applicable:
    st.error("该产品属于 ASTM F2057-23 衣物储存柜测试范围，需要进行防倾倒测试。")
else:
    st.success("该产品可能不属于 ASTM F2057-23 强制测试范围，但仍建议做稳定性风险评估。")


# =========================
# 8. 水平动态力测试
# =========================

st.header("8. 模拟水平动态力测试")

force_n = 44
force_height = min(height, 1422)

gravity_n = weight * 9.8
half_depth_m = depth / 2 / 1000

overturn_moment = force_n * (force_height / 1000)
resisting_moment = gravity_n * half_depth_m

horizontal_pass = resisting_moment >= overturn_moment * safety_factor

st.write(f"倾覆力矩：**{overturn_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")
st.write(f"考虑安全系数后的所需抗倾覆力矩：**{overturn_moment * safety_factor:.2f} N·m**")

if horizontal_pass:
    st.success("水平动态力测试预判：风险较低")
else:
    st.error("水平动态力测试预判：风险较高，柜体可能倾倒")


# =========================
# 9. 儿童荷重测试
# =========================

st.header("9. 模拟地毯上儿童体重反应测试")

child_weight = 27.22
child_force_n = child_weight * 9.8

drawer_extension = st.number_input(
    "最危险抽屉拉出距离 mm",
    min_value=0.0,
    value=300.0
)

child_overturn_moment = child_force_n * (drawer_extension / 1000)
child_pass = resisting_moment >= child_overturn_moment * safety_factor

st.write(f"儿童荷重造成的倾覆力矩：**{child_overturn_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")
st.write(f"考虑安全系数后的所需抗倾覆力矩：**{child_overturn_moment * safety_factor:.2f} N·m**")

if child_pass:
    st.success("儿童荷重测试预判：风险较低")
else:
    st.error("儿童荷重测试预判：风险较高，柜体可能倾倒")


# =========================
# 10. 综合判断与优化建议
# =========================

st.header("10. 综合判断与精确优化建议")

required_moment = max(
    overturn_moment * safety_factor,
    child_overturn_moment * safety_factor
)

required_depth_m = required_moment / gravity_n * 2
required_depth_mm = required_depth_m * 1000
extra_depth_mm = max(0, required_depth_mm - depth)

required_weight_kg = required_moment / (9.8 * half_depth_m)
extra_weight_kg = max(0, required_weight_kg - weight)

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

st.subheader("优化建议")

if resisting_moment >= required_moment:
    st.success("当前参数下，按安全系数计算，稳定性余量基本足够。")
else:
    st.write(f"柜体深度至少增加约 **{extra_depth_mm:.0f} mm**")
    st.write(f"建议深度：**{required_depth_mm:.0f} mm 以上**")

    st.write(f"整柜重量至少增加约 **{extra_weight_kg:.1f} kg**")
    st.write(f"建议重量：**{required_weight_kg:.1f} kg 以上**")

    st.write(f"建议优先把新增重量放在柜体底部，当前建议底部增重约 **{extra_weight_kg:.1f} kg**。")


# =========================
# 11. 报告下载
# =========================

st.header("11. 测试预判报告摘要")

report = f"""
产品名称：{product_name}

柜体尺寸：
- 宽度：{width:.0f} mm
- 深度：{depth:.0f} mm
- 高度：{height:.0f} mm
- 封闭存储体积：{closed_volume_dm3:.2f} dm³

材料密度：
- 柜体主材料：{main_material}，{density} kg/m³
- 门板/抽面材料：{door_material}，{door_density} kg/m³
- 背板/抽屉底板：MDF板-背板/抽屉底板，{back_bottom_density} kg/m³

板件重量：
- 顶板：{top_panel_weight:.2f} kg
- 底板：{bottom_panel_weight:.2f} kg
- 左侧板：{left_side_weight:.2f} kg
- 右侧板：{right_side_weight:.2f} kg
- 背板：{back_panel_weight:.2f} kg
- 底板加厚框：{bottom_frame_weight:.2f} kg
- 抽屉结构：{total_drawer_structure_weight:.2f} kg
- 门板结构：{total_door_weight:.2f} kg
- 五金：{hardware_weight:.2f} kg
- 底部额外配重：{extra_bottom_weight:.2f} kg

自动估算整柜重量：{weight:.2f} kg

F2057 适用性：
- 高度 ≥ 686mm：{"是" if is_height_ok else "否"}
- 重量 ≥ 13.6kg：{"是" if is_weight_ok else "否"}
- 封闭存储体积 ≥ 90.6dm³：{"是" if is_volume_ok else "否"}
- 是否属于测试范围：{"是" if is_f2057_applicable else "否"}

测试预判：
- 水平动态力测试：{"通过预判" if horizontal_pass else "风险较高"}
- 儿童荷重测试：{"通过预判" if child_pass else "风险较高"}
- 模拟衣服总荷重：{total_loaded_weight:.2f} kg

优化建议：
- 建议柜体深度：{required_depth_mm:.0f} mm 以上
- 需要增加深度：{extra_depth_mm:.0f} mm
- 建议整柜重量：{required_weight_kg:.1f} kg 以上
- 需要底部增重：{extra_weight_kg:.1f} kg

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
