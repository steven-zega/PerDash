import subprocess
import platform
import flet as ft
from database import save_data

def copy_to_clipboard(text: str):
    try:
        if platform.system() == "Windows":
            subprocess.run("clip", input=text.encode("utf-16"), check=True)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run("pbcopy", input=text.encode("utf-8"), check=True)
        else:  # Linux
            subprocess.run(["xclip", "-selection", "clipboard"], input=text.encode("utf-8"), check=True)
    except Exception:
        pass

def build_vault_mobile(page: ft.Page, app_data: dict):
    passwords = app_data.get("passwords", [])
    border_col = ft.Colors.OUTLINE

    def open_add_dialog(e=None):
        label_style = ft.TextStyle(size=12)

        service_input = ft.TextField(
            label="Platform / Website",
            label_style=label_style,
            text_size=12,
            border_color=border_col,
            autofocus=True,
            dense=True
        )

        user_input = ft.TextField(
            label="Username / Email",
            label_style=label_style,
            text_size=12,
            border_color=border_col,
            dense=True
        )

        pass_input = ft.TextField(
            label="Password",
            label_style=label_style,
            text_size=12,
            password=True,
            can_reveal_password=True,
            border_color=border_col,
            dense=True
        )

        def close_dialog(e):
            dialog.open = False
            page.update()

        def save_password_action(e):
            if not service_input.value.strip() or not pass_input.value.strip():
                return

            new_item = {
                "service": service_input.value.strip(),
                "username": user_input.value.strip(),
                "password": pass_input.value.strip()
            }

            passwords.insert(0, new_item)
            app_data["passwords"] = passwords
            save_data(app_data)

            dialog.open = False
            page.update()
            render_passwords()

        dialog = ft.AlertDialog(
            title=ft.Text("New Password Entry", weight=ft.FontWeight.BOLD, size=15),
            content=ft.Container(
                content=ft.Column(
                    [
                        service_input,
                        user_input,
                        pass_input
                    ],
                    tight=True,
                    spacing=8
                ),
                width=240,
                padding=5
            ),
            actions=[
                ft.TextButton("Cancel", on_click=close_dialog),
                ft.FilledButton("Save", on_click=save_password_action),
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )

        page.overlay.append(dialog)
        dialog.open = True
        page.update()

    vault_column = ft.Column(spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    def render_passwords():
        vault_column.controls.clear()
        if not passwords:
            vault_column.controls.append(
                ft.Container(
                    content=ft.Text("No passwords saved...", italic=True),
                    padding=20
                )
            )
        else:
            for item in passwords:
                def make_copy_handler(pass_text):
                    def on_copy(e):
                        copy_to_clipboard(pass_text)
                        page.snack_bar = ft.SnackBar(
                            content=ft.Text("Copied!"),
                            bgcolor="green800",
                            duration=2000
                        )
                        page.snack_bar.open = True
                        page.update()
                    return on_copy

                def make_delete_handler(vault_item):
                    return lambda e: delete_password(vault_item)

                copy_btn = ft.IconButton(
                    icon=ft.Icons.COPY,
                    icon_color="green400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Copy Password",
                    on_click=make_copy_handler(item["password"])
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=16,
                    width=26,
                    height=26,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Remove Password",
                    on_click=make_delete_handler(item)
                )

                vault_icon = ft.Container(
                    content=ft.Icon(ft.Icons.SHIELD_OUTLINED, color="green400", size=18),
                    padding=6,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8
                )

                details = ft.Column([
                    ft.Text(item["service"], weight=ft.FontWeight.BOLD, size=13, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=11, opacity=0.7),
                        ft.Text(item["username"], size=10, opacity=0.8, overflow=ft.TextOverflow.ELLIPSIS, expand=True)
                    ], spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([
                        ft.Icon(ft.Icons.KEY, size=11, opacity=0.7),
                        ft.Text("••••••••", size=10, opacity=0.5)
                    ], spacing=3, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], expand=True, spacing=2)

                card_content = ft.Row([
                    ft.Row([vault_icon, details], expand=True, spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([copy_btn, del_btn], spacing=2, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

                card = ft.Container(
                    content=card_content,
                    padding=8,
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                vault_column.controls.append(card)

            vault_column.controls.append(ft.Container(height=60))

        page.update()

    def delete_password(vault_item):
        passwords.remove(vault_item)
        app_data["passwords"] = passwords
        save_data(app_data)
        render_passwords()

    render_passwords()

    main_content = ft.Column(
        [
            vault_column
        ],
        expand=True,
        spacing=0
    )

    fab_button = ft.FloatingActionButton(
        icon=ft.Icons.ADD,
        bgcolor=ft.Colors.BLUE_600,
        foreground_color=ft.Colors.WHITE,
        shape=ft.CircleBorder(),
        tooltip="New Entry",
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