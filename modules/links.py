import webbrowser
import flet as ft
from database import save_data

def build_links(page: ft.Page, app_data: dict):
    links = app_data.get("links", [])

    # Menggunakan warna outline dinamis dari Flet Theme
    border_col = ft.Colors.OUTLINE

    title_input = ft.TextField(
        label="Title / Name",
        expand=True,
        prefix_icon=ft.Icons.TITLE,
        border_color=border_col
    )
    url_input = ft.TextField(
        label="URL",
        expand=True,
        prefix_icon=ft.Icons.LINK,
        border_color=border_col
    )

    desc_input = ft.TextField(
        label="Description",
        expand=True,
        prefix_icon=ft.Icons.NOTES,
        border_color=border_col
    )

    links_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

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

                # Ukuran dan padding disesuaikan agar rapat dan rapi
                open_btn = ft.IconButton(
                    icon=ft.Icons.OPEN_IN_NEW,
                    icon_color="blue400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Open Link in Browser",
                    on_click=make_open_handler(item["url"])
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Remove Link",
                    on_click=make_delete_handler(item)
                )

                link_icon = ft.Container(
                    content=ft.Icon(ft.Icons.LANGUAGE, color="blue400", size=22),
                    padding=10,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8
                )

                details = ft.Column([
                    ft.Text(item["title"], weight=ft.FontWeight.BOLD, size=15),
                    ft.Text(item["url"], color="blue400", size=12, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Text(item.get("desc", ""), size=12, opacity=0.7) if item.get("desc") else ft.Container()
                ], expand=True, spacing=2)

                card_content = ft.Row([
                    ft.Row([link_icon, details], expand=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([open_btn, del_btn], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

                card = ft.Container(
                    content=card_content,
                    padding=ft.padding.Padding(12, 8, 12, 8),
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                links_column.controls.append(card)

        page.update()

    def add_link(e):
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
        # Menggunakan insert(0, ...) agar link baru berada di paling atas
        links.insert(0, new_item)
        app_data["links"] = links
        save_data(app_data)

        title_input.value = ""
        url_input.value = ""
        desc_input.value = ""
        render_links()

    def delete_link(link_item):
        links.remove(link_item)
        app_data["links"] = links
        save_data(app_data)
        render_links()

    add_btn = ft.FilledButton(
        "Save Link",
        icon=ft.Icons.ADD,
        on_click=add_link,
        height=48
    )

    form_row_1 = ft.Row([title_input, url_input], spacing=10)
    form_row_2 = ft.Row([desc_input, add_btn], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    form_card = ft.Container(
        content=ft.Column([form_row_1, form_row_2], spacing=12),
        padding=16,
        border_radius=12,
        bgcolor="surfaceVariant"
    )

    render_links()

    return ft.Column([
        ft.Text("Link Bookmark", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_card,
        ft.Divider(height=15, color="transparent"),
        links_column
    ], expand=True)