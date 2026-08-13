"""
views/settings_view.py

OpenAI API 키 관리 + 데이터 백업/복원을 다루는 화면입니다.
AI 기능(성장 분석, 면접 준비, 자소서 문장 생성 등)을 쓰려면
여기서 먼저 키를 등록해야 하고, V6부터는 백업 관리도 이 화면에서 합니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from utils.settings_store import get_openai_api_key, set_openai_api_key
from utils.file_utils import open_file_with_default_app
from services import backup_service
from config import BACKUPS_DIR


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="설정", font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 4))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        self._build_api_key_section(self.scroll)
        self._build_backup_section(self.scroll)

    def _build_api_key_section(self, parent):
        ctk.CTkLabel(
            parent, text="AI 기능(성장 분석 / 면접 준비 / 자소서 문장 생성)을 쓰려면 OpenAI API 키가 필요합니다.",
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), anchor="w",
        ).pack(fill="x", pady=(0, 12))

        box = ctk.CTkFrame(parent, corner_radius=12)
        box.pack(fill="x", pady=(0, 24))

        ctk.CTkLabel(box, text="OpenAI API 키", anchor="w").pack(fill="x", padx=20, pady=(20, 4))
        self.api_key_entry = ctk.CTkEntry(box, show="•", placeholder_text="sk-...")
        self.api_key_entry.pack(fill="x", padx=20)

        existing_key = get_openai_api_key()
        if existing_key:
            # 이미 저장된 키는 그대로 다시 보여주지 않고, 일부만 마스킹해서 안내합니다
            # (설정 화면을 캡처/공유했을 때 키가 그대로 노출되지 않도록).
            masked = existing_key[:6] + "..." + existing_key[-4:] if len(existing_key) > 12 else "설정됨"
            ctk.CTkLabel(
                box, text=f"현재 저장된 키: {masked}", font=ctk.CTkFont(size=11),
                text_color=("gray40", "gray70"), anchor="w",
            ).pack(fill="x", padx=20, pady=(6, 0))

        self.show_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            box, text="입력값 표시", variable=self.show_var, command=self._toggle_visibility,
        ).pack(anchor="w", padx=20, pady=(10, 0))

        ctk.CTkLabel(
            box, text="API 키는 이 컴퓨터의 settings.json 파일에만 저장되며, 외부로 전송되지 않습니다.\n"
            "(GitHub에 프로젝트를 올릴 때는 .gitignore에 등록되어 있어 자동으로 제외됩니다.)",
            font=ctk.CTkFont(size=11), text_color=("gray45", "gray65"), justify="left", anchor="w",
        ).pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkButton(box, text="저장", command=self._handle_save).pack(
            anchor="e", padx=20, pady=(0, 20)
        )

    def _build_backup_section(self, parent):
        header_row = ctk.CTkFrame(parent, fg_color="transparent")
        header_row.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(
            header_row, text="데이터 백업", font=ctk.CTkFont(size=15, weight="bold"), anchor="w"
        ).pack(side="left")
        ctk.CTkButton(
            header_row, text="지금 백업", width=100, height=28, command=self._handle_backup_now,
        ).pack(side="right")
        ctk.CTkButton(
            header_row, text="백업 폴더 열기", width=110, height=28, fg_color="transparent",
            border_width=1, command=self._handle_open_backup_folder,
        ).pack(side="right", padx=(0, 8))

        ctk.CTkLabel(
            parent, text="앱을 실행할 때마다 하루 한 번 자동으로 백업됩니다 (최근 14개까지 보관). "
            "복원하면 지금 상태도 안전하게 별도로 백업해둔 뒤 되돌립니다.",
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"),
            anchor="w", justify="left", wraplength=700,
        ).pack(fill="x", pady=(0, 12))

        self.backup_list_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.backup_list_frame.pack(fill="x")
        self._render_backup_list()

    def _render_backup_list(self):
        for widget in self.backup_list_frame.winfo_children():
            widget.destroy()

        backups = backup_service.list_backups()
        if not backups:
            ctk.CTkLabel(
                self.backup_list_frame, text="아직 백업이 없습니다.",
                text_color=("gray50", "gray60"), anchor="w",
            ).pack(fill="x", pady=8)
            return

        for backup_path in backups:
            row = ctk.CTkFrame(self.backup_list_frame, corner_radius=8)
            row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                row, text=backup_service.format_backup_label(backup_path), anchor="w",
            ).pack(side="left", padx=12, pady=8)
            ctk.CTkButton(
                row, text="복원", width=60, height=26, fg_color="transparent", border_width=1,
                command=lambda p=backup_path: self._handle_restore(p),
            ).pack(side="right", padx=8)

    def _handle_backup_now(self):
        try:
            backup_service.create_backup()
        except FileNotFoundError as e:
            messagebox.showwarning("백업 실패", str(e), parent=self)
            return
        messagebox.showinfo("백업 완료", "지금 상태를 백업했습니다.", parent=self)
        self._render_backup_list()

    def _handle_open_backup_folder(self):
        try:
            open_file_with_default_app(str(BACKUPS_DIR))
        except FileNotFoundError as e:
            messagebox.showwarning("폴더 열기 실패", str(e), parent=self)

    def _handle_restore(self, backup_path):
        label = backup_service.format_backup_label(backup_path)
        if not messagebox.askyesno(
            "복원 확인",
            f"'{label}' 시점으로 되돌리시겠습니까?\n"
            "지금 상태는 자동으로 안전 백업된 뒤 교체됩니다.",
            parent=self,
        ):
            return
        try:
            backup_service.restore_backup(backup_path)
        except FileNotFoundError as e:
            messagebox.showerror("복원 실패", str(e), parent=self)
            return
        messagebox.showinfo("복원 완료", "복원되었습니다. 다른 화면으로 이동하면 반영된 내용이 보입니다.", parent=self)
        self._render_backup_list()

    def _toggle_visibility(self):
        self.api_key_entry.configure(show="" if self.show_var.get() else "•")

    def _handle_save(self):
        key = self.api_key_entry.get().strip()
        if not key:
            messagebox.showwarning("입력 오류", "API 키를 입력해주세요.", parent=self)
            return
        set_openai_api_key(key)
        messagebox.showinfo("저장 완료", "API 키가 저장되었습니다.", parent=self)
        self.api_key_entry.delete(0, "end")
        self._build_ui_refresh()

    def _build_ui_refresh(self):
        for widget in self.winfo_children():
            widget.destroy()
        self._build_ui()
