"""
views/ai_analysis_view.py

버튼 하나로 AI 성장 분석 리포트를 생성하고, 과거 분석 이력도 함께 보여줍니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from services.ai_analysis_service import AIAnalysisService
from ai.ai_client import AIConfigError, AIRequestError


class AIAnalysisView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            header, text="🤖 AI 성장 분석", font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")
        self.generate_btn = ctk.CTkButton(
            header, text="새 분석 생성", command=self._handle_generate
        )
        self.generate_btn.pack(side="right")

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), anchor="w"
        )
        self.status_label.pack(fill="x", padx=24, pady=(0, 12))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = AIAnalysisService(session)
            logs = service.get_recent_logs(limit=5)

        if not logs:
            ctk.CTkLabel(
                self.scroll,
                text="아직 생성된 분석이 없습니다. 위 '새 분석 생성' 버튼을 눌러보세요.",
                text_color=("gray50", "gray60"),
            ).pack(pady=40)
            return

        for i, log in enumerate(logs):
            box = ctk.CTkFrame(self.scroll, corner_radius=12)
            box.pack(fill="x", pady=(0, 12))

            label_text = "최신 분석" if i == 0 else "이전 분석"
            ctk.CTkLabel(
                box, text=f"{label_text}  ·  {log.created_at.strftime('%Y-%m-%d %H:%M')}",
                font=ctk.CTkFont(size=12, weight="bold"), text_color=("gray30", "gray80"), anchor="w",
            ).pack(fill="x", padx=16, pady=(14, 6))

            ctk.CTkLabel(
                box, text=log.content, anchor="w", justify="left", wraplength=700,
            ).pack(fill="x", padx=16, pady=(0, 14))

    def _handle_generate(self):
        self.generate_btn.configure(state="disabled", text="생성 중...")
        self.status_label.configure(text="AI가 활동 데이터를 분석하고 있습니다. 잠시만 기다려주세요...")
        self.update()  # 버튼 비활성화 상태를 화면에 즉시 반영

        try:
            with get_session() as session:
                AIAnalysisService(session).generate_growth_analysis()
        except AIConfigError as e:
            messagebox.showwarning("설정 필요", str(e), parent=self)
        except AIRequestError as e:
            messagebox.showerror("생성 실패", str(e), parent=self)
        except ValueError as e:
            messagebox.showwarning("생성 불가", str(e), parent=self)
        else:
            self.status_label.configure(text="")
            self.refresh()
            return
        finally:
            self.generate_btn.configure(state="normal", text="새 분석 생성")

        self.status_label.configure(text="")
