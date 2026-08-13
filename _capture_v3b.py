import subprocess
from datetime import date

import customtkinter as ctk
from database.db_session import init_db, get_session
from services.activity_service import ActivityService
from models.activity import ActivityType, ActivityStatus
from models.reflection import Reflection
from views.main_window import MainWindow
from views.activity_form_view import ActivityFormView

init_db()

with get_session() as session:
    a1 = ActivityService(session).create_activity(
        title="교내 창업 공모전", activity_type=ActivityType.CONTEST,
        date_start=date(2026, 3, 1), status=ActivityStatus.DONE, importance=5,
        purpose="팀 프로젝트 경험을 쌓고 싶어서 참가했습니다.",
        content="4인 팀으로 아이디어 기획부터 발표까지 진행했습니다.",
        category_names=["협업", "도전", "창의성"], tag_names=["공모전", "AI"],
    )
    session.add(Reflection(activity_id=a1.id, learned="협업의 중요성을 느꼈다", next_action="팀 프로젝트를 더 해보고 싶다"))
    session.commit()

app = MainWindow()

def capture(name):
    app.update()
    subprocess.run(["import", "-window", "root", f"/home/claude/screenshot_{name}.png"])

def open_detail():
    app.open_activity_detail(1)
    app.after(400, lambda: (capture("activity_detail"), app.after(200, open_form)))

def open_form():
    form = ActivityFormView(app, activity=None, on_saved=lambda: None)
    def scroll_and_capture():
        # 스크롤 가능한 프레임을 맨 아래로 이동해서 카테고리 체크박스가 보이게 함
        for child in form.winfo_children():
            if isinstance(child, ctk.CTkScrollableFrame):
                child._parent_canvas.yview_moveto(1.0)
        app.update()
        capture("activity_form_categories")
        form.destroy()
        app.after(200, app.destroy)
    app.after(400, scroll_and_capture)

app.after(500, open_detail)
app.mainloop()
print("DONE")
