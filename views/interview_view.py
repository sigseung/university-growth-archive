"""
views/interview_view.py

활동을 하나 선택하고 "AI로 예상질문 생성"을 누르면, 그 활동을 근거로
면접 예상질문 + 꼬리질문 + 모범답변을 만들어서 InterviewQA에 저장하고 보여줍니다.
사용자가 직접 자신의 답변을 써볼 수도 있습니다.
"""

import customtkinter as ctk
from tkinter import messagebox

from database.db_session import get_session
from services.activity_service import ActivityService
from services.ai_content_service import AIContentService
from repositories.interview_qa_repository import InterviewQARepository
from ai.ai_client import AIConfigError, AIRequestError


class InterviewView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.selected_activity_id: int | None = None
        self._build_ui()
        self._load_activity_choices()

    def _build_ui(self):
        ctk.CTkLabel(
            self, text="🎤 면접 준비", font=ctk.CTkFont(size=20, weight="bold"), anchor="w"
        ).pack(fill="x", padx=24, pady=(20, 4))
        ctk.CTkLabel(
            self, text="활동을 선택하면 AI가 예상 질문과 모범답변을 만들어줍니다.",
            font=ctk.CTkFont(size=12), text_color=("gray40", "gray70"), anchor="w",
        ).pack(fill="x", padx=24, pady=(0, 12))

        control_bar = ctk.CTkFrame(self, fg_color="transparent")
        control_bar.pack(fill="x", padx=24, pady=(0, 12))

        self.activity_combo = ctk.CTkComboBox(control_bar, values=["활동 없음"], command=self._on_select_activity)
        self.activity_combo.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.generate_btn = ctk.CTkButton(
            control_bar, text="AI로 예상질문 생성", width=160, command=self._handle_generate
        )
        self.generate_btn.pack(side="right")

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def _load_activity_choices(self):
        with get_session() as session:
            self._activities = ActivityService(session).list_activities()

        if not self._activities:
            self.activity_combo.configure(values=["등록된 활동이 없습니다"])
            self.activity_combo.set("등록된 활동이 없습니다")
            self.generate_btn.configure(state="disabled")
            return

        labels = [f"{a.title} ({a.date_start})" for a in self._activities]
        self.activity_combo.configure(values=labels)
        self.activity_combo.set(labels[0])
        self.selected_activity_id = self._activities[0].id
        self._render_qa_list()

    def _on_select_activity(self, selected_label: str):
        for a, label in zip(self._activities, [f"{x.title} ({x.date_start})" for x in self._activities]):
            if label == selected_label:
                self.selected_activity_id = a.id
                break
        self._render_qa_list()

    def _render_qa_list(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if self.selected_activity_id is None:
            return

        with get_session() as session:
            qa_list = InterviewQARepository(session).list_by_activity(self.selected_activity_id)

            if not qa_list:
                ctk.CTkLabel(
                    self.scroll,
                    text="아직 생성된 질문이 없습니다. 'AI로 예상질문 생성' 버튼을 눌러보세요.",
                    text_color=("gray50", "gray60"),
                ).pack(pady=40)
                return

            for i, qa in enumerate(qa_list, start=1):
                self._render_qa_card(qa, i)

    def _render_qa_card(self, qa, index: int):
        box = ctk.CTkFrame(self.scroll, corner_radius=12)
        box.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(
            box, text=f"Q{index}. {qa.question}", font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w", justify="left", wraplength=700,
        ).pack(fill="x", padx=16, pady=(14, 4))

        if qa.follow_up_question:
            ctk.CTkLabel(
                box, text=f"꼬리질문: {qa.follow_up_question}", font=ctk.CTkFont(size=12),
                text_color=("gray35", "gray75"), anchor="w", justify="left", wraplength=680,
            ).pack(fill="x", padx=16, pady=(0, 6))

        if qa.model_answer:
            ctk.CTkLabel(
                box, text="모범답변", font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray30", "gray80"), anchor="w",
            ).pack(fill="x", padx=16, pady=(6, 2))
            ctk.CTkLabel(
                box, text=qa.model_answer, anchor="w", justify="left", wraplength=680,
            ).pack(fill="x", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            box, text="나의 답변 연습", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=("gray30", "gray80"), anchor="w",
        ).pack(fill="x", padx=16, pady=(4, 2))
        answer_box = ctk.CTkTextbox(box, height=60)
        answer_box.pack(fill="x", padx=16, pady=(0, 8))
        if qa.user_answer:
            answer_box.insert("1.0", qa.user_answer)

        ctk.CTkButton(
            box, text="답변 저장", width=90, height=26,
            command=lambda qid=qa.id, box=answer_box: self._handle_save_answer(qid, box),
        ).pack(anchor="e", padx=16, pady=(0, 14))

    def _handle_save_answer(self, qa_id: int, answer_box):
        answer = answer_box.get("1.0", "end").strip()
        with get_session() as session:
            InterviewQARepository(session).update_user_answer(qa_id, answer)
        messagebox.showinfo("저장 완료", "답변이 저장되었습니다.", parent=self)

    def _handle_generate(self):
        if self.selected_activity_id is None:
            return

        self.generate_btn.configure(state="disabled", text="생성 중...")
        self.update()

        try:
            with get_session() as session:
                activity = ActivityService(session).get_activity(self.selected_activity_id)
                if activity is None:
                    return
                AIContentService(session).generate_and_save_interview_qa(activity)
        except AIConfigError as e:
            messagebox.showwarning("설정 필요", str(e), parent=self)
        except AIRequestError as e:
            messagebox.showerror("생성 실패", str(e), parent=self)
        except ValueError as e:
            messagebox.showwarning("생성 불가", str(e), parent=self)
        else:
            self._render_qa_list()
        finally:
            self.generate_btn.configure(state="normal", text="AI로 예상질문 생성")
