"""
views/activity_detail_view.py

활동 하나의 상세 정보를 보여주는 화면입니다.
V1: 기본정보 + Reflection / V2: 첨부파일 업로드 섹션 추가 / V3: 자기소개서 분류 표시 + PDF/MD Export 버튼 추가.
V4: STAR 섹션 + 성장 연결(GrowthLink) 섹션 추가.
"""

import customtkinter as ctk
from tkinter import messagebox, filedialog

from database.db_session import get_session
from models.reflection import Reflection
from services.activity_service import ActivityService
from services.attachment_service import AttachmentService
from services.export_service import ExportService
from services.growth_link_service import GrowthLinkService
from utils.date_utils import format_date_kr
from utils.file_utils import open_file_with_default_app


class ActivityDetailView(ctk.CTkFrame):
    def __init__(self, master, activity_id: int, on_back=None, on_deleted=None, on_edit=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.activity_id = activity_id
        self.on_back = on_back
        self.on_deleted = on_deleted
        self.on_edit = on_edit
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.pack(fill="x", padx=24, pady=(20, 8))

        ctk.CTkButton(
            top_bar, text="< 목록으로", width=100, fg_color="transparent",
            border_width=1, command=lambda: self.on_back() if self.on_back else None,
        ).pack(side="left")

        self.edit_btn = ctk.CTkButton(top_bar, text="수정", width=70, command=self._handle_edit)
        self.edit_btn.pack(side="right", padx=(6, 0))
        self.delete_btn = ctk.CTkButton(
            top_bar, text="삭제", width=70, fg_color="#EF4444", hover_color="#DC2626",
            command=self._handle_delete,
        )
        self.delete_btn.pack(side="right")

        ctk.CTkButton(
            top_bar, text="Markdown", width=90, fg_color="transparent", border_width=1,
            command=self._handle_export_markdown,
        ).pack(side="right", padx=(0, 6))
        ctk.CTkButton(
            top_bar, text="PDF", width=70, fg_color="transparent", border_width=1,
            command=self._handle_export_pdf,
        ).pack(side="right", padx=(0, 6))

        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=24, pady=(0, 20))

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        with get_session() as session:
            service = ActivityService(session)
            activity = service.get_activity(self.activity_id)

            if activity is None:
                ctk.CTkLabel(self.scroll, text="활동을 찾을 수 없습니다.").pack(pady=40)
                return

            ctk.CTkLabel(
                self.scroll, text=activity.title, font=ctk.CTkFont(size=22, weight="bold"), anchor="w"
            ).pack(fill="x", pady=(4, 4))

            meta = (
                f"{activity.activity_type.value}  ·  {format_date_kr(activity.date_start)}  ·  "
                f"{activity.location or '장소 미정'}  ·  상태: {activity.status.value}  ·  "
                f"중요도: {'★' * activity.importance}{'☆' * (5 - activity.importance)}"
            )
            ctk.CTkLabel(
                self.scroll, text=meta, font=ctk.CTkFont(size=13),
                text_color=("gray40", "gray70"), anchor="w",
            ).pack(fill="x", pady=(0, 6))

            if activity.tags:
                tag_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
                tag_frame.pack(fill="x", pady=(0, 8), anchor="w")
                for tag in activity.tags:
                    ctk.CTkLabel(
                        tag_frame, text=f"#{tag.name}", fg_color=("gray85", "gray25"),
                        corner_radius=8, padx=8,
                    ).pack(side="left", padx=(0, 6))

            if activity.categories:
                category_frame = ctk.CTkFrame(self.scroll, fg_color="transparent")
                category_frame.pack(fill="x", pady=(0, 16), anchor="w")
                for cat in activity.categories:
                    ctk.CTkLabel(
                        category_frame, text=cat.name, fg_color="#3B82F6", text_color="white",
                        corner_radius=8, padx=8,
                    ).pack(side="left", padx=(0, 6))

            self._section(self.scroll, "참여 목적", activity.purpose)
            self._section(self.scroll, "활동 내용", activity.content)
            self._section(self.scroll, "새롭게 배운 기술", activity.new_skills)
            self._section(self.scroll, "새롭게 알게 된 직무", activity.new_roles)

            self._attachment_section(self.scroll, service)
            self._star_section(self.scroll, activity)
            self._growth_link_section(self.scroll, service, activity)
            self._reflection_section(self.scroll, activity)

    def _section(self, parent, title: str, content: str | None):
        if not content:
            return
        ctk.CTkLabel(
            parent, text=title, font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(14, 4))
        ctk.CTkLabel(
            parent, text=content, anchor="w", justify="left", wraplength=700
        ).pack(fill="x")

    def _attachment_section(self, parent, activity_service: ActivityService):
        header_row = ctk.CTkFrame(parent, fg_color="transparent")
        header_row.pack(fill="x", pady=(20, 8))
        ctk.CTkLabel(
            header_row, text="첨부파일", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(side="left")
        ctk.CTkButton(
            header_row, text="+ 파일 업로드", width=110, height=28,
            command=self._handle_upload,
        ).pack(side="right")

        attachment_service = AttachmentService(activity_service.session)
        attachments = attachment_service.list_attachments(self.activity_id)

        if not attachments:
            ctk.CTkLabel(
                parent, text="첨부된 파일이 없습니다.", text_color=("gray50", "gray60"), anchor="w"
            ).pack(fill="x", pady=(0, 8))
            return

        for att in attachments:
            row = ctk.CTkFrame(parent, corner_radius=8)
            row.pack(fill="x", pady=3)

            ctk.CTkLabel(
                row, text=f"[{att.file_type.value}]", width=60, font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(side="left", padx=(12, 4), pady=8)
            ctk.CTkLabel(
                row, text=att.original_name or "파일", anchor="w",
            ).pack(side="left", fill="x", expand=True, pady=8)
            ctk.CTkButton(
                row, text="열기", width=50, height=26, fg_color="transparent", border_width=1,
                command=lambda p=att.file_path: self._handle_open_attachment(p),
            ).pack(side="right", padx=(4, 8))
            ctk.CTkButton(
                row, text="삭제", width=50, height=26, fg_color="#EF4444", hover_color="#DC2626",
                command=lambda aid=att.id: self._handle_delete_attachment(aid),
            ).pack(side="right")

    def _handle_upload(self):
        file_path = filedialog.askopenfilename(title="첨부할 파일 선택")
        if not file_path:
            return
        try:
            with get_session() as session:
                AttachmentService(session).upload_attachment(self.activity_id, file_path)
        except FileNotFoundError as e:
            messagebox.showwarning("업로드 실패", str(e), parent=self)
            return
        self.refresh()

    def _handle_open_attachment(self, file_path: str):
        try:
            open_file_with_default_app(file_path)
        except FileNotFoundError as e:
            messagebox.showwarning("파일 열기 실패", str(e), parent=self)

    def _handle_delete_attachment(self, attachment_id: int):
        if not messagebox.askyesno("삭제 확인", "이 첨부파일 기록을 삭제하시겠습니까?"):
            return
        with get_session() as session:
            AttachmentService(session).delete_attachment(attachment_id)
        self.refresh()

    def _star_section(self, parent, activity):
        """STAR(Situation/Task/Action/Result). 값이 하나라도 있으면 보여주고,
        수정은 activity_form_view의 'STAR' 섹션에서 합니다 (한 활동에 STAR는
        Reflection과 달리 '한 세트'만 존재하므로, 회고처럼 여러 개 추가하는 UI 대신
        폼에서 통째로 수정하는 방식이 더 자연스럽습니다)."""
        star_fields = [
            ("Situation (상황)", activity.star_situation),
            ("Task (과제/목표)", activity.star_task),
            ("Action (행동)", activity.star_action),
            ("Result (결과)", activity.star_result),
        ]
        if not any(v for _, v in star_fields):
            return

        ctk.CTkLabel(
            parent, text="STAR", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(20, 8))

        box = ctk.CTkFrame(parent, corner_radius=10)
        box.pack(fill="x", pady=4)
        for label, value in star_fields:
            if not value:
                continue
            ctk.CTkLabel(
                box, text=label, font=ctk.CTkFont(size=12, weight="bold"),
                text_color=("gray30", "gray80"), anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 0))
            ctk.CTkLabel(
                box, text=value, anchor="w", justify="left", wraplength=680
            ).pack(fill="x", padx=12, pady=(0, 8))

    def _growth_link_section(self, parent, activity_service: ActivityService, activity):
        """성장 연결(GrowthLink). "이 활동을 계기로 시작한 다음 행동"들을 보여주고,
        새 연결을 추가할 수 있습니다. 설계 문서의 핵심 기능인
        '활동 간 인과관계'가 실제로 저장/조회되는 부분입니다."""
        ctk.CTkLabel(
            parent, text="🔗 연결된 다음 행동", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(20, 8))

        if not activity.outgoing_links:
            ctk.CTkLabel(
                parent, text="아직 연결된 다음 행동이 없습니다.",
                text_color=("gray50", "gray60"), anchor="w",
            ).pack(fill="x", pady=(0, 8))
        else:
            for link in activity.outgoing_links:
                row = ctk.CTkFrame(parent, corner_radius=10)
                row.pack(fill="x", pady=3)
                text = f"→ {link.to_activity.title}"
                if link.link_reason:
                    text += f"  ({link.link_reason})"
                ctk.CTkLabel(row, text=text, anchor="w", wraplength=600).pack(
                    side="left", fill="x", expand=True, padx=12, pady=8
                )
                ctk.CTkButton(
                    row, text="연결 해제", width=70, height=26, fg_color="transparent", border_width=1,
                    command=lambda lid=link.id: self._handle_unlink(lid),
                ).pack(side="right", padx=8)

        # 새 연결 추가 UI: 자기 자신을 제외한 다른 활동들 중에서 선택
        other_activities = [
            a for a in activity_service.list_activities() if a.id != self.activity_id
        ]
        if not other_activities:
            return

        add_frame = ctk.CTkFrame(parent, fg_color="transparent")
        add_frame.pack(fill="x", pady=(8, 0))

        self._link_target_choices = other_activities
        target_labels = [f"{a.title} ({a.date_start})" for a in other_activities]
        self.link_target_combo = ctk.CTkComboBox(add_frame, values=target_labels)
        self.link_target_combo.set(target_labels[0])
        self.link_target_combo.pack(fill="x")

        self.link_reason_entry = ctk.CTkEntry(
            add_frame, placeholder_text="이 활동이 다음 행동으로 이어진 이유 (선택)"
        )
        self.link_reason_entry.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(
            add_frame, text="+ 연결 추가", command=self._handle_add_link
        ).pack(anchor="e", pady=(8, 0))

    def _handle_add_link(self):
        selected_label = self.link_target_combo.get()
        target = None
        for a, label in zip(self._link_target_choices, [f"{a.title} ({a.date_start})" for a in self._link_target_choices]):
            if label == selected_label:
                target = a
                break
        if target is None:
            return

        reason = self.link_reason_entry.get().strip() or None
        with get_session() as session:
            try:
                GrowthLinkService(session).link_activities(self.activity_id, target.id, reason)
            except ValueError as e:
                messagebox.showwarning("연결 실패", str(e), parent=self)
                return
        self.refresh()

    def _handle_unlink(self, link_id: int):
        if not messagebox.askyesno("연결 해제", "이 성장 연결을 삭제하시겠습니까?"):
            return
        with get_session() as session:
            GrowthLinkService(session).unlink(link_id)
        self.refresh()

    def _reflection_section(self, parent, activity):
        ctk.CTkLabel(
            parent, text="Reflection (회고)", font=ctk.CTkFont(size=14, weight="bold"), anchor="w"
        ).pack(fill="x", pady=(20, 8))

        if not activity.reflections:
            ctk.CTkLabel(
                parent, text="아직 작성한 회고가 없습니다.", text_color=("gray50", "gray60"), anchor="w"
            ).pack(fill="x", pady=(0, 8))
        else:
            for r in activity.reflections:
                box = ctk.CTkFrame(parent, corner_radius=10)
                box.pack(fill="x", pady=4)
                if r.learned:
                    ctk.CTkLabel(
                        box, text=f"느낀 점: {r.learned}", anchor="w", justify="left", wraplength=680
                    ).pack(fill="x", padx=12, pady=(10, 2))
                if r.next_action:
                    ctk.CTkLabel(
                        box, text=f"앞으로 할 행동: {r.next_action}", anchor="w",
                        justify="left", wraplength=680, text_color=("gray30", "gray80"),
                    ).pack(fill="x", padx=12, pady=(0, 10))

        add_frame = ctk.CTkFrame(parent, fg_color="transparent")
        add_frame.pack(fill="x", pady=(8, 0))

        self.learned_box = ctk.CTkTextbox(add_frame, height=50)
        self.learned_box.pack(fill="x")
        self.learned_box.configure(border_width=1)
        self.next_action_box = ctk.CTkTextbox(add_frame, height=50)
        self.next_action_box.pack(fill="x", pady=(6, 0))

        ctk.CTkButton(
            add_frame, text="+ 회고 추가", command=self._handle_add_reflection
        ).pack(anchor="e", pady=(8, 0))

    def _handle_add_reflection(self):
        learned = self.learned_box.get("1.0", "end").strip()
        next_action = self.next_action_box.get("1.0", "end").strip()
        if not learned and not next_action:
            return

        with get_session() as session:
            reflection = Reflection(
                activity_id=self.activity_id,
                learned=learned or None,
                next_action=next_action or None,
            )
            session.add(reflection)
            session.commit()

        self.refresh()

    def _handle_edit(self):
        if self.on_edit:
            self.on_edit(self.activity_id)

    def _handle_export_pdf(self):
        self._export(mode="pdf")

    def _handle_export_markdown(self):
        self._export(mode="markdown")

    def _export(self, mode: str):
        with get_session() as session:
            activity = ActivityService(session).get_activity(self.activity_id)
            if activity is None:
                return
            # 세션이 닫히기 전에 필요한 관계(tags/categories/reflections)를
            # 미리 접근해서 로딩해둡니다. (세션이 닫힌 뒤 접근하면
            # SQLAlchemy가 DetachedInstanceError를 던지기 때문)
            _ = (activity.tags, activity.categories, activity.reflections, activity.outgoing_links)

            try:
                if mode == "pdf":
                    path = ExportService().export_to_pdf(activity)
                else:
                    path = ExportService().export_to_markdown(activity)
            except Exception as e:
                messagebox.showerror("내보내기 실패", str(e), parent=self)
                return

        messagebox.showinfo(
            "내보내기 완료", f"파일로 저장했습니다:\n{path}", parent=self
        )

    def _handle_delete(self):
        if not messagebox.askyesno("삭제 확인", "이 활동을 삭제하시겠습니까? 되돌릴 수 없습니다."):
            return
        with get_session() as session:
            service = ActivityService(session)
            service.delete_activity(self.activity_id)
        if self.on_deleted:
            self.on_deleted()
