import flet as ft
import os


def main(page: ft.Page):
    page.title = "เปรียบเทียบราคาสินค้า"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.scroll = ft.ScrollMode.ADAPTIVE
    page.bgcolor = "#F0F4FF"

    entries = []

    # ===== Responsive padding ตาม screen width =====
    def update_padding(e=None):
        w = page.width or 400
        if w < 600:
            page.padding = ft.padding.symmetric(horizontal=12, vertical=16)
        elif w < 1024:
            page.padding = ft.padding.symmetric(horizontal=24, vertical=24)
        else:
            page.padding = ft.padding.symmetric(horizontal=80, vertical=32)
        page.update()

    page.on_resized = update_padding

    # ===== Dialog สำหรับผลลัพธ์ =====
    result_content = ft.Column([], tight=True, spacing=8)

    result_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("📊 ผลการคำนวณ", weight="bold", size=18),
        content=ft.Container(content=result_content, width=360),
        actions=[
            ft.FilledButton(
                "ตกลง",
                on_click=lambda e: close_result_dialog(),
                style=ft.ButtonStyle(bgcolor="#3949AB"),
            )
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def close_result_dialog():
        result_dialog.open = False
        page.update()

    def show_result(rows, winner_names, cheapest_price):
        result_content.controls.clear()

        for name, unit_price, is_winner in rows:
            result_content.controls.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(
                            ft.Icons.STAR if is_winner else ft.Icons.LABEL_OUTLINE,
                            color="#F9A825" if is_winner else "#90A4AE",
                            size=18,
                        ),
                        ft.Column([
                            ft.Text(
                                name,
                                weight="bold" if is_winner else "normal",
                                size=14,
                                color="#1A237E" if is_winner else "#455A64",
                            ),
                            ft.Text(
                                f"{unit_price:.2f} บาท/หน่วย",
                                size=13,
                                color="#F9A825" if is_winner else "#607D8B",
                            ),
                        ], spacing=2, expand=True),
                    ], spacing=8),
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    border_radius=10,
                    bgcolor="#FFFDE7" if is_winner else "#F5F5F5",
                    border=ft.border.all(1.5, "#F9A825" if is_winner else "#E0E0E0"),
                )
            )

        winner_label = " และ ".join(winner_names)
        result_content.controls.append(
            ft.Container(
                content=ft.Text(
                    f"✅ คุ้มค่าที่สุด: {winner_label}",
                    weight="bold",
                    size=14,
                    color="#2E7D32",
                ),
                padding=ft.padding.only(top=8),
            )
        )
        page.open(result_dialog)

    def show_error(message):
        page.open(ft.SnackBar(content=ft.Text(message)))

    # ===== ลบสินค้า =====
    def remove_entry(entry_container, row_data):
        entry_grid.controls.remove(entry_container)
        entries.remove(row_data)
        page.update()

    # ===== คำนวณ =====
    def calculate_result(e=None):
        if not entries:
            show_error("❗ กรุณาเพิ่มสินค้าอย่างน้อย 1 รายการ")
            return

        cheapest_price = float("inf")
        cheapest_names = []
        result_rows = []

        for row in entries:
            name = row["name"].value.strip()
            if not name:
                show_error("❗ กรุณากรอกชื่อสินค้าทุกรายการ")
                return

            try:
                price = float(row["price"].value)
                quantity = float(row["quantity"].value)
            except ValueError:
                show_error("❗ กรุณากรอกราคาและปริมาณให้ถูกต้อง")
                return

            if quantity <= 0:
                show_error("❗ ปริมาณต้องมากกว่า 0")
                return

            unit_price = price / quantity
            row["unit_price"].value = f"{unit_price:.2f} บาท/หน่วย"
            result_rows.append((name, unit_price))

            if unit_price < cheapest_price:
                cheapest_price = unit_price
                cheapest_names = [name]
            elif unit_price == cheapest_price:
                cheapest_names.append(name)

        page.update()

        rows_with_flag = [
            (name, price, name in cheapest_names)
            for name, price in result_rows
        ]
        show_result(rows_with_flag, cheapest_names, cheapest_price)

    # ===== เพิ่มสินค้า =====
    def add_entry(e=None):
        idx = len(entries) + 1

        name = ft.TextField(
            label="ชื่อสินค้า",
            hint_text="เช่น น้ำยาล้างจาน A",
            expand=True,
            border_radius=8,
            focused_border_color="#3949AB",
        )
        price = ft.TextField(
            label="ราคา (บาท)",
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
            border_radius=8,
            prefix_icon=ft.Icons.ATTACH_MONEY,
            focused_border_color="#3949AB",
        )
        quantity = ft.TextField(
            label="ปริมาณ",
            keyboard_type=ft.KeyboardType.NUMBER,
            expand=True,
            border_radius=8,
            prefix_icon=ft.Icons.SCALE,
            focused_border_color="#3949AB",
        )
        unit_price = ft.Text(value="", size=12, color="#7986CB", italic=True)

        row_data = {
            "name": name,
            "price": price,
            "quantity": quantity,
            "unit_price": unit_price,
        }

        delete_btn = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color="#EF5350",
            tooltip="ลบสินค้า",
            on_click=lambda e: remove_entry(entry_container, row_data),
        )

        entry_container = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Row([
                        ft.Icon(ft.Icons.SHOPPING_BASKET_OUTLINED, color="#3949AB", size=18),
                        ft.Text(f"สินค้า #{idx}", weight="bold", size=14, color="#3949AB"),
                    ], spacing=6),
                    delete_btn,
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                name,
                ft.Row([price, quantity], spacing=8),
                unit_price,
            ], spacing=10),
            padding=16,
            border_radius=16,
            bgcolor=ft.colors.WHITE,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=12,
                color=ft.colors.with_opacity(0.08, ft.colors.BLACK),
                offset=ft.Offset(0, 3),
            ),
            col={"xs": 12, "sm": 12, "md": 6, "lg": 4},
        )

        entries.append(row_data)
        entry_grid.controls.append(entry_container)
        page.update()

    # ===== UI =====
    header = ft.Container(
        content=ft.Column([
            ft.Text("เปรียบเทียบราคาต่อหน่วย", size=26, weight="bold", color="#1A237E"),
            ft.Text("กรอกสินค้า ราคา และปริมาณ แล้วกดคำนวณ", size=13, color="#78909C", italic=True),
        ], spacing=4),
        padding=ft.padding.only(bottom=4),
    )

    entry_grid = ft.ResponsiveRow(spacing=12, run_spacing=12)

    action_row = ft.Container(
        content=ft.Row(
            [
                ft.ElevatedButton(
                    "เพิ่มสินค้า",
                    icon=ft.Icons.ADD_CIRCLE_OUTLINE,
                    on_click=add_entry,
                    style=ft.ButtonStyle(
                        bgcolor="#E8EAF6",
                        color="#3949AB",
                        padding=ft.padding.symmetric(horizontal=20, vertical=14),
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
                ft.FilledButton(
                    "คำนวณ",
                    icon=ft.Icons.CALCULATE_OUTLINED,
                    on_click=calculate_result,
                    style=ft.ButtonStyle(
                        bgcolor="#3949AB",
                        padding=ft.padding.symmetric(horizontal=20, vertical=14),
                        shape=ft.RoundedRectangleBorder(radius=12),
                    ),
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=12,
            wrap=True,
        ),
        padding=ft.padding.only(top=8),
    )

    add_entry()
    add_entry()

    page.add(ft.Column([header, entry_grid, action_row], spacing=20))
    update_padding()


# ===== RUN — อ่าน PORT จาก environment variable (Render จะ inject ให้อัตโนมัติ) =====
port = int(os.environ.get("PORT", 8080))

ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=port,
    host="0.0.0.0",   # ต้องเปิดให้รับ traffic จากภายนอกได้
)
