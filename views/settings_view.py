"""
views/settings_view.py

OpenAI API 키를 입력/저장하는 화면입니다.
AI 기능(성장 분석, 면접 준비, 자소서 문장 생성 등)을 쓰려면
여기서 먼저 키를 등록해야 합니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from utils.settings_store import get_openai_api_key, set_openai_api_key


class SettingsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="설정", font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            self, text="AI 기능(성장 분석 / 면접 준비 / 자소서 문장 생성)을 쓰려면 OpenAI API 키가 필요합니다.",
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 20))

        box = ctk.CTkFrame(self, corner_radius=12)
        box.pack(fill="x", padx=24)

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
