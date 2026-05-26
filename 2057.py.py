import streamlit as st

st.set_page_config(page_title="F2057 防倾倒测试预判工具", layout="wide")

st.title("柜类产品 F2057 防倾倒测试预判工具")
st.warning("本工具仅用于设计阶段预判，不能替代正式实验室测试。")


# =========================
# 工具函数
# =========================

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

safety_factor = st.number_input("安全系数", min_value=1.0, value=1.2, step=0.1)

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
    "玻璃": 2500,
}

main_material = st.selectbox(
    "柜体主材料",
    ["PB板", "MDF板-柜体/横条/门板/抽面/抽盒"],
    index=0
)

density = material_density_map[main_material]

door_material = st.selectbox(
    "门板/抽面默认材料",
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
glass_density = material_density_map["玻璃"]

st.write(f"柜体主材料密度：**{density} kg/m³**")
st.write(f"门板/抽面默认密度：**{door_density} kg/m³**")
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

bottom_frame_weight = 0.0

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
# 3. 抽屉重量与拉开风险
# =========================

st.header("3. 抽屉重量与拉开风险计算")

force_n = 44

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
drawer_data = []

for i in range(int(drawer_count)):
    st.subheader(f"抽屉 {i + 1}")

    col1, col2, col3, col4, col5 = st.columns(5)

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

    with col4:
        drawer_bottom_height = st.number_input(
            f"抽屉 {i + 1} 底边离地高度 mm",
            min_value=0.0,
            value=100.0 + i * 180,
            key=f"drawer_bottom_height_{i}"
        )

    with col5:
        drawer_extension = st.number_input(
            f"抽屉 {i + 1} 拉出距离 mm",
            min_value=0.0,
            value=300.0,
            key=f"drawer_extension_{i}"
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

    drawer_volume_dm3 = drawer_inner_width * drawer_inner_depth * drawer_box_height / 1_000_000
    loaded_weight = drawer_volume_dm3 * 0.136

    drawer_center_height = drawer_bottom_height + drawer_outer_height / 2
    drawer_total_moving_weight = single_drawer_structure_weight + loaded_weight

    drawer_open_moment = drawer_total_moving_weight * 9.8 * (drawer_extension / 1000)
    drawer_horizontal_moment = force_n * (drawer_center_height / 1000)

    total_drawer_structure_weight += single_drawer_structure_weight
    total_loaded_weight += loaded_weight

    drawer_data.append({
        "index": i + 1,
        "structure_weight": single_drawer_structure_weight,
        "loaded_weight": loaded_weight,
        "moving_weight": drawer_total_moving_weight,
        "bottom_height": drawer_bottom_height,
        "center_height": drawer_center_height,
        "extension": drawer_extension,
        "open_moment": drawer_open_moment,
        "horizontal_moment": drawer_horizontal_moment,
    })

    st.write(f"抽面计算尺寸：**{drawer_front_width:.0f} × {drawer_front_height:.0f} mm**")
    st.write(f"抽盒内宽：**{drawer_inner_width:.0f} mm**")
    st.write(f"抽盒高度：**{drawer_box_height:.0f} mm**")
    st.write(f"抽屉结构自重：**{single_drawer_structure_weight:.2f} kg**")
    st.write(f"模拟衣服荷重：**{loaded_weight:.2f} kg**")
    st.write(f"抽屉中心离地高度：**{drawer_center_height:.0f} mm**")
    st.write(f"抽屉拉开倾覆力矩：**{drawer_open_moment:.2f} N·m**")
    st.write(f"该高度下水平拉力力矩：**{drawer_horizontal_moment:.2f} N·m**")

total_drawer_open_moment = sum(item["open_moment"] for item in drawer_data)
max_single_drawer_moment = max([item["open_moment"] for item in drawer_data], default=0)
max_single_drawer = max(drawer_data, key=lambda x: x["open_moment"], default=None)

st.subheader("抽屉拉开风险汇总")
st.write(f"所有抽屉同时拉开造成的总倾覆力矩：**{total_drawer_open_moment:.2f} N·m**")
st.write(f"单个最危险抽屉造成的最大倾覆力矩：**{max_single_drawer_moment:.2f} N·m**")

if max_single_drawer:
    st.write(
        f"最危险抽屉：**抽屉 {max_single_drawer['index']}**，"
        f"中心离地高度 **{max_single_drawer['center_height']:.0f} mm**，"
        f"拉出距离 **{max_single_drawer['extension']:.0f} mm**"
    )


# =========================
# 4. 柜门重量与打开风险
# =========================

st.header("4. 柜门重量与打开风险计算")

door_enabled = st.checkbox("是否有门板/柜门", value=False)

total_door_weight = 0.0
door_data = []

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

        col1, col2, col3, col4, col5 = st.columns(5)

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

        with col3:
            door_bottom_height = st.number_input(
                f"门板 {i + 1} 底边离地高度 mm",
                min_value=0.0,
                value=100.0,
                key=f"door_bottom_height_{i}"
            )

        with col4:
            door_open_distance = st.number_input(
                f"门板 {i + 1} 打开后重心前移距离 mm",
                min_value=0.0,
                value=150.0,
                key=f"door_open_distance_{i}"
            )

        with col5:
            door_pull_height = st.number_input(
                f"门板 {i + 1} 拉力作用高度 mm",
                min_value=0.0,
                value=door_bottom_height + door_outer_height / 2,
                key=f"door_pull_height_{i}"
            )

        if door_type == "内嵌门板":
            door_width = max(0, door_outer_width - 6)
            door_height = max(0, door_outer_height - 6)
        else:
            door_width = max(0, door_outer_width - 2)
            door_height = max(0, door_outer_height - 3)

        door_weight_mode = st.radio(
            f"门板 {i + 1} 重量计算方式",
            ["按材质自动计算", "手动填写重量"],
            horizontal=True,
            key=f"door_weight_mode_{i}"
        )

        door_structure_type = st.selectbox(
            f"门板 {i + 1} 结构类型",
            ["板式门板", "玻璃门板", "板式+玻璃混合门板"],
            key=f"door_structure_type_{i}"
        )

        if door_weight_mode == "手动填写重量":
            door_weight = st.number_input(
                f"门板 {i + 1} 实际重量 kg",
                min_value=0.0,
                value=3.0,
                key=f"door_manual_weight_{i}"
            )
        else:
            if door_structure_type == "板式门板":
                door_weight = calc_board_weight(
                    door_width,
                    door_height,
                    board_thickness,
                    door_density
                )

            elif door_structure_type == "玻璃门板":
                glass_thickness = st.number_input(
                    f"门板 {i + 1} 玻璃厚度 mm",
                    min_value=1.0,
                    value=4.0,
                    key=f"door_glass_thickness_{i}"
                )

                door_weight = calc_board_weight(
                    door_width,
                    door_height,
                    glass_thickness,
                    glass_density
                )

            else:
                glass_ratio = st.slider(
                    f"门板 {i + 1} 玻璃面积占比",
                    min_value=0.0,
                    max_value=1.0,
                    value=0.5,
                    step=0.05,
                    key=f"door_glass_ratio_{i}"
                )

                glass_thickness = st.number_input(
                    f"门板 {i + 1} 玻璃厚度 mm",
                    min_value=1.0,
                    value=4.0,
                    key=f"door_mixed_glass_thickness_{i}"
                )

                board_part_weight = calc_board_weight(
                    door_width,
                    door_height * (1 - glass_ratio),
                    board_thickness,
                    door_density
                )

                glass_part_weight = calc_board_weight(
                    door_width,
                    door_height * glass_ratio,
                    glass_thickness,
                    glass_density
                )

                door_weight = board_part_weight + glass_part_weight

        door_center_height = door_bottom_height + door_height / 2
        door_open_moment = door_weight * 9.8 * (door_open_distance / 1000)
        door_horizontal_moment = force_n * (door_pull_height / 1000)

        total_door_weight += door_weight

        door_data.append({
            "index": i + 1,
            "weight": door_weight,
            "bottom_height": door_bottom_height,
            "center_height": door_center_height,
            "open_distance": door_open_distance,
            "pull_height": door_pull_height,
            "open_moment": door_open_moment,
            "horizontal_moment": door_horizontal_moment,
            "structure_type": door_structure_type,
        })

        st.write(f"门板计算尺寸：**{door_width:.0f} × {door_height:.0f} mm**")
        st.write(f"门板重量：**{door_weight:.2f} kg**")
        st.write(f"门板中心离地高度：**{door_center_height:.0f} mm**")
        st.write(f"门板打开前移力矩：**{door_open_moment:.2f} N·m**")
        st.write(f"门板水平拉力力矩：**{door_horizontal_moment:.2f} N·m**")

total_door_open_moment = sum(item["open_moment"] for item in door_data)
max_single_door_moment = max([item["open_moment"] for item in door_data], default=0)
max_single_door = max(door_data, key=lambda x: x["open_moment"], default=None)

st.subheader("柜门打开风险汇总")
st.write(f"所有柜门同时打开造成的总倾覆力矩：**{total_door_open_moment:.2f} N·m**")
st.write(f"单扇最危险柜门造成的最大倾覆力矩：**{max_single_door_moment:.2f} N·m**")

if max_single_door:
    st.write(
        f"最危险柜门：**门板 {max_single_door['index']}**，"
        f"结构：**{max_single_door['structure_type']}**，"
        f"重量 **{max_single_door['weight']:.2f} kg**，"
        f"拉力高度 **{max_single_door['pull_height']:.0f} mm**"
    )


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
- 门板/柜门结构：{total_door_weight:.2f} kg
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

force_height = min(height, 1422)

drawer_max_horizontal_moment = max([item["horizontal_moment"] for item in drawer_data], default=0)
door_max_horizontal_moment = max([item["horizontal_moment"] for item in door_data], default=0)

standard_horizontal_moment = force_n * (force_height / 1000)
overturn_moment = max(
    standard_horizontal_moment,
    drawer_max_horizontal_moment,
    door_max_horizontal_moment
)

gravity_n = weight * 9.8
half_depth_m = depth / 2 / 1000
resisting_moment = gravity_n * half_depth_m

horizontal_pass = resisting_moment >= overturn_moment * safety_factor

st.write(f"标准水平拉力力矩：**{standard_horizontal_moment:.2f} N·m**")
st.write(f"抽屉高度中最大水平拉力力矩：**{drawer_max_horizontal_moment:.2f} N·m**")
st.write(f"柜门高度中最大水平拉力力矩：**{door_max_horizontal_moment:.2f} N·m**")
st.write(f"最终采用的水平倾覆力矩：**{overturn_moment:.2f} N·m**")
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

if max_single_drawer and max_single_door:
    if max_single_drawer["open_moment"] >= max_single_door["open_moment"]:
        child_target_type = "抽屉"
        child_target_index = max_single_drawer["index"]
        child_test_extension = max_single_drawer["extension"]
        child_target_height = max_single_drawer["center_height"]
    else:
        child_target_type = "柜门"
        child_target_index = max_single_door["index"]
        child_test_extension = max_single_door["open_distance"]
        child_target_height = max_single_door["center_height"]
elif max_single_drawer:
    child_target_type = "抽屉"
    child_target_index = max_single_drawer["index"]
    child_test_extension = max_single_drawer["extension"]
    child_target_height = max_single_drawer["center_height"]
elif max_single_door:
    child_target_type = "柜门"
    child_target_index = max_single_door["index"]
    child_test_extension = max_single_door["open_distance"]
    child_target_height = max_single_door["center_height"]
else:
    child_target_type = "无"
    child_target_index = None
    child_test_extension = 0
    child_target_height = 0

child_overturn_moment = child_force_n * (child_test_extension / 1000)
child_pass = resisting_moment >= child_overturn_moment * safety_factor

if child_target_index:
    st.write(f"儿童荷重默认作用于最危险部件：**{child_target_type} {child_target_index}**")
    st.write(f"目标中心离地高度：**{child_target_height:.0f} mm**")
    st.write(f"目标前移/拉出距离：**{child_test_extension:.0f} mm**")

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

total_open_moment = total_drawer_open_moment + total_door_open_moment

all_drawers_open_pass = resisting_moment >= total_drawer_open_moment * safety_factor
all_doors_open_pass = resisting_moment >= total_door_open_moment * safety_factor
all_drawers_doors_open_pass = resisting_moment >= total_open_moment * safety_factor

required_moment = max(
    overturn_moment * safety_factor,
    child_overturn_moment * safety_factor,
    total_drawer_open_moment * safety_factor,
    total_door_open_moment * safety_factor,
    total_open_moment * safety_factor
)

required_depth_m = required_moment / gravity_n * 2 if gravity_n > 0 else 0
required_depth_mm = required_depth_m * 1000
extra_depth_mm = max(0, required_depth_mm - depth)

required_weight_kg = required_moment / (9.8 * half_depth_m) if half_depth_m > 0 else 0
extra_weight_kg = max(0, required_weight_kg - weight)

risk_points = []

if is_f2057_applicable:
    risk_points.append("属于 F2057 测试范围")

if not horizontal_pass:
    risk_points.append("水平动态力测试风险高")

if not child_pass:
    risk_points.append("儿童荷重测试风险高")

if not all_drawers_open_pass:
    risk_points.append("所有抽屉同时拉开风险高")

if not all_doors_open_pass:
    risk_points.append("所有柜门同时打开风险高")

if not all_drawers_doors_open_pass:
    risk_points.append("所有抽屉和柜门同时打开风险高")

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

st.subheader("全部打开风险汇总")
st.write(f"所有抽屉同时拉开力矩：**{total_drawer_open_moment:.2f} N·m**")
st.write(f"所有柜门同时打开力矩：**{total_door_open_moment:.2f} N·m**")
st.write(f"所有抽屉 + 柜门同时打开总力矩：**{total_open_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")

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
- 门板/抽面默认材料：{door_material}，{door_density} kg/m³
- 背板/抽屉底板：MDF板-背板/抽屉底板，{back_bottom_density} kg/m³

板件重量：
- 顶板：{top_panel_weight:.2f} kg
- 底板：{bottom_panel_weight:.2f} kg
- 左侧板：{left_side_weight:.2f} kg
- 右侧板：{right_side_weight:.2f} kg
- 背板：{back_panel_weight:.2f} kg
- 底板加厚框：{bottom_frame_weight:.2f} kg
- 抽屉结构：{total_drawer_structure_weight:.2f} kg
- 门板/柜门结构：{total_door_weight:.2f} kg
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

抽屉/柜门打开风险：
- 所有抽屉同时拉开倾覆力矩：{total_drawer_open_moment:.2f} N·m
- 所有柜门同时打开倾覆力矩：{total_door_open_moment:.2f} N·m
- 所有抽屉 + 柜门同时打开倾覆力矩：{total_open_moment:.2f} N·m
- 单个最危险抽屉力矩：{max_single_drawer_moment:.2f} N·m
- 单扇最危险柜门力矩：{max_single_door_moment:.2f} N·m

综合风险点：
{chr(10).join(["- " + item for item in risk_points]) if risk_points else "- 暂无明显高风险点"}

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
