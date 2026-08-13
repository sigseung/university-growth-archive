"""
main.py

앱 실행 진입점. 이 파일은 최대한 짧게 유지합니다.
실제 로직은 전부 views/ 이하로 위임합니다.

실행 방법:
    python main.py
"""

from views.main_window import MainWindow


def main():
    app = MainWindow()
    app.mainloop()


if __name__ == "__main__":
    main()
