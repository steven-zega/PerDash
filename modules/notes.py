import flet as ft
from database import save_data

def build_notes(page: ft.Page, app_data: dict):
    notes = app_data.get("notes", [])

    # Menggunakan warna outline tema dinamis
    border_col = ft.Colors.OUTLINE

    main_layout = ft.Column(expand=True)

    def show_grid_view():
        grid = ft.GridView(
            expand=True,
            runs_count=4,            
            child_aspect_ratio=1.0, 
            spacing=12,
            run_spacing=12,
        )

        if not notes:
            grid_content = ft.Container(
                content=ft.Text("No notes saved...", italic=True),
                padding=20,
                alignment=ft.Alignment(0, 0)  
            )
        else:
            # Menggunakan warna variant outline agar border kartu catatan terlihat rapi di kedua mode
            card_border_color = ft.Colors.OUTLINE_VARIANT

            for item in notes:
                def make_card(note_item):
                    def on_card_click(e):
                        if note_item in notes:
                            show_editor_view(note_item)

                    content_text = note_item.get("content", "")
                    is_long_note = len(content_text) > 90

                    card_controls = [
                        ft.Text(
                            note_item["title"],
                            weight=ft.FontWeight.BOLD,
                            size=15,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1
                        ),
                        ft.Divider(height=1),
                        ft.Text(
                            content_text,
                            size=12,
                            opacity=0.8,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=4,
                            expand=True
                        )
                    ]

                    if is_long_note:
                        card_controls.append(
                            ft.Text("Read more...", color="amber400", size=11, italic=True)
                        )

                    return ft.Container(
                        content=ft.Column(card_controls, spacing=6, expand=True),
                        padding=14,
                        border_radius=12,
                        bgcolor="surfaceVariant",
                        border=ft.Border.all(1, card_border_color),
                        on_click=on_card_click,
                        ink=True
                    )

                grid.controls.append(make_card(item))
            grid_content = grid

        top_bar = ft.Row([
            ft.Text("Notes", size=24, weight=ft.FontWeight.BOLD),
            ft.FilledButton(
                "New Note",
                icon=ft.Icons.ADD,
                on_click=lambda e: show_editor_view(None)
            )
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        main_layout.controls = [
            top_bar,
            ft.Divider(height=10, color="transparent"),
            grid_content
        ]
        page.update()

    def show_editor_view(note_item=None):
        is_edit = note_item is not None

        title_field = ft.TextField(
            label="Title",
            value=note_item["title"] if is_edit else "",
            prefix_icon=ft.Icons.TITLE,
            border_color=border_col
        )

        content_field = ft.TextField(
            label="Content",
            value=note_item.get("content", "") if is_edit else "",
            multiline=True,
            min_lines=12,
            expand=True,
            prefix_icon=ft.Icons.EDIT_NOTE,
            border_color=border_col
        )

        def save_action(e):
            if not title_field.value.strip() or not content_field.value.strip():
                return

            if is_edit:
                note_item["title"] = title_field.value.strip()
                note_item["content"] = content_field.value.strip()
            else:
                new_note = {
                    "title": title_field.value.strip(),
                    "content": content_field.value.strip()
                }
                # Menggunakan insert(0, ...) agar catatan baru berada di posisi paling atas
                notes.insert(0, new_note)

            app_data["notes"] = notes
            save_data(app_data)
            show_grid_view()

        def delete_action(e):
            if is_edit and note_item in notes:
                notes.remove(note_item)
                app_data["notes"] = notes
                save_data(app_data)
            show_grid_view()

        action_buttons = []

        if is_edit:
            action_buttons.append(
                ft.OutlinedButton(
                    "Delete",
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    style=ft.ButtonStyle(color="red400"),
                    on_click=delete_action
                )
            )

        action_buttons.append(
            ft.FilledButton(
                "Save",
                icon=ft.Icons.SAVE,
                on_click=save_action
            )
        )

        editor_header = ft.Row([
            ft.Row([
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK,
                    tooltip="Back",
                    on_click=lambda e: show_grid_view()
                ),
                ft.Text("Edit" if is_edit else "New note", size=22, weight=ft.FontWeight.BOLD)
            ], spacing=10),
            ft.Row(action_buttons, spacing=10)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        editor_card = ft.Container(
            content=ft.Column([
                title_field,
                content_field
            ], spacing=12, expand=True),
            padding=16,
            border_radius=12,
            bgcolor="surfaceVariant",
            expand=True
        )

        main_layout.controls = [
            editor_header,
            ft.Divider(height=10, color="transparent"),
            editor_card
        ]
        page.update()

    show_grid_view()

    return main_layout