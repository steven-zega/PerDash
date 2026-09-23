import webbrowser
import flet as ft
from database import save_data

def build_links_mobile(page: ft.Page, app_data: dict):
    links = app_data.get("links", [])
    border_col = ft.Colors.OUTLINE

    def open_add_dialog(e=None):
        label_style = ft.TextStyle(size=12)
        
        title_input = ft.TextField(
            label="Title / Name",
            label_style=label_style,
            text_size=12,
            border_color=border_col,
            autofocus=True,
            dense=True
        )

        url_input = ft.TextField(
            label="URL",
            label_style=label_style,
            text_size=12,
            border_color=border_col,
            dense=True
        )

        desc_input = ft.TextField(
            label="Description (Optional)",
            label_style=label_style,
            text_size=12,
            border_color=border_col,
            multiline=True,
            max_lines=2,
            dense=True
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_link_action(e):
            if not title_input.value.strip() or not url_input.value.strip():
                return

            raw_url = url_input.value.strip()
            if not (raw_url.startswith("http://") or raw_url.startswith("https://")):
                raw_url = "https://" + raw_url

            new_item = {
                "title": title_input.value.strip(),
                "url": raw_url,
                "desc": desc_input.value.strip()
            }

            links.insert(0, new_item)
            app_data["links"] = links
            save_data(app_data)

            dialog.open = False
            page.update()
            render_links()

        dialog = ft.AlertDialog(
            title=ft.Text("New Link Bookmark", weight=ft.FontWeight.BOLD, size=15),
            content=ft.Container(
                content=ft.Column(
                    [
                        title_input,
                        url_input,
                        desc_input
                    ],
                    tight=True,
                    spacing=8
                ),
                width=240,
                padding=5
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save", on_click=save_link_action),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    links_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_links():
        links_column.controls.clear()
        if not links:
            links_column.controls.append(
                ft.Container(
                    content=ft.Text("No links saved...", italic=True),
                    padding=20
                )
            )
        else:
            for item in links:
                def make_open_handler(target_url):
                    return lambda e: webbrowser.open(target_url)

                def make_delete_handler(link_item):
                    return lambda e: delete_link(link_item)

                open_btn = ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    icon_color="blue400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Open Link in Browser",
                    on_click=make_open_handler(item["url"])
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Remove Link",
                    on_click=make_delete_handler(item)
                )

                link_icon = ft.Container(
                    content=ft.Icon(ft.Icons.LANGUAGE, color="blue400", size=18),
                    padding=6,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8
                )

                details = ft.Column([
                    ft.Text(item["title"], weight=ft.FontWeight.BOLD, size=13, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(item["url"], color="blue400", size=10, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(item.get("desc", ""), size=10, opacity=0.7, overflow=ft.TextOverflow.ELLIPSIS) if item.get("desc") else ft.Container()
                ], expand=True, spacing=2)

                card_content = ft.Row([
                    ft.Row([link_icon, details], expand=True, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([open_btn, del_btn], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

                card = ft.Container(
                    content=card_content,
                    padding=8,
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                links_column.controls.append(card)

            links_column.controls.append(ft.Container(height=60))

        page.update()

    def delete_link(link_item):
        links.remove(link_item)
        app_data["links"] = links
        save_data(app_data)
        render_links()

    render_links()

    main_content = ft.Column(
        [
            links_column
        ],
        expand=True,
        spacing=0
    )

    fab_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        foreground_color=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        tooltip="New Link",
        on_click=open_add_dialog
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