# PyInstaller spec file for Optics Simulator
# 运行: conda activate finesse && pyinstaller optics_sim.spec

import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 收集项目 Python 模块
project_dir = os.path.dirname(os.path.abspath(SPECPATH))
sys.path.insert(0, project_dir)

# 收集 finesse 的数据文件（如 finesse.ini）和所有子模块
finesse_datas = collect_data_files('finesse')
finesse_hidden = collect_submodules('finesse')

a = Analysis(
    ['launcher.py'],
    pathex=[project_dir],
    binaries=[
        (r'C:\Users\89589\.conda\envs\finesse\Library\bin\klu.dll', '.'),
    ],
    datas=[
        ('templates/index.html', 'templates'),
        ('templates/jupyter.html', 'templates'),
        ('static', 'static'),
        ('node_modules', 'node_modules'),
    ] + finesse_datas,
    hiddenimports=[
        # 项目模块
        'component_registry',
        'finesse_engine',
        'debug',
        # 基础依赖
        'numpy',
        'scipy',
        'scipy.sparse',
        'scipy.sparse.linalg',
        'networkx',
        'click',
        'dill',
        'matplotlib',
        'deprecated',
    ] + finesse_hidden,
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
        'sphinx',
        'cv2',
        'pandas',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='OpticsSimulator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # 显示控制台窗口（查看日志）
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
