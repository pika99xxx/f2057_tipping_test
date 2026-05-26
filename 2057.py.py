import math
import streamlit as st

st.set_page_config(page_title="F2057 防倾倒测试预判工具", layout="wide")

st.title("柜类产品 F2057 防倾倒测试预判工具")
st.warning("本工具仅用于设计阶段预判，不能替代 ASTM F2057-23 正式实验室测试。")


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

col1, col2 = st.columns([1, 2])

with col1:
    safety_factor = st.number_input(
        "安全系数",
        min_value=1.0,
        value=1.2,
        step=0.1
    )

with col2:
    st.info(
        """
安全系数说明：

- 1.0：完全按理论临界值判断，不推荐  
- 1.1：轻微保守  
- 1.2：推荐默认值  
- 1.3：更保守，适合高柜、窄柜、儿童接触风险高的产品  
- 1.5：非常保守，适合前期快速筛掉高风险设计
        """
    )

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
    ["同柜体主材料", "MDF板-柜体/横条/门板/抽面/抽盒", "MDF板-吸塑门板"],
    index=0
)

door_density = density if door_material == "同柜体主材料" else material_density_map[door_material]
back_bottom_density = material_density_map["MDF板-背板/抽屉底板"]
glass_density = material_density_map["玻璃"]

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
st.write(f"顶板：{top_panel_weight:.2f} kg")
st.write(f"底板：{bottom_panel_weight:.2f} kg")
st.write(f"左侧板：{left_side_weight:.2f} kg")
st.write(f"右侧板：{right_side_weight:.2f} kg")
st.write(f"背板：{back_panel_weight:.2f} kg")
st.write(f"底板加厚框：{bottom_frame_weight:.2f} kg")


# =========================
# 3. 抽屉数据采集
# =========================

st.header("3. 抽屉重量、体积与打开风险")

force_n = 44

drawer_type = st.selectbox("抽面形式", ["内嵌抽面", "外盖抽面"], index=0)

drawer_count = st.number_input(
    "抽屉数量",
    min_value=0,
    max_value=20,
    value=3,
    step=1
)

drawer_raw_data = []

for i in range(int(drawer_count)):
    st.subheader(f"抽屉 {i + 1}")

    col1, col2, col3, col4 = st.columns(4)

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

    col5, col6 = st.columns(2)

    with col5:
        drawer_has_stop = st.checkbox(
            f"抽屉 {i + 1} 是否有阻挡/限位",
            value=False,
            key=f"drawer_has_stop_{i}"
        )

    with col6:
        osl = st.number_input(
            f"抽屉 {i + 1} OSL 最大滑出长度 mm",
            min_value=0.0,
            value=500.0,
            key=f"drawer_osl_{i}"
        )

    if drawer_has_stop:
        drawer_extension = st.number_input(
            f"抽屉 {i + 1} 实际可拉出距离 mm",
            min_value=0.0,
            value=300.0,
            key=f"drawer_extension_{i}"
        )
    else:
        drawer_extension = osl * 0.6
        st.write(f"无阻挡时，测试拉出距离按 OSL 60% 计算：**{drawer_extension:.0f} mm**")

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

    drawer_storage_volume_dm3 = drawer_inner_width * drawer_inner_depth * drawer_box_height / 1_000_000

    drawer_raw_data.append({
        "index": i + 1,
        "structure_weight": single_drawer_structure_weight,
        "storage_volume_dm3": drawer_storage_volume_dm3,
        "bottom_height": drawer_bottom_height,
        "outer_height": drawer_outer_height,
        "center_height": drawer_bottom_height + drawer_outer_height / 2,
        "extension": drawer_extension,
        "inner_width": drawer_inner_width,
        "inner_depth": drawer_inner_depth,
        "box_height": drawer_box_height,
    })

    st.write(f"抽屉结构自重：**{single_drawer_structure_weight:.2f} kg**")
    st.write(f"抽屉封闭存储体积：**{drawer_storage_volume_dm3:.2f} dm³**")
    st.write(f"抽屉中心离地高度：**{drawer_bottom_height + drawer_outer_height / 2:.0f} mm**")


# =========================
# 4. 非延展封闭空间体积
# =========================

st.header("4. 非延展封闭空间体积计算")

total_extendable_volume_dm3 = sum(item["storage_volume_dm3"] for item in drawer_raw_data)
total_non_extendable_volume_dm3 = 0.0

non_extendable_count = st.number_input(
    "非延展封闭空间数量",
    min_value=0,
    max_value=20,
    value=0,
    step=1
)

for i in range(int(non_extendable_count)):
    st.subheader(f"非延展空间 {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        space_w = st.number_input(
            f"空间 {i + 1} 内宽 mm",
            min_value=1.0,
            value=400.0,
            key=f"space_w_{i}"
        )

    with col2:
        space_d = st.number_input(
            f"空间 {i + 1} 内深 mm",
            min_value=1.0,
            value=300.0,
            key=f"space_d_{i}"
        )

    with col3:
        space_h = st.number_input(
            f"空间 {i + 1} 内高 mm",
            min_value=1.0,
            value=300.0,
            key=f"space_h_{i}"
        )

    raw_volume_dm3 = space_w * space_d * space_h / 1_000_000

    if space_h < 76.2:
        effective_volume_dm3 = 0
        st.warning("该空间高度小于 3in / 76.2mm，不计入封闭存储体积。")
    elif raw_volume_dm3 < 1.7:
        effective_volume_dm3 = 0
        st.warning("该连续空间小于 1.7dm³，不计入封闭存储体积。")
    else:
        effective_volume_dm3 = raw_volume_dm3 * 0.5

    total_non_extendable_volume_dm3 += effective_volume_dm3

    st.write(f"原始体积：{raw_volume_dm3:.2f} dm³")
    st.write(f"计入体积：{effective_volume_dm3:.2f} dm³")

closed_volume_dm3 = total_extendable_volume_dm3 + total_non_extendable_volume_dm3

if closed_volume_dm3 > 0:
    extendable_ratio = total_extendable_volume_dm3 / closed_volume_dm3
else:
    extendable_ratio = 0

load_clothes_enabled = extendable_ratio >= 0.5

st.subheader("封闭存储体积汇总")
st.write(f"可延展部件体积：**{total_extendable_volume_dm3:.2f} dm³**")
st.write(f"非延展空间计入体积：**{total_non_extendable_volume_dm3:.2f} dm³**")
st.write(f"总封闭存储体积：**{closed_volume_dm3:.2f} dm³**")
st.write(f"可延展部件体积占比：**{extendable_ratio * 100:.1f}%**")

if load_clothes_enabled:
    st.success("可延展部件体积占比 ≥ 50%，模拟衣服荷重生效。")
else:
    st.warning("可延展部件体积占比 < 50%，模拟衣服荷重不加载。")


# =========================
# 5. 抽屉加载与风险计算
# =========================

total_drawer_structure_weight = 0.0
total_loaded_weight = 0.0
drawer_data = []

for item in drawer_raw_data:
    loaded_weight = item["storage_volume_dm3"] * 0.136 if load_clothes_enabled else 0
    moving_weight = item["structure_weight"] + loaded_weight
    open_moment = moving_weight * 9.8 * (item["extension"] / 1000)
    horizontal_moment = force_n * (min(item["center_height"], 1422) / 1000)

    total_drawer_structure_weight += item["structure_weight"]
    total_loaded_weight += loaded_weight

    new_item = item.copy()
    new_item.update({
        "loaded_weight": loaded_weight,
        "moving_weight": moving_weight,
        "open_moment": open_moment,
        "horizontal_moment": horizontal_moment,
    })

    drawer_data.append(new_item)

total_drawer_open_moment = sum(item["open_moment"] for item in drawer_data)
max_single_drawer_moment = max([item["open_moment"] for item in drawer_data], default=0)
max_single_drawer = max(drawer_data, key=lambda x: x["open_moment"], default=None)

st.header("5. 抽屉加载与风险汇总")
st.write(f"抽屉结构总重量：**{total_drawer_structure_weight:.2f} kg**")
st.write(f"模拟衣服总荷重：**{total_loaded_weight:.2f} kg**")
st.write(f"所有抽屉同时拉开倾覆力矩：**{total_drawer_open_moment:.2f} N·m**")


# =========================
# 6. 柜门重量与打开风险
# =========================

st.header("6. 柜门重量与打开风险计算")

door_enabled = st.checkbox("是否有门板/柜门", value=False)

total_door_weight = 0.0
door_data = []

if door_enabled:
    door_type = st.selectbox("门板形式", ["内嵌门板", "外盖门板"], index=0)

    door_count = st.number_input(
        "门板数量",
        min_value=1,
        max_value=20,
        value=2,
        step=1
    )

    for i in range(int(door_count)):
        st.subheader(f"门板 {i + 1}")

        col1, col2, col3, col4 = st.columns(4)

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
            door_open_angle = st.number_input(
                f"门板 {i + 1} 打开角度 °",
                min_value=0.0,
                max_value=180.0,
                value=90.0,
                key=f"door_open_angle_{i}"
            )

        if door_type == "内嵌门板":
            door_width = max(0, door_outer_width - 6)
            door_height = max(0, door_outer_height - 6)
        else:
            door_width = max(0, door_outer_width - 2)
            door_height = max(0, door_outer_height - 3)

        door_open_distance = (door_width / 2) * math.sin(math.radians(door_open_angle))

        door_pull_height = st.number_input(
            f"门板 {i + 1} 拉力作用高度 mm",
            min_value=0.0,
            value=door_bottom_height + door_height / 2,
            key=f"door_pull_height_{i}"
        )

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
                door_weight = calc_board_weight(door_width, door_height, board_thickness, door_density)

            elif door_structure_type == "玻璃门板":
                glass_thickness = st.number_input(
                    f"门板 {i + 1} 玻璃厚度 mm",
                    min_value=1.0,
                    value=4.0,
                    key=f"door_glass_thickness_{i}"
                )
                door_weight = calc_board_weight(door_width, door_height, glass_thickness, glass_density)

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
        door_horizontal_moment = force_n * (min(door_pull_height, 1422) / 1000)

        total_door_weight += door_weight

        door_data.append({
            "index": i + 1,
            "weight": door_weight,
            "center_height": door_center_height,
            "open_distance": door_open_distance,
            "pull_height": door_pull_height,
            "open_moment": door_open_moment,
            "horizontal_moment": door_horizontal_moment,
            "structure_type": door_structure_type,
        })

        st.write(f"门板计算尺寸：**{door_width:.0f} × {door_height:.0f} mm**")
        st.write(f"门板重量：**{door_weight:.2f} kg**")
        st.write(f"按角度计算的门板重心前移距离：**{door_open_distance:.0f} mm**")
        st.write(f"门板打开前移力矩：**{door_open_moment:.2f} N·m**")

total_door_open_moment = sum(item["open_moment"] for item in door_data)
max_single_door_moment = max([item["open_moment"] for item in door_data], default=0)
max_single_door = max(door_data, key=lambda x: x["open_moment"], default=None)

st.subheader("柜门打开风险汇总")
st.write(f"所有柜门同时打开倾覆力矩：**{total_door_open_moment:.2f} N·m**")


# =========================
# 7. 五金与额外重量
# =========================

st.header("7. 五金与额外重量")

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

st.header("8. 整柜重量汇总")

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
# 8. F2057 适用性判断
# =========================

st.header("9. 是否属于 F2057 测试范围")

is_height_ok = height >= 686
is_weight_ok = weight >= 13.6
is_volume_ok = closed_volume_dm3 >= 90.6

is_f2057_applicable = is_height_ok and is_weight_ok and is_volume_ok

st.write("高度 ≥ 686mm：", "✅ 是" if is_height_ok else "❌ 否")
st.write("重量 ≥ 13.6kg：", "✅ 是" if is_weight_ok else "❌ 否")
st.write("封闭存储体积 ≥ 90.6dm³：", "✅ 是" if is_volume_ok else "❌ 否")

if is_f2057_applicable:
    st.error("该产品属于 ASTM F2057-23 衣物储存柜测试范围，需要进行防倾倒测试。")
else:
    st.success("该产品可能不属于 ASTM F2057-23 强制测试范围，但仍建议做稳定性风险评估。")


# =========================
# 9. 水平动态力测试
# =========================

st.header("10. 模拟水平动态力测试")

standard_horizontal_moment = force_n * (min(height, 1422) / 1000)
drawer_max_horizontal_moment = max([item["horizontal_moment"] for item in drawer_data], default=0)
door_max_horizontal_moment = max([item["horizontal_moment"] for item in door_data], default=0)

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
st.write(f"抽屉最大水平拉力力矩：**{drawer_max_horizontal_moment:.2f} N·m**")
st.write(f"柜门最大水平拉力力矩：**{door_max_horizontal_moment:.2f} N·m**")
st.write(f"最终采用的水平倾覆力矩：**{overturn_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")

if horizontal_pass:
    st.success("水平动态力测试预判：风险较低")
else:
    st.error("水平动态力测试预判：风险较高")


# =========================
# 10. 儿童荷重逐一测试 + 后脚垫块修正
# =========================

st.header("11. 儿童荷重逐一测试")

child_weight = 27.22
child_force_n = child_weight * 9.8

test_block_height = st.number_input(
    "后脚测试块高度 mm",
    min_value=0.0,
    value=10.9
)

estimated_cog_height = st.number_input(
    "预估整柜重心高度 mm",
    min_value=1.0,
    value=height * 0.45
)

tilt_angle_rad = math.atan(test_block_height / depth)
cog_forward_shift_mm = estimated_cog_height * math.tan(tilt_angle_rad)
block_extra_moment = gravity_n * (cog_forward_shift_mm / 1000)

st.write(f"后脚垫块导致的等效重心前移：**{cog_forward_shift_mm:.1f} mm**")
st.write(f"后脚垫块增加的倾覆力矩：**{block_extra_moment:.2f} N·m**")

child_test_results = []

for item in drawer_data:
    moment = child_force_n * (item["extension"] / 1000) + block_extra_moment
    passed = resisting_moment >= moment * safety_factor

    child_test_results.append({
        "type": "抽屉",
        "index": item["index"],
        "distance": item["extension"],
        "moment": moment,
        "passed": passed,
    })

for item in door_data:
    moment = child_force_n * (item["open_distance"] / 1000) + block_extra_moment
    passed = resisting_moment >= moment * safety_factor

    child_test_results.append({
        "type": "柜门",
        "index": item["index"],
        "distance": item["open_distance"],
        "moment": moment,
        "passed": passed,
    })

max_child_moment = max([item["moment"] for item in child_test_results], default=0)
child_pass = all(item["passed"] for item in child_test_results) if child_test_results else True

for item in child_test_results:
    msg = (
        f"{item['type']} {item['index']}："
        f"前移/拉出距离 {item['distance']:.0f}mm，"
        f"儿童荷重力矩 {item['moment']:.2f} N·m"
    )
    if item["passed"]:
        st.success(msg)
    else:
        st.error(msg)


# =========================
# 11. 全部打开风险
# =========================

st.header("12. 全部打开风险")

total_open_moment = total_drawer_open_moment + total_door_open_moment

all_drawers_open_pass = resisting_moment >= total_drawer_open_moment * safety_factor
all_doors_open_pass = resisting_moment >= total_door_open_moment * safety_factor
all_drawers_doors_open_pass = resisting_moment >= total_open_moment * safety_factor

st.write(f"所有抽屉同时拉开力矩：**{total_drawer_open_moment:.2f} N·m**")
st.write(f"所有柜门同时打开力矩：**{total_door_open_moment:.2f} N·m**")
st.write(f"所有抽屉 + 柜门同时打开总力矩：**{total_open_moment:.2f} N·m**")
st.write(f"当前抗倾覆力矩：**{resisting_moment:.2f} N·m**")


# =========================
# 12. 内锁、防倒五金、警告标贴检查
# =========================

st.header("13. 内锁、防倒五金与警告标贴检查")

has_interlock = st.checkbox("是否有内锁装置", value=False)

if has_interlock:
    interlock_auto = st.checkbox("内锁是否在正常打开/关闭过程中自动生效", value=True)
    interlock_pull_pass = st.checkbox("内锁是否通过 30lb / 10s 拉力测试", value=False)
    interlock_all_combinations_tested = st.checkbox("是否已测试所有内锁组合", value=False)
    interlock_pass = interlock_auto and interlock_pull_pass and interlock_all_combinations_tested
else:
    interlock_pass = True

has_anti_tip = st.checkbox("是否配备防倾倒五金", value=True)
anti_tip_60lb_pass = st.checkbox("防倾倒五金是否通过 60lb / 30s 拉力测试", value=False)
has_install_manual = st.checkbox("是否有清晰安装说明书", value=False)

anti_tip_pass = has_anti_tip and anti_tip_60lb_pass and has_install_manual

has_warning_label = st.checkbox("是否至少有一处永久性警告标贴", value=True)
warning_label_visible = st.checkbox("警告标贴是否在显眼位置", value=True)
warning_label_not_folded = st.checkbox("警告标贴是否未折叠/未包裹在角落", value=True)

warning_label_pass = has_warning_label and warning_label_visible and warning_label_not_folded


# =========================
# 13. 综合判断与优化建议
# =========================

st.header("14. 综合判断与优化建议")

required_moment = max(
    overturn_moment * safety_factor,
    max_child_moment * safety_factor,
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
    risk_points.append("儿童荷重逐一测试存在风险")

if not all_drawers_open_pass:
    risk_points.append("所有抽屉同时拉开风险高")

if not all_doors_open_pass:
    risk_points.append("所有柜门同时打开风险高")

if not all_drawers_doors_open_pass:
    risk_points.append("所有抽屉和柜门同时打开风险高")

if not interlock_pass:
    risk_points.append("内锁装置存在合规风险")

if not anti_tip_pass:
    risk_points.append("防倾倒五金存在合规风险")

if not warning_label_pass:
    risk_points.append("警告标贴存在合规风险")

if len(risk_points) == 0:
    st.success("综合风险：低")
elif len(risk_points) <= 3:
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
# 14. 报告下载
# =========================

st.header("15. 测试预判报告摘要")

report = f"""
产品名称：{product_name}

柜体尺寸：
- 宽度：{width:.0f} mm
- 深度：{depth:.0f} mm
- 高度：{height:.0f} mm

封闭存储体积：
- 可延展部件体积：{total_extendable_volume_dm3:.2f} dm³
- 非延展空间计入体积：{total_non_extendable_volume_dm3:.2f} dm³
- 总封闭存储体积：{closed_volume_dm3:.2f} dm³
- 可延展体积占比：{extendable_ratio * 100:.1f}%
- 模拟衣服荷重是否生效：{"是" if load_clothes_enabled else "否"}

整柜重量：
- 基础柜体板件：{basic_cabinet_weight:.2f} kg
- 抽屉结构：{total_drawer_structure_weight:.2f} kg
- 门板/柜门结构：{total_door_weight:.2f} kg
- 五金：{hardware_weight:.2f} kg
- 底部额外配重：{extra_bottom_weight:.2f} kg
- 自动估算整柜重量：{weight:.2f} kg

F2057 适用性：
- 高度 ≥ 686mm：{"是" if is_height_ok else "否"}
- 重量 ≥ 13.6kg：{"是" if is_weight_ok else "否"}
- 封闭存储体积 ≥ 90.6dm³：{"是" if is_volume_ok else "否"}
- 是否属于测试范围：{"是" if is_f2057_applicable else "否"}

稳定性预判：
- 水平动态力测试：{"通过预判" if horizontal_pass else "风险较高"}
- 儿童荷重逐一测试：{"通过预判" if child_pass else "存在风险"}
- 所有抽屉同时拉开力矩：{total_drawer_open_moment:.2f} N·m
- 所有柜门同时打开力矩：{total_door_open_moment:.2f} N·m
- 所有抽屉 + 柜门同时打开力矩：{total_open_moment:.2f} N·m
- 后脚垫块修正力矩：{block_extra_moment:.2f} N·m

合规检查：
- 内锁装置：{"通过/不适用" if interlock_pass else "存在风险"}
- 防倾倒五金：{"通过" if anti_tip_pass else "存在风险"}
- 警告标贴：{"通过" if warning_label_pass else "存在风险"}

综合风险点：
{chr(10).join(["- " + item for item in risk_points]) if risk_points else "- 暂无明显高风险点"}

优化建议：
- 建议柜体深度：{required_depth_mm:.0f} mm 以上
- 需要增加深度：{extra_depth_mm:.0f} mm
- 建议整柜重量：{required_weight_kg:.1f} kg 以上
- 建议底部增重：{extra_weight_kg:.1f} kg

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
