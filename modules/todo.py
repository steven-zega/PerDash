import os
import datetime
import tkinter as tk
from tkinter import filedialog
import flet as ft
from database import save_data

def build_todo(page: ft.Page, app_data: dict):
    todos = app_data.get("todos", [])

    # Warna outline dinamis dari Flet Theme
    border_col = ft.Colors.OUTLINE

    task_input = ft.TextField(
        hint_text="Title / Activity Name",
        label="Activity",
        expand=True,
        autofocus=True,
        prefix_icon=ft.Icons.TASK_ALT,
        border_color=border_col
    )

    # --- PICKER HANDLERS (MAIN FORM) ---
    def on_start_date_change(e):
        if start_date_picker.value:
            adjusted = start_date_picker.value + datetime.timedelta(hours=12)
            start_date_input.value = adjusted.strftime("%d %b %Y")
            start_date_input.update()

    def on_end_date_change(e):
        if end_date_picker.value:
            adjusted = end_date_picker.value + datetime.timedelta(hours=12)
            end_date_input.value = adjusted.strftime("%d %b %Y")
            end_date_input.update()

    def on_start_time_change(e):
        if start_time_picker.value:
            start_time_input.value = start_time_picker.value.strftime("%H:%M")
            start_time_input.update()

    def on_end_time_change(e):
        if end_time_picker.value:
            end_time_input.value = end_time_picker.value.strftime("%H:%M")
            end_time_input.update()

    start_date_picker = ft.DatePicker(on_change=on_start_date_change)
    end_date_picker = ft.DatePicker(on_change=on_end_date_change)
    start_time_picker = ft.TimePicker(on_change=on_start_time_change)
    end_time_picker = ft.TimePicker(on_change=on_end_time_change)

    page.overlay.extend([start_date_picker, end_date_picker, start_time_picker, end_time_picker])

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

    # --- FORM INPUT CONTROLS ---
    priority_dropdown = ft.Dropdown(
        label="Priority",
        hint_text="Priority",
        width=110,
        value="Medium",
        text_size=12,
        label_style=ft.TextStyle(size=11),
        border_color=border_col,
        options=[
            ft.dropdown.Option("High"),
            ft.dropdown.Option("Medium"),
            ft.dropdown.Option("Low"),
        ]
    )

    start_date_input = ft.TextField(
        label="Start Date",
        width=120,
        text_size=11,
        label_style=ft.TextStyle(size=10),
        read_only=True,
        prefix_icon=ft.Icons.CALENDAR_MONTH,
        border_color=border_col,
        on_click=lambda e: open_picker(start_date_picker)
    )

    end_date_input = ft.TextField(
        label="End Date",
        width=120,
        text_size=11,
        label_style=ft.TextStyle(size=10),
        read_only=True,
        prefix_icon=ft.Icons.EVENT,
        border_color=border_col,
        on_click=lambda e: open_picker(end_date_picker)
    )

    start_time_input = ft.TextField(
        label="Start Time",
        width=110,
        text_size=11,                       
        label_style=ft.TextStyle(size=10),   
        read_only=True,
        prefix_icon=ft.Icons.ACCESS_TIME,
        border_color=border_col,
        on_click=lambda e: open_picker(start_time_picker)
    )

    end_time_input = ft.TextField(
        label="End Time",
        width=110,
        text_size=11,                     
        label_style=ft.TextStyle(size=10),   
        read_only=True,
        prefix_icon=ft.Icons.ACCESS_TIME_FILLED,
        border_color=border_col,
        on_click=lambda e: open_picker(end_time_picker)
    )

    selected_image = {"path": ""}

    def open_file_picker(e):
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        file_path = filedialog.askopenfilename(
            title="Insert Image",
            filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
        )
        root.destroy()

        if file_path:
            selected_image["path"] = file_path
            image_btn.text = "Image Chosen"
            image_btn.icon = ft.Icons.CHECK
            page.update()

    image_btn = ft.OutlinedButton(
        "Insert Image",
        icon=ft.Icons.IMAGE,
        on_click=open_file_picker,
        height=48
    )

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
            padding=30,
            on_click=close_preview
        )

        page.overlay.append(preview_overlay)
        page.update()

    # --- DIALOG EDIT TASK (RAPI & SIMETRIS) ---
    def open_edit_dialog(todo_item):
        edit_task_input = ft.TextField(
            label="Activity Name",
            value=todo_item.get("task", ""),
            border_color=border_col,
            prefix_icon=ft.Icons.TASK_ALT
        )
        
        edit_priority_dropdown = ft.Dropdown(
            label="Priority",
            value=todo_item.get("priority", "Medium"),
            options=[
                ft.dropdown.Option("High"),
                ft.dropdown.Option("Medium"),
                ft.dropdown.Option("Low"),
            ],
            border_color=border_col,
            expand=True
        )

        # Parse Waktu
        time_val = todo_item.get("time", "")
        start_val, end_val = "", ""
        if " - " in time_val:
            parts = time_val.split(" - ")
            start_val, end_val = parts[0], parts[1]
        elif time_val.startswith("s.d "):
            end_val = time_val.replace("s.d ", "")
        else:
            start_val = time_val

        # Parse Tanggal
        start_date_val = todo_item.get("start_date") or todo_item.get("date", "")
        end_date_val = todo_item.get("end_date", "")

        edit_start_date = ft.TextField(
            label="Start Date",
            value=start_date_val,
            read_only=True,
            prefix_icon=ft.Icons.CALENDAR_MONTH,
            border_color=border_col,
            on_click=lambda e: open_picker(edit_start_date_picker),
            expand=True
        )

        edit_end_date = ft.TextField(
            label="End Date",
            value=end_date_val,
            read_only=True,
            prefix_icon=ft.Icons.EVENT,
            border_color=border_col,
            on_click=lambda e: open_picker(edit_end_date_picker),
            expand=True
        )

        edit_start_time = ft.TextField(
            label="Start Time",
            value=start_val,
            read_only=True,
            prefix_icon=ft.Icons.ACCESS_TIME,
            border_color=border_col,
            on_click=lambda e: open_picker(edit_start_time_picker),
            expand=True
        )

        edit_end_time = ft.TextField(
            label="End Time",
            value=end_val,
            read_only=True,
            prefix_icon=ft.Icons.ACCESS_TIME_FILLED,
            border_color=border_col,
            on_click=lambda e: open_picker(edit_end_time_picker),
            expand=True
        )

        def on_edit_start_date_change(e):
            if edit_start_date_picker.value:
                adj = edit_start_date_picker.value + datetime.timedelta(hours=12)
                edit_start_date.value = adj.strftime("%d %b %Y")
                edit_start_date.update()

        def on_edit_end_date_change(e):
            if edit_end_date_picker.value:
                adj = edit_end_date_picker.value + datetime.timedelta(hours=12)
                edit_end_date.value = adj.strftime("%d %b %Y")
                edit_end_date.update()

        def on_edit_start_time_change(e):
            if edit_start_time_picker.value:
                edit_start_time.value = edit_start_time_picker.value.strftime("%H:%M")
                edit_start_time.update()

        def on_edit_end_time_change(e):
            if edit_end_time_picker.value:
                edit_end_time.value = edit_end_time_picker.value.strftime("%H:%M")
                edit_end_time.update()

        edit_start_date_picker = ft.DatePicker(on_change=on_edit_start_date_change)
        edit_end_date_picker = ft.DatePicker(on_change=on_edit_end_date_change)
        edit_start_time_picker = ft.TimePicker(on_change=on_edit_start_time_change)
        edit_end_time_picker = ft.TimePicker(on_change=on_edit_end_time_change)

        page.overlay.extend([
            edit_start_date_picker, edit_end_date_picker, 
            edit_start_time_picker, edit_end_time_picker
        ])

        edit_image_path = {"path": todo_item.get("image", "")}

        def edit_file_picker(e):
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)
            fpath = filedialog.askopenfilename(
                title="Change Image",
                filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.webp;*.bmp")]
            )
            root.destroy()
            if fpath:
                edit_image_path["path"] = fpath
                edit_img_btn.text = "Image Updated"
                edit_img_btn.icon = ft.Icons.CHECK
                page.update()

        edit_img_btn = ft.OutlinedButton(
            "Change Image" if edit_image_path["path"] else "Add Image",
            icon=ft.Icons.IMAGE,
            on_click=edit_file_picker,
            height=48,
            expand=True
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_edit(e):
            if not edit_task_input.value.strip():
                return

            st = edit_start_time.value.strip()
            et = edit_end_time.value.strip()
            t_str = ""
            if st and et:
                t_str = f"{st} - {et}"
            elif st:
                t_str = st
            elif et:
                t_str = f"s.d {et}"

            todo_item["task"] = edit_task_input.value.strip()
            todo_item["start_date"] = edit_start_date.value.strip()
            todo_item["end_date"] = edit_end_date.value.strip()
            todo_item["time"] = t_str
            todo_item["priority"] = edit_priority_dropdown.value
            todo_item["image"] = edit_image_path["path"]

            # Membersihkan key lama jika ada
            if "date" in todo_item:
                del todo_item["date"]

            app_data["todos"] = todos
            save_data(app_data)

            dialog.open = False
            page.update()
            render_todos()

        # Layout Dialog disusun per-baris secara rapi & simetris
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Activity", weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    [
                        edit_task_input,
                        ft.Row([edit_priority_dropdown, edit_img_btn], spacing=10),
                        ft.Row([edit_start_date, edit_end_date], spacing=10),
                        ft.Row([edit_start_time, edit_end_time], spacing=10),
                    ],
                    tight=True,
                    spacing=14
                ),
                width=460
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save", on_click=save_edit),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    todo_list_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

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
                    return lambda e: open_edit_dialog(todo_item)

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
                        width=12,
                        height=12,
                        bgcolor=badge_color,
                        border_radius=3,
                    ),
                    padding=ft.padding.Padding(0, 0, 4, 0),
                    tooltip=f"Priority: {priority}"
                )

                edit_btn = ft.IconButton(
                    icon=ft.Icons.EDIT_OUTLINED,
                    icon_color="blue400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Edit",
                    on_click=make_edit_handler(item)
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Delete",
                    on_click=make_delete_handler(item)
                )

                image_widget = None
                img_path = item.get("image", "")
                if img_path and isinstance(img_path, str) and img_path.strip() and os.path.exists(img_path):
                    image_widget = ft.Container(
                        content=ft.Image(
                            src=img_path,
                            width=45,
                            height=45,
                            fit="cover",
                            border_radius=6
                        ),
                        on_click=make_image_click_handler(img_path),
                        tooltip="Click to enlarge image",
                        border_radius=6,
                        ink=True
                    )

                task_title_text = ft.Text(
                    item["task"],
                    size=15,
                    weight=ft.FontWeight.W_600,
                    opacity=0.5 if is_completed else 1.0,
                    style=ft.TextStyle(
                        decoration=ft.TextDecoration.LINE_THROUGH if is_completed else ft.TextDecoration.NONE
                    ),
                    overflow=ft.TextOverflow.ELLIPSIS
                )

                # Format Tampilan Tanggal (Mulai & Berakhir)
                start_d = item.get("start_date") or item.get("date", "")
                end_d = item.get("end_date", "")

                date_str = ""
                if start_d and end_d:
                    date_str = start_d if start_d == end_d else f"{start_d} - {end_d}"
                elif start_d:
                    date_str = start_d
                elif end_d:
                    date_str = f"s.d {end_d}"

                meta_controls = []
                if date_str:
                    meta_controls.extend([
                        ft.Icon(ft.Icons.CALENDAR_TODAY_OUTLINED, size=13),
                        ft.Text(date_str, size=12)
                    ])

                if item.get("time"):
                    if meta_controls:
                        meta_controls.append(ft.Text("•", size=12))
                    meta_controls.extend([
                        ft.Icon(ft.Icons.ACCESS_TIME_OUTLINED, size=13),
                        ft.Text(item["time"], size=12)
                    ])

                task_details_column = ft.Column(
                    controls=[
                        task_title_text,
                        ft.Row(meta_controls, spacing=5, alignment=ft.MainAxisAlignment.START) if meta_controls else ft.Container()
                    ],
                    spacing=3,
                    expand=True
                )

                left_controls = [chk, task_details_column]
                if image_widget:
                    left_controls.insert(0, image_widget)

                right_controls = ft.Row(
                    [priority_badge, edit_btn, del_btn],
                    spacing=4,
                    alignment=ft.MainAxisAlignment.END,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER
                )

                card = ft.Container(
                    content=ft.Row(
                        [
                            ft.Row(left_controls, alignment=ft.MainAxisAlignment.START, expand=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            right_controls
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    ),
                    padding=ft.padding.Padding(12, 8, 12, 8),
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                todo_list_column.controls.append(card)
        
        page.update()

    def add_todo(e):
        if not task_input.value.strip():
            return
        
        start_t = start_time_input.value.strip()
        end_t = end_time_input.value.strip()
        time_str = ""
        if start_t and end_t:
            time_str = f"{start_t} - {end_t}"
        elif start_t:
            time_str = start_t
        elif end_t:
            time_str = f"s.d {end_t}"

        new_item = {
            "task": task_input.value.strip(),
            "start_date": start_date_input.value.strip(),
            "end_date": end_date_input.value.strip(),
            "time": time_str,
            "priority": priority_dropdown.value or "Medium",
            "image": selected_image["path"],
            "completed": False
        }
        todos.insert(0, new_item)
        app_data["todos"] = todos
        save_data(app_data)

        # Reset Form Input
        task_input.value = ""
        start_date_input.value = ""
        end_date_input.value = ""
        start_time_input.value = ""
        end_time_input.value = ""
        priority_dropdown.value = "Medium"
        selected_image["path"] = ""
        image_btn.text = "Insert Image"
        image_btn.icon = ft.Icons.IMAGE

        render_todos()

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

    add_btn = ft.FilledButton(
        "Add Task",
        icon=ft.Icons.ADD,
        on_click=add_todo,
        height=48
    )

    form_row_1 = ft.Row([task_input])

    left_options = ft.Row(
        [priority_dropdown, start_date_input, end_date_input, start_time_input, end_time_input, image_btn],
        spacing=8,
        wrap=True
    )

    form_row_2 = ft.Row(
        controls=[left_options, add_btn],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER
    )
    
    form_card = ft.Container(
        content=ft.Column([form_row_1, form_row_2], spacing=12),
        padding=16,
        border_radius=12,
        bgcolor="surfaceVariant"
    )

    render_todos()

    return ft.Column([
        ft.Text("To-Do List", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_card,
        ft.Divider(height=15, color="transparent"),
        todo_list_column
    ], expand=True)