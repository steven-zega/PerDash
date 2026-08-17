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

def build_vault(page: ft.Page, app_data: dict):
    passwords = app_data.get("passwords", [])

    # Warna border dinamis dari tema Flet
    border_col = ft.Colors.OUTLINE

    service_input = ft.TextField(
        label="Platform / Website",
        expand=True,
        prefix_icon=ft.Icons.SECURITY,
        border_color=border_col
    )
    user_input = ft.TextField(
        label="Username / Email",
        expand=True,
        prefix_icon=ft.Icons.PERSON_OUTLINE,
        border_color=border_col
    )
    pass_input = ft.TextField(
        label="Password",
        password=True,
        can_reveal_password=True,
        expand=True,
        prefix_icon=ft.Icons.LOCK_OUTLINE,
        border_color=border_col
    )

    vault_column = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

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

                # Ukuran dan padding tombol disesuaikan agar rapat
                copy_btn = ft.IconButton(
                    icon=ft.Icons.COPY,
                    icon_color="green400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Copy Password",
                    on_click=make_copy_handler(item["password"])
                )

                del_btn = ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE,
                    icon_color="red400",
                    icon_size=18,
                    width=28,
                    height=28,
                    style=ft.ButtonStyle(padding=0),
                    tooltip="Remove Password",
                    on_click=make_delete_handler(item)
                )

                vault_icon = ft.Container(
                    content=ft.Icon(ft.Icons.SHIELD_OUTLINED, color="green400", size=22),
                    padding=10,
                    bgcolor=ft.Colors.PRIMARY_CONTAINER,
                    border_radius=8
                )

                details = ft.Column([
                    ft.Text(item["service"], weight=ft.FontWeight.BOLD, size=15),
                    ft.Row([
                        ft.Icon(ft.Icons.PERSON_OUTLINE, size=13),
                        ft.Text(item["username"], size=12, opacity=0.8)
                    ], spacing=4),
                    ft.Row([
                        ft.Icon(ft.Icons.KEY, size=13),
                        ft.Text("••••••••", size=12, opacity=0.5)
                    ], spacing=4)
                ], expand=True, spacing=3)

                card_content = ft.Row([
                    ft.Row([vault_icon, details], expand=True, spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ft.Row([copy_btn, del_btn], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN, vertical_alignment=ft.CrossAxisAlignment.CENTER)

                card = ft.Container(
                    content=card_content,
                    padding=ft.padding.Padding(12, 8, 12, 8),
                    border_radius=8,
                    bgcolor="surfaceVariant"
                )
                vault_column.controls.append(card)

        page.update()

    def add_password(e):
        if not service_input.value.strip() or not pass_input.value.strip():
            return

        new_item = {
            "service": service_input.value.strip(),
            "username": user_input.value.strip(),
            "password": pass_input.value.strip()
        }
        # Menggunakan insert(0, ...) agar entri baru berada di posisi paling atas
        passwords.insert(0, new_item)
        app_data["passwords"] = passwords
        save_data(app_data)

        service_input.value = ""
        user_input.value = ""
        pass_input.value = ""
        render_passwords()

    def delete_password(vault_item):
        passwords.remove(vault_item)
        app_data["passwords"] = passwords
        save_data(app_data)
        render_passwords()

    add_btn = ft.FilledButton(
        "Save Password",
        icon=ft.Icons.ADD,
        on_click=add_password,
        height=48
    )

    form_row_1 = ft.Row([service_input, user_input], spacing=10)
    form_row_2 = ft.Row([pass_input, add_btn], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER)

    form_card = ft.Container(
        content=ft.Column([form_row_1, form_row_2], spacing=12),
        padding=16,
        border_radius=12,
        bgcolor="surfaceVariant"
    )

    render_passwords()

    return ft.Column([
        ft.Text("Password Vault", size=24, weight=ft.FontWeight.BOLD),
        ft.Divider(height=10, color="transparent"),
        form_card,
        ft.Divider(height=15, color="transparent"),
        vault_column
    ], expand=True)