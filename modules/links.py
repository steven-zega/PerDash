import webbrowser
import flet as ft
from database import save_data

def build_links(page: ft.Page, app_data: dict):
    links = app_data.get("links", [])

    title_input = ft.TextField(hint_text="Name / Title...", expand=True, border_color="white")
    url_input = ft.TextField(hint_text="URL", expand=True, border_color="white")
    desc_input = ft.TextField(hint_text="Notes...", expand=True, border_color="white")

    links_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_links():
        links_column.controls.clear()
        if not links:
            links_column.controls.append(
                ft.Container(
                    content=ft.Text("No links saved", color="white54", italic=True),
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
                    tooltip="Open Link",
                    on_click=make_open_handler(item["url"])
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    tooltip="Remove",
                    on_click=make_delete_handler(item)
                )

                card_content = ft.Row([
                    ft.Column([
                        ft.Text(item["title"], weight=ft.FontWeight.BOLD, size=15,),
                        ft.Text(item["url"], color="blue300", size=12,),
                        ft.Text(item.get("desc", ""), color="white54", size=12,) if item.get("desc") else ft.Container()
                    ], expand=True, spacing=2),
                    ft.Row([open_btn, del_btn], spacing=0)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

                card = ft.Container(
                    content=card_content,
                    padding=12,
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
        links.append(new_item)
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

    add_btn = ft.ElevatedButton(
        "Save",
        icon=ft.Icons.ADD,
        on_click=add_link
    )

    form_layout = ft.Column([
        ft.Row([title_input, url_input]),
        ft.Row([desc_input, add_btn])
    ], spacing=10)

    render_links()

    return ft.Column([
        ft.Text("Link", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_layout,
        ft.Divider(height=10),
        links_column
    ], expand=True)