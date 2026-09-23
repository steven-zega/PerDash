import flet as ft
from database import save_data

def build_notes_mobile(page: ft.Page, app_data: dict):
    notes = app_data.get("notes", [])

    main_layout = ft.Column(expand=True, spacing=0)

    def show_grid_view():
        grid_items = []
        
        if not notes:
            grid_content = ft.Container(
                content=ft.Text("No notes saved...", italic=True, opacity=0.6),
                padding=20,
                alignment=ft.Alignment(0, 0)
            )
        else:
            for item in notes:
                def make_card(note_item):
                    def on_card_click(e):
                        if note_item in notes:
                            show_editor_view(note_item)

                    content_text = note_item.get("content", "")
                    is_long_note = len(content_text) > 60

                    card_controls = [
                        ft.Text(
                            note_item.get("title", "Untitled"),
                            weight=ft.FontWeight.BOLD,
                            size=13,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=1
                        ),
                        ft.Divider(height=1, thickness=1, color=ft.Colors.OUTLINE_VARIANT),
                        ft.Text(
                            content_text,
                            size=11,
                            opacity=0.8,
                            overflow=ft.TextOverflow.ELLIPSIS,
                            max_lines=3,
                            expand=True
                        )
                    ]

                    if is_long_note:
                        card_controls.append(
                            ft.Text("Read more...", color="amber400", size=10, italic=True)
                        )

                    return ft.Container(
                        content=ft.Column(card_controls, spacing=4, expand=True),
                        padding=10,
                        border_radius=8,
                        bgcolor="surfaceVariant",
                        border=ft.Border.all(1, ft.Colors.OUTLINE_VARIANT),
                        on_click=on_card_click,
                        ink=True
                    )

                grid_items.append(make_card(item))

            grid_content = ft.GridView(
                controls=grid_items,
                max_extent=160,
                child_aspect_ratio=0.85,
                spacing=8,
                run_spacing=8,
                expand=True
            )

        fab_button = ft.FloatingActionButton(
            icon=ft.Icons.ADD,
            bgcolor=ft.Colors.BLUE_600,
            foreground_color=ft.Colors.WHITE,
            shape=ft.CircleBorder(),
            tooltip="New Note",
            on_click=lambda e: show_editor_view(None)
        )

        main_layout.controls = [
            ft.Stack(
                [
                    grid_content,
                    ft.Container(
                        content=fab_button,
                        bottom=16,
                        right=16
                    )
                ],
                expand=True
            )
        ]
        page.update()

    def show_editor_view(note_item=None):
        is_edit = note_item is not None

        title_field = ft.TextField(
            label="Title",
            value=note_item["title"] if is_edit else "",
            label_style=ft.TextStyle(size=12),
            text_size=13,
            dense=True,
            border_color=ft.Colors.OUTLINE
        )

        content_field = ft.TextField(
            label="Content",
            value=note_item.get("content", "") if is_edit else "",
            multiline=True,
            min_lines=8,
            max_lines=12,
            expand=True,
            label_style=ft.TextStyle(size=12),
            text_size=12,
            border_color=ft.Colors.OUTLINE
        )

        def save_action(e):
            if not title_field.value.strip() and not content_field.value.strip():
                show_grid_view()
                return

            if is_edit:
                note_item["title"] = title_field.value.strip() or "Untitled"
                note_item["content"] = content_field.value.strip()
            else:
                new_note = {
                    "title": title_field.value.strip() or "Untitled",
                    "content": content_field.value.strip()
                }
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
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=20,
                    on_click=delete_action
                )
            )

        action_buttons.append(
            ft.FilledButton(
                content=ft.Row([ft.Icon(ft.Icons.SAVE, size=14), ft.Text("Save", size=12)], spacing=4),
                on_click=save_action,
                style=ft.ButtonStyle(padding=ft.Padding(12, 6, 12, 6))
            )
        )

        editor_header = ft.Row(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            icon_size=20,
                            on_click=lambda e: show_grid_view()
                        ),
                        ft.Text("Edit" if is_edit else "New Note", weight=ft.FontWeight.BOLD, size=15)
                    ],
                    spacing=6
                ),
                ft.Row(action_buttons, spacing=4)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        editor_card = ft.Column(
            [
                editor_header,
                title_field,
                content_field
            ],
            spacing=10,
            expand=True
        )

        main_layout.controls = [editor_card]
        page.update()

    show_grid_view()
    return main_layout