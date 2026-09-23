import os
import datetime
import tkinter as tk
from tkinter import filedialog
import flet as ft
from database import save_data

def build_todo_mobile(page: ft.Page, app_data: dict):
    todos = app_data.get("todos", [])
    border_col = ft.Colors.OUTLINE

    def open_image_preview(img_path):
        if not img_path or not os.path.exists(img_path):
            return

        def close_preview(e):
            if preview_overlay in page.overlay:
                page.overlay.remove(preview_overlay)
                page.update()

        preview_overlay = ft.Container(
            content=ft.Column(
                [
                    ft.Image(
                        src=img_path,
                        fit="contain",
                        expand=True,
                    ),
                    ft.Text(
                        "Click anywhere to close", 
                        size=12,
                        italic=True
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            bgcolor="#CC000000",
            alignment=ft.Alignment(0, 0),
            padding=20,
            on_click=close_preview
        )

        page.overlay.append(preview_overlay)
        page.update()

    def open_picker(picker):
        try:
            if hasattr(page, "open"):
                page.open(picker)
            elif hasattr(picker, "pick_date"):
                picker.pick_date()
            elif hasattr(picker, "pick_time"):
                picker.pick_time()
            else:
                picker.open = True
                page.update()
        except Exception:
            picker.open = True
            page.update()

    def open_todo_dialog(todo_item=None):
        is_edit = todo_item is not None

        task_input = ft.TextField(
            label="Activity Name",
            value=todo_item.get("task", "") if is_edit else "",
            border_color=border_col,
            prefix_icon=ft.Icons.TASK_ALT,
            autofocus=True,
            dense=True,
            text_size=12,
            label_style=ft.TextStyle(size=11)
        )

        priority_dropdown = ft.Dropdown(
            label="Priority",
            value=todo_item.get("priority", "Medium") if is_edit else "Medium",
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            border_color=border_col,
            dense=True,
            text_size=12,
            label_style=ft.TextStyle(size=11),
            expand=True
        )

        start_val, end_val = "", ""
        if is_edit:
            time_val = todo_item.get("time", "")
            if " - " in time_val:
                parts = time_val.split(" - ")
                start_val, end_val = parts[0], parts[1]
            elif time_val.startswith("s.d "):
                end_val = time_val.replace("s.d ", "")
            else:
                start_val = time_val

        start_date_val = todo_item.get("start_date") or todo_item.get("date", "") if is_edit else ""
        end_date_val = todo_item.get("end_date", "") if is_edit else ""

        start_date_field = ft.TextField(
            label="Start Date",
            value=start_date_val,
            read_only=True,
            border_color=border_col,
            on_click=lambda e: open_picker(start_date_picker),
            dense=True,
            text_size=11,
            label_style=ft.TextStyle(size=10),
            expand=True
        )

        end_date_field = ft.TextField(
            label="End Date",
            value=end_date_val,
            read_only=True,
            border_color=border_col,
            on_click=lambda e: open_picker(end_date_picker),
            dense=True,
            text_size=11,
            label_style=ft.TextStyle(size=10),
            expand=True
        )

        start_time_field = ft.TextField(
            label="Start Time",
            value=start_val,
            read_only=True,
            border_color=border_col,
            on_click=lambda e: open_picker(start_time_picker),
            dense=True,
            text_size=11,
            label_style=ft.TextStyle(size=10),
            expand=True
        )

        end_time_field = ft.TextField(
            label="End Time",
            value=end_val,
            read_only=True,
            border_color=border_col,
            on_click=lambda e: open_picker(end_time_picker),
            dense=True,
            text_size=11,
            label_style=ft.TextStyle(size=10),
            expand=True
        )

        def on_start_date_change(e):
            if start_date_picker.value:
                adj = start_date_picker.value + datetime.timedelta(hours=12)
                start_date_field.value = adj.strftime("%d %b %Y")
                start_date_field.update()

        def on_end_date_change(e):
            if end_date_picker.value:
                adj = end_date_picker.value + datetime.timedelta(hours=12)
                end_date_field.value = adj.strftime("%d %b %Y")
                end_date_field.update()

        def on_start_time_change(e):
            if start_time_picker.value:
                start_time_field.value = start_time_picker.value.strftime("%H:%M")
                start_time_field.update()

        def on_end_time_change(e):
            if end_time_picker.value:
                end_time_field.value = end_time_picker.value.strftime("%H:%M")
                end_time_field.update()

        start_date_picker = ft.DatePicker(on_change=on_start_date_change)
        end_date_picker = ft.DatePicker(on_change=on_end_date_change)
        start_time_picker = ft.TimePicker(on_change=on_start_time_change)
        end_time_picker = ft.TimePicker(on_change=on_end_time_change)

        page.overlay.extend([
            start_date_picker, end_date_picker,
            start_time_picker, end_time_picker
        ])

        image_path_store = {"path": todo_item.get("image", "") if is_edit else ""}

        img_btn_text = ft.Text("Change" if (is_edit and image_path_store["path"]) else "Image", size=12)

        def file_picker_action(e):
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            fpath = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
            )
            root.destroy()
            if fpath:
                image_path_store["path"] = fpath
                img_btn_text.value = "Attached"
                img_btn.icon = ft.Icons.CHECK
                page.update()

        img_btn = ft.OutlinedButton(
            content=img_btn_text,
            icon=ft.Icons.IMAGE,
            on_click=file_picker_action,
            height=40,
            style=ft.ButtonStyle(
                padding=ft.Padding(8, 0, 8, 0),
                shape=ft.RoundedRectangleBorder(radius=8)
            ),
            expand=True
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_task(e):
            if not task_input.value.strip():
                return

            st = start_time_field.value.strip()
            et = end_time_field.value.strip()
            time_str = ""
            if st and et:
                time_str = f"{st} - {et}"
            elif st:
                time_str = st
            elif et:
                time_str = f"s.d {et}"

            if is_edit:
                todo_item["task"] = task_input.value.strip()
                todo_item["start_date"] = start_date_field.value.strip()
                todo_item["end_date"] = end_date_field.value.strip()
                todo_item["time"] = time_str
                todo_item["priority"] = priority_dropdown.value
                todo_item["image"] = image_path_store["path"]
                if "date" in todo_item:
                    del todo_item["date"]
            else:
                new_item = {
                    "task": task_input.value.strip(),
                    "start_date": start_date_field.value.strip(),
                    "end_date": end_date_field.value.strip(),
                    "time": time_str,
                    "priority": priority_dropdown.value or "Medium",
                    "image": image_path_store["path"],
                    "completed": False
                }
                todos.insert(0, new_item)

            app_data["todos"] = todos
            save_data(app_data)

            dialog.open = False
            page.update()
            render_todos()

        dialog = ft.AlertDialog(
            title=ft.Text("Edit Activity" if is_edit else "New Activity", weight=ft.FontWeight.BOLD, size=16),
            content=ft.Container(
                content=ft.Column(
                    [
                        task_input,
                        ft.Row([priority_dropdown, img_btn], spacing=8),
                        ft.Row([start_date_field, end_date_field], spacing=8),
                        ft.Row([start_time_field, end_time_field], spacing=8),
                    ],
                    tight=True,
                    spacing=10
                ),
                padding=ft.Padding(0, 5, 0, 0)
            ),
            actions=[
                ft.TextButton(content=ft.Text("Cancel"), on_click=close_dialog),
                ft.FilledButton(content=ft.Text("Save"), on_click=save_task),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    todo_list_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_todos():
        todo_list_column.controls.clear()
        if not todos:
            todo_list_column.controls.append(
                ft.Container(
                    content=ft.Text("No activities...", italic=True),
                    padding=20
                )
            )
        else:
            for item in todos:
                def make_checkbox_handler(todo_item):
                    return lambda e: toggle_todo(todo_item, e.control.value)

                def make_delete_handler(todo_item):
                    return lambda e: delete_todo(todo_item)

                def make_edit_handler(todo_item):
                    return lambda e: open_todo_dialog(todo_item)

                def make_image_click_handler(path):
                    return lambda e: open_image_preview(path)

                is_completed = item.get("completed", False)

                chk = ft.Checkbox(
                    value=is_completed,
                    on_change=make_checkbox_handler(item)
                )

                priority = item.get("priority", "Medium")
                if priority == "High":
                    badge_color = "red800"
                elif priority == "Medium":
                    badge_color = "orange800"
                elif priority == "Low":
                    badge_color = "green800"
                else:
                    badge_color = "grey700"

                priority_badge = ft.Container(
                    content=ft.Container(
                        width=8,
                        height=8,
                        bgcolor=badge_color,
                        border_radius=4,
                    ),
                    padding=ft.Padding(0, 0, 2, 0),
                    tooltip=f"Priority: {priority}"
                )

                edit_btn = ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color="blue400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Edit",
                    on_click=make_edit_handler(item)
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Delete",
                    on_click=make_delete_handler(item)
                )

                # Format Tanggal & Waktu
                start_d = item.get("start_date") or item.get("date", "")
                end_d = item.get("end_date", "")

                date_str = ""
                if start_d and end_d:
                    date_str = start_d if start_d == end_d else f"{start_d} - {end_d}"
                elif start_d:
                    date_str = start_d
                elif end_d:
                    date_str = f"s.d {end_d}"

                details_controls = []
                if date_str:
                    details_controls.append(
                        ft.Row([
                            ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=12, color=ft.Colors.OUTLINE),
                            ft.Text(date_str, size=11, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], spacing=4)
                    )

                if item.get("time"):
                    details_controls.append(
                        ft.Row([
                            ft.Icon(ft.Icons.ACCESS_TIME_OUTLINED, size=12, color=ft.Colors.OUTLINE),
                            ft.Text(item["time"], size=11, color=ft.Colors.ON_SURFACE_VARIANT)
                        ], spacing=4)
                    )

                img_path = item.get("image", "")
                if img_path and isinstance(img_path, str) and img_path.strip() and os.path.exists(img_path):
                    details_controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Icon(ft.Icons.IMAGE_OUTLINED, size=12, color=ft.Colors.OUTLINE),
                                ft.Text("View Attached Image", size=11, color=ft.Colors.BLUE_400, underline=True)
                            ], spacing=4),
                            on_click=make_image_click_handler(img_path),
                            ink=True
                        )
                    )

                # Container Detail
                details_container = ft.Column(
                    controls=details_controls,
                    spacing=4,
                    visible=False
                )

                def toggle_details(e, target_col=details_container):
                    target_col.visible = not target_col.visible
                    page.update()

                # Text dengan expand=True dan max_lines=1 agar teks terpotong rapi dengan "..." jika terlalu panjang
                task_title_text = ft.Text(
                    item.get("task", ""),
                    size=12,
                    weight=ft.FontWeight.W_600,
                    opacity=0.5 if is_completed else 1.0,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH if is_completed else ft.TextDecoration.NONE
                    ),
                    overflow=ft.TextOverflow.ELLIPSIS,
                    max_lines=1,
                    expand=True
                )

                title_click_area = ft.Container(
                    content=ft.Row([task_title_text], expand=True),
                    on_click=toggle_details,
                    expand=True,
                    padding=ft.Padding(0, 4, 0, 4)
                )

                left_section = ft.Row(
                    [chk, title_click_area],
                    alignment=ft.MainAxisAlignment.START,
                    expand=True,
                    spacing=2,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )

                right_controls = ft.Row(
                    [priority_badge, edit_btn, del_btn],
                    spacing=2,
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )

                card_content = ft.Column(
                    [
                        ft.Row(
                            [left_section, right_controls],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            vertical_alignment=ft.CrossAxisAlignment.CENTER
                        ),
                        ft.Container(
                            content=details_container,
                            padding=ft.Padding(36, 0, 0, 4)
                        ) if details_controls else ft.Container()
                    ],
                    spacing=2
                )

                card = ft.Container(
                    content=card_content,
                    padding=ft.Padding(6, 4, 6, 6),
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                todo_list_column.controls.append(card)

            todo_list_column.controls.append(ft.Container(height=60))

        page.update()

    def toggle_todo(todo_item, value):
        todo_item["completed"] = value
        app_data["todos"] = todos
        save_data(app_data)
        render_todos()

    def delete_todo(todo_item):
        todos.remove(todo_item)
        app_data["todos"] = todos
        save_data(app_data)
        render_todos()

    render_todos()

    main_content = ft.Column(
        [
            todo_list_column
        ],
        expand=True,
        spacing=0
    )

    fab_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        foreground_color=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        tooltip="New Task",
        on_click=lambda e: open_todo_dialog(None)
    )

    return ft.Stack(
        [
            main_content,
            ft.Container(
                content=fab_button,
                bottom=16,
                right=16
            )
        ],
        expand=True
    )