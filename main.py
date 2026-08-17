APP_VERSION = "1.0.0"

import flet as ft
from database import load_data, save_data
from modules.todo import build_todo
from modules.links import build_links
from modules.vault import build_vault
from modules.notes import build_notes  

def main(page: ft.Page):
    page.title = "Personal Dashboard"
    page.padding = 0
    page.window.width = 1000
    page.window.height = 650

    app_data = load_data()

    saved_theme = app_data.get("theme_mode", "dark")
    page.theme_mode = ft.ThemeMode.DARK if saved_theme == "dark" else ft.ThemeMode.LIGHT

    def toggle_theme(e):
        if page.theme_mode == ft.ThemeMode.DARK:
            page.theme_mode = ft.ThemeMode.LIGHT
            theme_btn.icon = ft.Icons.DARK_MODE
            theme_btn.tooltip = "Switch to Dark Mode"
            app_data["theme_mode"] = "light"
        else:
            page.theme_mode = ft.ThemeMode.DARK
            theme_btn.icon = ft.Icons.LIGHT_MODE
            theme_btn.tooltip = "Switch to Light Mode"
            app_data["theme_mode"] = "dark"
        
        save_data(app_data)
        page.update()

    theme_btn = ft.IconButton(
        icon=ft.Icons.LIGHT_MODE if page.theme_mode == ft.ThemeMode.DARK else ft.Icons.DARK_MODE,
        tooltip="Switch to Light Mode" if page.theme_mode == ft.ThemeMode.DARK else "Switch to Dark Mode",
        on_click=toggle_theme
    )

    content_area = ft.Container(
        content=build_todo(page, app_data),
        expand=True,
        padding=25
    )

    def on_nav_change(e):
        selected_idx = e.control.selected_index
        if selected_idx == 0:
            content_area.content = build_todo(page, app_data)
        elif selected_idx == 1:
            content_area.content = build_links(page, app_data)
        elif selected_idx == 2:
            content_area.content = build_vault(page, app_data)
        elif selected_idx == 3:
            content_area.content = build_notes(page, app_data)
        
        page.update()

    sidebar = ft.NavigationRail(
        selected_index=0,
        label_type=ft.NavigationRailLabelType.ALL,
        min_width=90,
        min_extended_width=180,
        group_alignment=-1.0,
        expand=True,
        destinations=[
            ft.NavigationRailDestination(
                icon=ft.Icons.CHECK_BOX_OUTLINED,
                selected_icon=ft.Icons.CHECK_BOX,
                label="To-Do List",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LINK_OUTLINED,
                selected_icon=ft.Icons.LINK,
                label="Link",
            ),
            ft.NavigationRailDestination(
                icon=ft.Icons.LOCK_OUTLINE,
                selected_icon=ft.Icons.LOCK,
                label="Password",
            ),
            ft.NavigationRailDestination(  
                icon=ft.Icons.STICKY_NOTE_2_OUTLINED,
                selected_icon=ft.Icons.STICKY_NOTE_2,
                label="Notes",
            ),
        ],
        on_change=on_nav_change,
    )

    left_sidebar = ft.Column(
        [
            sidebar,
            ft.Container(
                content=theme_btn,
                padding=ft.padding.Padding(0, 0, 0, 10),
                alignment=ft.Alignment(0, 1)
            )
        ],
        width=90,
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

    layout = ft.Row(
        [
            left_sidebar,
            ft.VerticalDivider(width=1),
            content_area,
        ],
        expand=True,
    )

    page.add(layout)

ft.run(main)