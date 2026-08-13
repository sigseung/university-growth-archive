# uga.spec
#
# PyInstaller가 이 프로젝트를 하나의 실행파일(.exe / .app / 리눅스 바이너리)로
# 묶을 때 사용하는 설정 파일입니다.
#
# 빌드 방법:
#     pyinstaller uga.spec
# 결과물은 dist/UGA/ (또는 dist/UGA.exe, macOS는 dist/UGA.app) 에 생성됩니다.
#
# ★ customtkinter는 자체 폰트/테마 파일을 패키지 내부에 두기 때문에,
#   datas에 customtkinter 리소스를 명시적으로 포함시켜야 실행파일에서도
#   깨지지 않고 정상적으로 UI가 뜹니다. (일반 PyInstaller 자동 탐지로는
#   이 리소스 파일들이 자동으로 안 딸려오는 경우가 있습니다.)

import customtkinter
from pathlib import Path

customtkinter_path = Path(customtkinter.__file__).parent

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        (str(customtkinter_path), 'customtkinter'),
    ],
    hiddenimports=[
        'PIL._tkinter_finder',  # Pillow + Tkinter 조합에서 종종 누락되는 임포트
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='UGA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # False: 콘솔 창 없이 GUI만 뜸 (배포용). 디버깅 시 True로 바꿔서 에러 로그 확인 가능
    icon=None,  # assets/icons/ 에 .ico(Windows) 또는 .icns(macOS) 파일을 넣으면 여기에 경로 지정
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='UGA',
)
