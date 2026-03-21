import csv
import hashlib
import importlib
import importlib.util
import os
import threading
import tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

#===============================================================
# File Name : hash_viewer_gui_dev.py
# Purpose   : SHA256 hash viewer / CSV export / version comparison / D&D support
# Version   : v3.2-dev
# Summary   : Supports Japanese/English UI switching, A/B comparison,
#             and Developer Mode (release hashlist generation)
# 備考      : 日本語UIにも対応した汎用ハッシュ管理ツール
#===============================================================

# ---------------------------------------------------------------
# Drag & Drop Support Library
# Install if needed:
#   pip install tkinterdnd2
# ---------------------------------------------------------------

# ---------------------------------------------------------------
# Build Instructions (PyInstaller)
# 1. Install required packages:
#      pip install pyinstaller
#      pip install tkinterdnd2
#
# 2. Build executable:
#      pyinstaller --noconsole --onefile --icon=assets/app.ico src/hash_viewer_gui.py
#
# 3. Output:
#      The executable will be generated in the "dist" folder.
#
# Notes:
# - Run the command from the project root.
# - If you include assets, add:
#      --add-data "assets;assets"
# ---------------------------------------------------------------

import csv
import hashlib
...
_tkinterdnd2_spec = importlib.util.find_spec("tkinterdnd2")
if _tkinterdnd2_spec is not None:
    tkinterdnd2_module = importlib.import_module("tkinterdnd2")
    DND_FILES = tkinterdnd2_module.DND_FILES
    TkinterDnD = tkinterdnd2_module.TkinterDnD
    DND_AVAILABLE = True
else:
    TkinterDnD = None
    DND_FILES = None
    DND_AVAILABLE = False

APP_VERSION = "v3.2-dev"
APP_GEOMETRY = "1280x920"
CHUNK_SIZE = 1024 * 1024  # 1MBずつ読む

CSV_HEADER = [
    "version_name",
    "saved_at",
    "base_path",
    "target_type",
    "relative_path",
    "full_path",
    "file_size",
    "last_modified",
    "sha256",
]

TEXTS = {
    "ja": {
        "app_title": "SHA256 ハッシュ管理ツール",
        "app_subtitle": "ファイル / フォルダの SHA256 を計算し、バージョン管理・比較できます",
        "group_actions": "操作",
        "group_dnd": "ドラッグ＆ドロップ",
        "group_checksum": "入力チェックサム比較",
        "group_ab_compare": "事前指定の比較対象",
        "group_results": "結果表示",
        "group_compare": "比較結果",
        "group_dev_mode": "開発者モード",
        "group_release_tools": "Release 用ハッシュ生成",
        "label_version": "バージョン名:",
        "label_target": "現在の対象:",
        "label_language": "表示言語:",
        "label_checksum": "比較したいSHA256:",
        "label_compare_a": "比較対象A:",
        "label_compare_b": "比較対象B:",
        "label_release_files": "対象ファイル:",
        "label_release_output": "生成結果:",
        "check_dev_mode": "開発者モード",
        "dnd_enabled": "ここへファイルまたはフォルダをドロップしてください。",
        "dnd_disabled": "ドラッグ＆ドロップを使うには tkinterdnd2 のインストールが必要です: pip install tkinterdnd2",
        "checksum_header": "比較対象のチェックサム入力欄に、照合したい SHA256 を貼り付けて比較できます。",
        "ab_header": "A と B を先に指定して、直接 SHA256 比較できます。",
        "dev_header": "配布者 / 開発者向け。EXE / ZIP / PY などのハッシュ一覧を生成できます。",
        "btn_select_file": "ファイルを選ぶ",
        "btn_select_folder": "フォルダを選ぶ",
        "btn_save_csv": "CSV保存",
        "btn_compare_input": "入力チェックサムと比較",
        "btn_compare_csv": "CSV読込して比較",
        "btn_copy_result": "結果をコピー",
        "btn_clear": "クリア",
        "btn_clear_input": "入力欄クリア",
        "btn_a_file": "A: ファイル",
        "btn_a_folder": "A: フォルダ",
        "btn_b_file": "B: ファイル",
        "btn_b_folder": "B: フォルダ",
        "btn_ab_compare": "A/B比較",
        "btn_release_select": "Release対象を選ぶ",
        "btn_release_generate": "ハッシュ生成",
        "btn_release_copy": "生成結果をコピー",
        "btn_release_clear": "開発者欄クリア",
        "status_ready": "準備完了",
        "status_cleared": "クリアしました",
        "status_checksum_input_cleared": "比較用チェックサム入力欄をクリアしました",
        "status_release_cleared": "開発者モード欄をクリアしました",
        "status_scanning": "SHA256 を計算中です...",
        "status_scan_done": "計算完了: {count} 件",
        "status_error": "エラーが発生しました",
        "status_copied": "結果をコピーしました",
        "status_csv_saved": "CSV保存完了: {path}",
        "status_compare_done": "比較が完了しました",
        "status_checksum_match": "入力チェックサム比較完了: {count} 件一致",
        "status_checksum_no_match": "入力チェックサム比較完了: 一致なし",
        "status_ab_match": "A/B比較完了: 一致",
        "status_ab_no_match": "A/B比較完了: 不一致",
        "status_release_generated": "Release用ハッシュを生成しました",
        "status_release_copied": "Release用ハッシュをコピーしました",
        "msg_error_title": "エラー",
        "msg_copy_title": "コピー",
        "msg_compare_title": "比較",
        "msg_csv_save_title": "CSV保存",
        "msg_csv_save_error_title": "CSV保存エラー",
        "msg_input_warning_title": "入力不足",
        "msg_format_warning_title": "形式エラー",
        "msg_compare_error_title": "比較エラー",
        "msg_release_title": "Release用ハッシュ",
        "msg_no_target_loaded": "先にファイルまたはフォルダを読み込んでください。",
        "msg_no_current_for_compare": "先に現在のファイルまたはフォルダを読み込んでください。",
        "msg_path_not_found": "指定パスが見つかりません。\n\n{path}",
        "msg_scan_error": "SHA256 計算中にエラーが発生しました。\n\n{error}",
        "msg_nothing_to_copy": "コピーする内容がありません。",
        "msg_copied": "結果をクリップボードにコピーしました。",
        "msg_need_version": "バージョン名を入力してください。",
        "msg_csv_saved": "CSV保存が完了しました。\n\n{path}",
        "msg_csv_save_error": "CSV保存に失敗しました。\n\n{error}",
        "msg_need_checksum": "比較したい SHA256 を入力してください。",
        "msg_bad_checksum": "SHA256 は 64 文字の16進数で入力してください。",
        "msg_compare_error": "比較処理に失敗しました。\n\n{error}",
        "msg_no_match": "一致するファイルは見つかりませんでした。",
        "msg_need_ab": "比較対象Aと比較対象Bの両方を指定してください。",
        "msg_a_not_found": "比較対象Aが見つかりません。\n\n{path}",
        "msg_b_not_found": "比較対象Bが見つかりません。\n\n{path}",
        "msg_ab_type_mismatch": "A と B は同じ種類で指定してください。\n\n例: ファイル同士 / フォルダ同士",
        "msg_ab_compare_error": "A/B比較に失敗しました。\n\n{error}",
        "msg_need_release_files": "Release用ハッシュを生成するファイルを選択してください。",
        "msg_need_release_output": "Release用ハッシュの生成結果がありません。",
        "msg_release_generated": "Release用ハッシュを生成しました。",
        "msg_release_copied": "Release用ハッシュをコピーしました。",
        "result_target": "【対象】",
        "result_type": "【種別】",
        "result_count": "【件数】",
        "result_file_type": "file",
        "result_folder_type": "folder",
        "compare_input_title": "【入力チェックサムとの比較結果】",
        "compare_checksum_label": "比較対象SHA256",
        "compare_match_count": "一致件数",
        "compare_match_tag": "[一致]",
        "compare_csv_source": "比較元CSV",
        "compare_old_version": "旧バージョン",
        "compare_new_version": "新バージョン",
        "compare_summary": "【集計】",
        "compare_added": "追加",
        "compare_removed": "削除",
        "compare_changed": "変更",
        "compare_unchanged": "未変更",
        "compare_added_title": "【追加】",
        "compare_removed_title": "【削除】",
        "compare_changed_title": "【変更】",
        "compare_no_diff": "差分はありません。",
        "compare_ab_title": "【事前指定A/B比較結果】",
        "compare_ab_judgement": "判定",
        "compare_ab_match": "一致",
        "compare_ab_no_match": "不一致",
        "compare_ab_a": "A",
        "compare_ab_b": "B",
        "compare_ab_sha_a": "SHA256(A)",
        "compare_ab_sha_b": "SHA256(B)",
        "compare_ab_folder_summary": "【フォルダ比較集計】",
        "release_output_title": "【Release用ハッシュ一覧】",
        "release_version": "Version",
        "release_file_count": "対象件数",
        "release_target_file": "ファイル名",
        "release_sha256": "SHA256",
        "unknown": "(不明)",
        "not_entered": "(未入力)",
        "save_dialog_title": "CSV保存",
        "open_compare_csv_title": "比較するCSVを選択",
        "select_file_title": "SHA256 を計算するファイルを選択",
        "select_folder_title": "SHA256 を計算するフォルダを選択",
        "select_compare_a_file": "比較対象Aのファイルを選択",
        "select_compare_a_folder": "比較対象Aのフォルダを選択",
        "select_compare_b_file": "比較対象Bのファイルを選択",
        "select_compare_b_folder": "比較対象Bのフォルダを選択",
        "select_release_files_title": "Release用ハッシュを生成するファイルを選択",
        "language_options": ["日本語", "English"],
        "language_map": {"日本語": "ja", "English": "en"},
    },
    "en": {
        "app_title": "SHA256 Hash Manager",
        "app_subtitle": "Calculate SHA256 for files or folders, manage versions, and compare results",
        "group_actions": "Actions",
        "group_dnd": "Drag & Drop",
        "group_checksum": "Input Checksum Comparison",
        "group_ab_compare": "Preselected Comparison Targets",
        "group_results": "Results",
        "group_compare": "Comparison Result",
        "group_dev_mode": "Developer Mode",
        "group_release_tools": "Release Hash Generator",
        "label_version": "Version:",
        "label_target": "Current Target:",
        "label_language": "Language:",
        "label_checksum": "SHA256 to compare:",
        "label_compare_a": "Target A:",
        "label_compare_b": "Target B:",
        "label_release_files": "Target Files:",
        "label_release_output": "Generated Result:",
        "check_dev_mode": "Developer Mode",
        "dnd_enabled": "Drop a file or folder here.",
        "dnd_disabled": "To use drag & drop, install tkinterdnd2: pip install tkinterdnd2",
        "checksum_header": "Paste the SHA256 checksum you want to verify into the field below.",
        "ab_header": "Specify A and B first, then compare their SHA256 values directly.",
        "dev_header": "For developers / distributors. Generate hash lists for EXE / ZIP / PY files.",
        "btn_select_file": "Select File",
        "btn_select_folder": "Select Folder",
        "btn_save_csv": "Save CSV",
        "btn_compare_input": "Compare with Input Checksum",
        "btn_compare_csv": "Compare with CSV",
        "btn_copy_result": "Copy Result",
        "btn_clear": "Clear",
        "btn_clear_input": "Clear Input",
        "btn_a_file": "A: File",
        "btn_a_folder": "A: Folder",
        "btn_b_file": "B: File",
        "btn_b_folder": "B: Folder",
        "btn_ab_compare": "Compare A/B",
        "btn_release_select": "Select Release Files",
        "btn_release_generate": "Generate Hash List",
        "btn_release_copy": "Copy Generated Result",
        "btn_release_clear": "Clear Developer Fields",
        "status_ready": "Ready",
        "status_cleared": "Cleared",
        "status_checksum_input_cleared": "Checksum input cleared",
        "status_release_cleared": "Developer fields cleared",
        "status_scanning": "Calculating SHA256...",
        "status_scan_done": "Completed: {count} item(s)",
        "status_error": "An error occurred",
        "status_copied": "Result copied",
        "status_csv_saved": "CSV saved: {path}",
        "status_compare_done": "Comparison completed",
        "status_checksum_match": "Checksum comparison completed: {count} match(es)",
        "status_checksum_no_match": "Checksum comparison completed: no match",
        "status_ab_match": "A/B comparison completed: MATCH",
        "status_ab_no_match": "A/B comparison completed: DIFFERENT",
        "status_release_generated": "Release hash list generated",
        "status_release_copied": "Release hash list copied",
        "msg_error_title": "Error",
        "msg_copy_title": "Copy",
        "msg_compare_title": "Compare",
        "msg_csv_save_title": "Save CSV",
        "msg_csv_save_error_title": "CSV Save Error",
        "msg_input_warning_title": "Input Required",
        "msg_format_warning_title": "Format Error",
        "msg_compare_error_title": "Comparison Error",
        "msg_release_title": "Release Hash Generator",
        "msg_no_target_loaded": "Please load a file or folder first.",
        "msg_no_current_for_compare": "Please load the current file or folder first.",
        "msg_path_not_found": "The specified path was not found.\n\n{path}",
        "msg_scan_error": "An error occurred while calculating SHA256.\n\n{error}",
        "msg_nothing_to_copy": "There is nothing to copy.",
        "msg_copied": "The result has been copied to the clipboard.",
        "msg_need_version": "Please enter a version name.",
        "msg_csv_saved": "CSV saved successfully.\n\n{path}",
        "msg_csv_save_error": "Failed to save CSV.\n\n{error}",
        "msg_need_checksum": "Please enter a SHA256 checksum to compare.",
        "msg_bad_checksum": "SHA256 must be a 64-character hexadecimal string.",
        "msg_compare_error": "Comparison failed.\n\n{error}",
        "msg_no_match": "No matching file was found.",
        "msg_need_ab": "Please specify both Target A and Target B.",
        "msg_a_not_found": "Target A was not found.\n\n{path}",
        "msg_b_not_found": "Target B was not found.\n\n{path}",
        "msg_ab_type_mismatch": "A and B must be the same type.\n\nExample: file vs file / folder vs folder",
        "msg_ab_compare_error": "A/B comparison failed.\n\n{error}",
        "msg_need_release_files": "Please select files for release hash generation.",
        "msg_need_release_output": "There is no generated release hash output.",
        "msg_release_generated": "Release hash list generated.",
        "msg_release_copied": "Release hash list copied.",
        "result_target": "[Target]",
        "result_type": "[Type]",
        "result_count": "[Count]",
        "result_file_type": "file",
        "result_folder_type": "folder",
        "compare_input_title": "[Input Checksum Comparison Result]",
        "compare_checksum_label": "Checksum",
        "compare_match_count": "Matches",
        "compare_match_tag": "[MATCH]",
        "compare_csv_source": "Source CSV",
        "compare_old_version": "Old Version",
        "compare_new_version": "New Version",
        "compare_summary": "[Summary]",
        "compare_added": "Added",
        "compare_removed": "Removed",
        "compare_changed": "Changed",
        "compare_unchanged": "Unchanged",
        "compare_added_title": "[Added]",
        "compare_removed_title": "[Removed]",
        "compare_changed_title": "[Changed]",
        "compare_no_diff": "No differences were found.",
        "compare_ab_title": "[Preselected A/B Comparison Result]",
        "compare_ab_judgement": "Judgement",
        "compare_ab_match": "MATCH",
        "compare_ab_no_match": "DIFFERENT",
        "compare_ab_a": "A",
        "compare_ab_b": "B",
        "compare_ab_sha_a": "SHA256(A)",
        "compare_ab_sha_b": "SHA256(B)",
        "compare_ab_folder_summary": "[Folder Comparison Summary]",
        "release_output_title": "[Release Hash List]",
        "release_version": "Version",
        "release_file_count": "Item Count",
        "release_target_file": "File Name",
        "release_sha256": "SHA256",
        "unknown": "(Unknown)",
        "not_entered": "(Not entered)",
        "save_dialog_title": "Save CSV",
        "open_compare_csv_title": "Select CSV to compare",
        "select_file_title": "Select a file to calculate SHA256",
        "select_folder_title": "Select a folder to calculate SHA256",
        "select_compare_a_file": "Select file for Target A",
        "select_compare_a_folder": "Select folder for Target A",
        "select_compare_b_file": "Select file for Target B",
        "select_compare_b_folder": "Select folder for Target B",
        "select_release_files_title": "Select files for release hash generation",
        "language_options": ["日本語", "English"],
        "language_map": {"日本語": "ja", "English": "en"},
    },
}


@dataclass
class HashRecord:
    """
    1ファイル分のハッシュ情報
    """
    relative_path: str
    full_path: str
    file_size: int
    last_modified: str
    sha256: str


class HashViewerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.lang = "ja"

        self.current_records: list[HashRecord] = []
        self.current_base_path: str = ""
        self.current_target_type: str = ""
        self.current_target_label: str = ""
        self.scan_thread = None
        self.is_busy = False

        self.compare_a_path: str = ""
        self.compare_b_path: str = ""

        self.version_name_var = tk.StringVar(value=APP_VERSION)
        self.target_var = tk.StringVar(value="")
        self.checksum_input_var = tk.StringVar()
        self.compare_a_var = tk.StringVar()
        self.compare_b_var = tk.StringVar()
        self.status_var = tk.StringVar(value="")
        self.language_display_var = tk.StringVar(value="日本語")

        self.dev_mode_var = tk.BooleanVar(value=False)
        self.release_file_paths: list[str] = []
        self.release_paths_var = tk.StringVar(value="")
        self.release_output_var = tk.StringVar(value="")

        self.root.geometry(APP_GEOMETRY)
        self._build_ui()
        self.apply_language()
        self._set_status(self.t("status_ready"))

    def t(self, key: str) -> str:
        return TEXTS[self.lang][key]

    def _build_ui(self) -> None:
        """
        画面部品を作成
        """
        outer = ttk.Frame(self.root, padding=10)
        outer.pack(fill="both", expand=True)

        # 開発者モードチェック
        self.chk_dev_mode = ttk.Checkbutton(
            outer,
            text="",
            variable=self.dev_mode_var,
            command=self.toggle_dev_mode,
        )
        self.chk_dev_mode.pack(anchor="w", pady=(0, 5))

        self.title_label = ttk.Label(
            outer,
            text="",
            font=("Yu Gothic UI", 11, "bold"),
            justify="left",
        )
        self.title_label.pack(anchor="w", pady=(0, 8))

        # 上部操作エリア
        self.top_group = ttk.LabelFrame(outer, text="", padding=10)
        self.top_group.pack(fill="x", pady=(0, 10))

        row1 = ttk.Frame(self.top_group)
        row1.pack(fill="x", pady=(0, 8))

        self.btn_select_file = ttk.Button(row1, text="", command=self.select_file)
        self.btn_select_file.pack(side="left", padx=(0, 6))

        self.btn_select_folder = ttk.Button(row1, text="", command=self.select_folder)
        self.btn_select_folder.pack(side="left", padx=(0, 6))

        self.btn_save_csv = ttk.Button(row1, text="", command=self.save_csv)
        self.btn_save_csv.pack(side="left", padx=(0, 6))

        self.btn_compare_input = ttk.Button(row1, text="", command=self.compare_with_input_checksum)
        self.btn_compare_input.pack(side="left", padx=(0, 6))

        self.btn_compare_csv = ttk.Button(row1, text="", command=self.compare_with_csv)
        self.btn_compare_csv.pack(side="left", padx=(0, 6))

        self.btn_copy_result = ttk.Button(row1, text="", command=self.copy_result)
        self.btn_copy_result.pack(side="left", padx=(0, 6))

        self.btn_clear = ttk.Button(row1, text="", command=self.clear_result)
        self.btn_clear.pack(side="left")

        row2 = ttk.Frame(self.top_group)
        row2.pack(fill="x")

        self.label_version = ttk.Label(row2, text="")
        self.label_version.pack(side="left")
        self.version_entry = ttk.Entry(row2, textvariable=self.version_name_var, width=18)
        self.version_entry.pack(side="left", padx=(6, 14))

        self.label_target = ttk.Label(row2, text="")
        self.label_target.pack(side="left")
        self.target_entry = ttk.Entry(row2, textvariable=self.target_var, width=58, state="readonly")
        self.target_entry.pack(side="left", padx=(6, 14), fill="x", expand=True)

        self.label_language = ttk.Label(row2, text="")
        self.label_language.pack(side="left")
        self.language_combo = ttk.Combobox(
            row2,
            textvariable=self.language_display_var,
            width=10,
            state="readonly",
        )
        self.language_combo.pack(side="left", padx=(6, 0))
        self.language_combo.bind("<<ComboboxSelected>>", self.on_language_change)

        # D&Dエリア
        self.dnd_group = ttk.LabelFrame(outer, text="", padding=10)
        self.dnd_group.pack(fill="x", pady=(0, 10))

        self.drop_label = tk.Label(
            self.dnd_group,
            text="",
            relief="groove",
            bd=2,
            padx=10,
            pady=18,
            anchor="center",
            font=("Yu Gothic UI", 10),
        )
        self.drop_label.pack(fill="x")

        if DND_AVAILABLE and DND_FILES is not None:
            self.drop_label.drop_target_register(DND_FILES)
            self.drop_label.dnd_bind("<<Drop>>", self.on_drop)

        
        # 入力チェックサム比較エリア
        self.checksum_group = ttk.LabelFrame(outer, text="", padding=8)
        self.checksum_group.pack(fill="x", pady=(0, 10))

        checksum_row1 = ttk.Frame(self.checksum_group)
        checksum_row1.pack(fill="x", pady=(0, 6))

        self.checksum_header_label = ttk.Label(checksum_row1, text="")
        self.checksum_header_label.pack(anchor="w")

        checksum_row2 = ttk.Frame(self.checksum_group)
        checksum_row2.pack(fill="x")

        self.label_checksum = ttk.Label(checksum_row2, text="")
        self.label_checksum.pack(side="left")

        self.checksum_entry = ttk.Entry(checksum_row2, textvariable=self.checksum_input_var, width=90)
        self.checksum_entry.pack(side="left", padx=(8, 8), fill="x", expand=True)

        self.btn_clear_input = ttk.Button(checksum_row2, text="", command=self.clear_checksum_input)
        self.btn_clear_input.pack(side="left")

        # A/B事前指定比較エリア
        self.ab_group = ttk.LabelFrame(outer, text="", padding=8)
        self.ab_group.pack(fill="x", pady=(0, 10))

        ab_row0 = ttk.Frame(self.ab_group)
        ab_row0.pack(fill="x", pady=(0, 6))
        self.ab_header_label = ttk.Label(ab_row0, text="")
        self.ab_header_label.pack(anchor="w")

        ab_row1 = ttk.Frame(self.ab_group)
        ab_row1.pack(fill="x", pady=(0, 6))

        self.label_compare_a = ttk.Label(ab_row1, text="")
        self.label_compare_a.pack(side="left")

        self.compare_a_entry = ttk.Entry(ab_row1, textvariable=self.compare_a_var, width=72)
        self.compare_a_entry.pack(side="left", padx=(8, 8), fill="x", expand=True)

        self.btn_a_file = ttk.Button(ab_row1, text="", command=self.select_compare_a_file)
        self.btn_a_file.pack(side="left", padx=(0, 6))

        self.btn_a_folder = ttk.Button(ab_row1, text="", command=self.select_compare_a_folder)
        self.btn_a_folder.pack(side="left")

        ab_row2 = ttk.Frame(self.ab_group)
        ab_row2.pack(fill="x", pady=(0, 6))

        self.label_compare_b = ttk.Label(ab_row2, text="")
        self.label_compare_b.pack(side="left")

        self.compare_b_entry = ttk.Entry(ab_row2, textvariable=self.compare_b_var, width=72)
        self.compare_b_entry.pack(side="left", padx=(8, 8), fill="x", expand=True)

        self.btn_b_file = ttk.Button(ab_row2, text="", command=self.select_compare_b_file)
        self.btn_b_file.pack(side="left", padx=(0, 6))

        self.btn_b_folder = ttk.Button(ab_row2, text="", command=self.select_compare_b_folder)
        self.btn_b_folder.pack(side="left")

        ab_row3 = ttk.Frame(self.ab_group)
        ab_row3.pack(fill="x")

        self.btn_ab_compare = ttk.Button(ab_row3, text="", command=self.compare_preselected_targets)
        self.btn_ab_compare.pack(side="left")

        # 開発者モードエリア（初期は非表示）
        self.dev_group = ttk.LabelFrame(outer, text="", padding=8)

        dev_row0 = ttk.Frame(self.dev_group)
        dev_row0.pack(fill="x", pady=(0, 6))

        self.dev_header_label = ttk.Label(dev_row0, text="")
        self.dev_header_label.pack(anchor="w")

        dev_row1 = ttk.Frame(self.dev_group)
        dev_row1.pack(fill="x", pady=(0, 6))

        self.label_release_files = ttk.Label(dev_row1, text="")
        self.label_release_files.pack(side="left")

        self.release_paths_entry = ttk.Entry(
            dev_row1,
            textvariable=self.release_paths_var,
            width=72,
            state="readonly",
        )
        self.release_paths_entry.pack(side="left", padx=(8, 8), fill="x", expand=True)

        self.btn_release_select = ttk.Button(
            dev_row1,
            text="",
            command=self.select_release_files,
        )
        self.btn_release_select.pack(side="left", padx=(0, 6))

        self.btn_release_generate = ttk.Button(
            dev_row1,
            text="",
            command=self.generate_release_hash,
        )
        self.btn_release_generate.pack(side="left", padx=(0, 6))

        dev_row2 = ttk.Frame(self.dev_group)
        dev_row2.pack(fill="x", pady=(0, 6))

        self.label_release_output = ttk.Label(dev_row2, text="")
        self.label_release_output.pack(side="left")

        self.btn_release_copy = ttk.Button(
            dev_row2,
            text="",
            command=self.copy_release_output,
        )
        self.btn_release_copy.pack(side="left", padx=(8, 6))

        self.btn_release_clear = ttk.Button(
            dev_row2,
            text="",
            command=self.clear_release_fields,
        )
        self.btn_release_clear.pack(side="left")

        dev_row3 = ttk.Frame(self.dev_group)
        dev_row3.pack(fill="both", expand=True)

        self.release_output_text = tk.Text(dev_row3, wrap="none", height=10, font=("Consolas", 10))
        self.release_output_text.pack(side="left", fill="both", expand=True)

        release_scroll = ttk.Scrollbar(dev_row3, orient="vertical", command=self.release_output_text.yview)
        release_scroll.pack(side="right", fill="y")
        self.release_output_text.configure(yscrollcommand=release_scroll.set)
        # ★ここに追加
        self.dev_group.pack(fill="x", pady=(0, 10))
        self.dev_group.pack_forget()

        # 中央分割エリア
        self.center = ttk.Panedwindow(outer, orient="horizontal")
        self.center.pack(fill="both", expand=True)

        left = ttk.Frame(self.center)
        right = ttk.Frame(self.center)
        self.center.add(left, weight=3)
        self.center.add(right, weight=2)

        self.result_group = ttk.LabelFrame(left, text="", padding=8)
        self.result_group.pack(fill="both", expand=True)

        self.result_text = tk.Text(self.result_group, wrap="none", font=("Consolas", 10))
        self.result_text.pack(side="left", fill="both", expand=True)

        y_scroll = ttk.Scrollbar(self.result_group, orient="vertical", command=self.result_text.yview)
        y_scroll.pack(side="right", fill="y")
        self.result_text.configure(yscrollcommand=y_scroll.set)

        x_scroll = ttk.Scrollbar(left, orient="horizontal", command=self.result_text.xview)
        x_scroll.pack(fill="x")
        self.result_text.configure(xscrollcommand=x_scroll.set)

        self.compare_group = ttk.LabelFrame(right, text="", padding=8)
        self.compare_group.pack(fill="both", expand=True)

        self.compare_text = tk.Text(self.compare_group, wrap="none", font=("Consolas", 10))
        self.compare_text.pack(side="left", fill="both", expand=True)

        cmp_scroll = ttk.Scrollbar(self.compare_group, orient="vertical", command=self.compare_text.yview)
        cmp_scroll.pack(side="right", fill="y")
        self.compare_text.configure(yscrollcommand=cmp_scroll.set)

        status_frame = ttk.Frame(outer)
        status_frame.pack(fill="x", pady=(8, 0))

        self.progress = ttk.Progressbar(status_frame, mode="indeterminate")
        self.progress.pack(side="left", fill="x", expand=True, padx=(0, 10))

        ttk.Label(status_frame, textvariable=self.status_var).pack(side="left")

        self.toggle_dev_mode()

    def apply_language(self) -> None:
        """
        現在の言語設定をUIへ反映
        """
        self.root.title(f"{self.t('app_title')} {APP_VERSION}")
        self.title_label.configure(
            text=f"{self.t('app_title')} {APP_VERSION}\n{self.t('app_subtitle')}"
        )

        self.chk_dev_mode.configure(text=self.t("check_dev_mode"))

        self.top_group.configure(text=self.t("group_actions"))
        self.dnd_group.configure(text=self.t("group_dnd"))
        self.checksum_group.configure(text=self.t("group_checksum"))
        self.ab_group.configure(text=self.t("group_ab_compare"))
        self.dev_group.configure(text=self.t("group_release_tools"))
        self.result_group.configure(text=self.t("group_results"))
        self.compare_group.configure(text=self.t("group_compare"))

        self.label_version.configure(text=self.t("label_version"))
        self.label_target.configure(text=self.t("label_target"))
        self.label_language.configure(text=self.t("label_language"))
        self.label_checksum.configure(text=self.t("label_checksum"))
        self.label_compare_a.configure(text=self.t("label_compare_a"))
        self.label_compare_b.configure(text=self.t("label_compare_b"))
        self.label_release_files.configure(text=self.t("label_release_files"))
        self.label_release_output.configure(text=self.t("label_release_output"))

        self.btn_select_file.configure(text=self.t("btn_select_file"))
        self.btn_select_folder.configure(text=self.t("btn_select_folder"))
        self.btn_save_csv.configure(text=self.t("btn_save_csv"))
        self.btn_compare_input.configure(text=self.t("btn_compare_input"))
        self.btn_compare_csv.configure(text=self.t("btn_compare_csv"))
        self.btn_copy_result.configure(text=self.t("btn_copy_result"))
        self.btn_clear.configure(text=self.t("btn_clear"))
        self.btn_clear_input.configure(text=self.t("btn_clear_input"))
        self.btn_a_file.configure(text=self.t("btn_a_file"))
        self.btn_a_folder.configure(text=self.t("btn_a_folder"))
        self.btn_b_file.configure(text=self.t("btn_b_file"))
        self.btn_b_folder.configure(text=self.t("btn_b_folder"))
        self.btn_ab_compare.configure(text=self.t("btn_ab_compare"))
        self.btn_release_select.configure(text=self.t("btn_release_select"))
        self.btn_release_generate.configure(text=self.t("btn_release_generate"))
        self.btn_release_copy.configure(text=self.t("btn_release_copy"))
        self.btn_release_clear.configure(text=self.t("btn_release_clear"))

        self.drop_label.configure(
            text=self.t("dnd_enabled") if DND_AVAILABLE else self.t("dnd_disabled")
        )
        self.checksum_header_label.configure(text=self.t("checksum_header"))
        self.ab_header_label.configure(text=self.t("ab_header"))
        self.dev_header_label.configure(text=self.t("dev_header"))

        options = self.t("language_options")
        self.language_combo["values"] = options

        if self.lang == "ja":
            self.language_display_var.set("日本語")
        else:
            self.language_display_var.set("English")

        if not self.status_var.get():
            self._set_status(self.t("status_ready"))

    def on_language_change(self, _event=None) -> None:
        """
        言語切替
        """
        selected = self.language_display_var.get()
        reverse_map = {"日本語": "ja", "English": "en"}
        self.lang = reverse_map.get(selected, "ja")
        self.apply_language()

    def toggle_dev_mode(self) -> None:
        """
        開発者モードの表示 / 非表示
        """
        print("toggle_dev_mode 呼ばれた")

        self.dev_group.pack_forget()

        if self.dev_mode_var.get():
            self.dev_group.pack(fill="x", pady=(0, 10), before=self.center)
    def _set_status(self, text: str) -> None:
        self.status_var.set(text)
        self.root.update_idletasks()

    def _set_busy(self, busy: bool, message: str = "") -> None:
        self.is_busy = busy
        if busy:
            self.progress.start(10)
            self._set_status(message)
        else:
            self.progress.stop()
            if message:
                self._set_status(message)

    def _write_result(self, text: str) -> None:
        self.result_text.insert(tk.END, text)
        self.result_text.see(tk.END)

    def _write_compare(self, text: str) -> None:
        self.compare_text.insert(tk.END, text)
        self.compare_text.see(tk.END)

    def clear_result(self) -> None:
        """
        結果欄をクリア
        """
        self.result_text.delete("1.0", tk.END)
        self.compare_text.delete("1.0", tk.END)
        self.current_records = []
        self.current_base_path = ""
        self.current_target_type = ""
        self.current_target_label = ""
        self.target_var.set("")
        self._set_status(self.t("status_cleared"))

    def clear_checksum_input(self) -> None:
        """
        比較用チェックサム入力欄をクリア
        """
        self.checksum_input_var.set("")
        self._set_status(self.t("status_checksum_input_cleared"))

    def clear_release_fields(self) -> None:
        """
        開発者モード欄をクリア
        """
        self.release_file_paths = []
        self.release_paths_var.set("")
        self.release_output_var.set("")
        self.release_output_text.delete("1.0", tk.END)
        self._set_status(self.t("status_release_cleared"))

    def select_file(self) -> None:
        if self.is_busy:
            return
        file_path = filedialog.askopenfilename(title=self.t("select_file_title"))
        if file_path:
            self.start_scan(file_path)

    def select_folder(self) -> None:
        if self.is_busy:
            return
        folder_path = filedialog.askdirectory(title=self.t("select_folder_title"))
        if folder_path:
            self.start_scan(folder_path)

    def select_compare_a_file(self) -> None:
        file_path = filedialog.askopenfilename(title=self.t("select_compare_a_file"))
        if file_path:
            self.compare_a_path = file_path
            self.compare_a_var.set(file_path)

    def select_compare_a_folder(self) -> None:
        folder_path = filedialog.askdirectory(title=self.t("select_compare_a_folder"))
        if folder_path:
            self.compare_a_path = folder_path
            self.compare_a_var.set(folder_path)

    def select_compare_b_file(self) -> None:
        file_path = filedialog.askopenfilename(title=self.t("select_compare_b_file"))
        if file_path:
            self.compare_b_path = file_path
            self.compare_b_var.set(file_path)

    def select_compare_b_folder(self) -> None:
        folder_path = filedialog.askdirectory(title=self.t("select_compare_b_folder"))
        if folder_path:
            self.compare_b_path = folder_path
            self.compare_b_var.set(folder_path)

    def select_release_files(self) -> None:
        """
        Release 用ハッシュ生成対象を選択
        """
        paths = filedialog.askopenfilenames(title=self.t("select_release_files_title"))
        if not paths:
            return

        self.release_file_paths = list(paths)

        if len(self.release_file_paths) == 1:
            self.release_paths_var.set(self.release_file_paths[0])
        else:
            display = f"{self.release_file_paths[0]}  ...  ({len(self.release_file_paths)} files)"
            self.release_paths_var.set(display)

    def on_drop(self, event) -> None:
        """
        ドロップされたパスを受け取る
        """
        if self.is_busy:
            return

        raw = event.data
        paths = self.root.tk.splitlist(raw)
        if not paths:
            return

        target = paths[0]
        self.start_scan(target)

    def start_scan(self, target_path: str) -> None:
        """
        スキャン開始
        """
        if self.is_busy:
            return

        path_obj = Path(target_path)
        if not path_obj.exists():
            messagebox.showerror(
                self.t("msg_error_title"),
                self.t("msg_path_not_found").format(path=target_path),
            )
            return

        self.result_text.delete("1.0", tk.END)
        self.compare_text.delete("1.0", tk.END)
        self.target_var.set(str(path_obj))
        self.current_target_label = str(path_obj)
        self._set_busy(True, self.t("status_scanning"))

        self.scan_thread = threading.Thread(
            target=self._scan_worker,
            args=(str(path_obj),),
            daemon=True,
        )
        self.scan_thread.start()

    def _scan_worker(self, target_path: str) -> None:
        """
        バックグラウンドで計算
        """
        try:
            path_obj = Path(target_path)
            records: list[HashRecord] = []

            if path_obj.is_file():
                records.append(self.build_record(path_obj, path_obj.parent))
                target_type = "file"
                base_path = str(path_obj.parent)
            else:
                target_type = "folder"
                base_path = str(path_obj)

                for file_path in sorted(p for p in path_obj.rglob("*") if p.is_file()):
                    records.append(self.build_record(file_path, path_obj))

            self.root.after(0, self.finish_scan, records, base_path, target_type)

        except Exception as e:
            self.root.after(0, self.scan_error, str(e))

    def build_record(self, file_path: Path, base_path: Path) -> HashRecord:
        """
        1ファイル分の記録を作成
        """
        stat = file_path.stat()
        return HashRecord(
            relative_path=os.path.relpath(str(file_path), str(base_path)),
            full_path=str(file_path),
            file_size=stat.st_size,
            last_modified=datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            sha256=self.sha256_file(str(file_path)),
        )

    def sha256_file(self, path: str) -> str:
        """
        SHA256 を計算
        """
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                sha256.update(chunk)
        return sha256.hexdigest()

    def build_folder_map(self, folder_path: str) -> dict[str, HashRecord]:
        """
        フォルダ配下のファイルを相対パス -> HashRecord の辞書にする
        """
        base = Path(folder_path)
        result: dict[str, HashRecord] = {}

        for file_path in sorted(p for p in base.rglob("*") if p.is_file()):
            rec = self.build_record(file_path, base)
            result[rec.relative_path] = rec

        return result

    def finish_scan(self, records: list[HashRecord], base_path: str, target_type: str) -> None:
        """
        計算完了後に画面へ反映
        """
        self.current_records = records
        self.current_base_path = base_path
        self.current_target_type = target_type

        self.result_text.delete("1.0", tk.END)
        self._write_result(f"{self.t('result_target')}\n{self.current_target_label}\n")
        self._write_result(f"{self.t('result_type')}\n{target_type}\n")
        self._write_result(f"{self.t('result_count')}\n{len(records)}\n\n")

        for rec in records:
            self._write_result(f"Path    : {rec.relative_path}\n")
            self._write_result(f"Size    : {rec.file_size:,} bytes\n")
            self._write_result(f"Updated : {rec.last_modified}\n")
            self._write_result(f"SHA256  : {rec.sha256}\n\n")

        self.version_name_var.set(APP_VERSION)
        self._set_busy(False, self.t("status_scan_done").format(count=len(records)))

    def scan_error(self, error_text: str) -> None:
        """
        エラー表示
        """
        self._set_busy(False, self.t("status_error"))
        messagebox.showerror(
            self.t("msg_error_title"),
            self.t("msg_scan_error").format(error=error_text),
        )

    def copy_result(self) -> None:
        """
        結果をクリップボードへコピー
        """
        result = self.result_text.get("1.0", tk.END).strip()
        compare = self.compare_text.get("1.0", tk.END).strip()
        combined = result

        if compare:
            combined += "\n\n===== Comparison =====\n" + compare

        if not combined.strip():
            messagebox.showinfo(self.t("msg_copy_title"), self.t("msg_nothing_to_copy"))
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(combined)
        self.root.update()
        self._set_status(self.t("status_copied"))
        messagebox.showinfo(self.t("msg_copy_title"), self.t("msg_copied"))

    def copy_release_output(self) -> None:
        """
        Release 用生成結果をコピー
        """
        text = self.release_output_text.get("1.0", tk.END).strip()
        if not text:
            messagebox.showinfo(self.t("msg_release_title"), self.t("msg_need_release_output"))
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self._set_status(self.t("status_release_copied"))
        messagebox.showinfo(self.t("msg_release_title"), self.t("msg_release_copied"))

    def save_csv(self) -> None:
        """
        現在の結果をCSVへ保存
        """
        if not self.current_records:
            messagebox.showinfo(self.t("msg_csv_save_title"), self.t("msg_no_target_loaded"))
            return

        version_name = self.version_name_var.get().strip()
        if not version_name:
            messagebox.showwarning(self.t("msg_input_warning_title"), self.t("msg_need_version"))
            return

        default_name = f"hash_{version_name}.csv"
        file_path = filedialog.asksaveasfilename(
            title=self.t("save_dialog_title"),
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return

        saved_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(CSV_HEADER)

                for rec in self.current_records:
                    writer.writerow([
                        version_name,
                        saved_at,
                        self.current_base_path,
                        self.current_target_type,
                        rec.relative_path,
                        rec.full_path,
                        rec.file_size,
                        rec.last_modified,
                        rec.sha256,
                    ])

            self._set_status(self.t("status_csv_saved").format(path=file_path))
            messagebox.showinfo(
                self.t("msg_csv_save_title"),
                self.t("msg_csv_saved").format(path=file_path),
            )

        except Exception as e:
            messagebox.showerror(
                self.t("msg_csv_save_error_title"),
                self.t("msg_csv_save_error").format(error=e),
            )

    def compare_with_input_checksum(self) -> None:
        """
        入力欄のチェックサムと現在結果を比較
        """
        if not self.current_records:
            messagebox.showinfo(self.t("msg_compare_title"), self.t("msg_no_target_loaded"))
            return

        target_checksum = self.checksum_input_var.get().strip().lower()
        if not target_checksum:
            messagebox.showwarning(self.t("msg_input_warning_title"), self.t("msg_need_checksum"))
            return

        if len(target_checksum) != 64 or any(c not in "0123456789abcdef" for c in target_checksum):
            messagebox.showwarning(self.t("msg_format_warning_title"), self.t("msg_bad_checksum"))
            return

        matched = [r for r in self.current_records if r.sha256.lower() == target_checksum]

        self.compare_text.delete("1.0", tk.END)
        self._write_compare(f"{self.t('compare_input_title')}\n")
        self._write_compare(f"{self.t('compare_checksum_label')}: {target_checksum}\n\n")

        if matched:
            self._write_compare(f"{self.t('compare_match_count')}: {len(matched)}\n\n")

            for rec in matched:
                self._write_compare(f"{self.t('compare_match_tag')} {rec.relative_path}\n")
                self._write_compare(f"  Size    : {rec.file_size:,} bytes\n")
                self._write_compare(f"  Updated : {rec.last_modified}\n")
                self._write_compare(f"  SHA256  : {rec.sha256}\n\n")

            self._set_status(self.t("status_checksum_match").format(count=len(matched)))
        else:
            self._write_compare(f"{self.t('msg_no_match')}\n")
            self._set_status(self.t("status_checksum_no_match"))

    def compare_preselected_targets(self) -> None:
        """
        事前指定した A / B を直接比較
        ・ファイル同士 -> ハッシュ直接比較
        ・フォルダ同士 -> 相対パスベースで比較
        """
        a_path = self.compare_a_var.get().strip()
        b_path = self.compare_b_var.get().strip()

        if not a_path or not b_path:
            messagebox.showwarning(self.t("msg_input_warning_title"), self.t("msg_need_ab"))
            return

        if not os.path.exists(a_path):
            messagebox.showerror(
                self.t("msg_error_title"),
                self.t("msg_a_not_found").format(path=a_path),
            )
            return

        if not os.path.exists(b_path):
            messagebox.showerror(
                self.t("msg_error_title"),
                self.t("msg_b_not_found").format(path=b_path),
            )
            return

        a_is_file = os.path.isfile(a_path)
        b_is_file = os.path.isfile(b_path)
        a_is_dir = os.path.isdir(a_path)
        b_is_dir = os.path.isdir(b_path)

        if (a_is_file and not b_is_file) or (a_is_dir and not b_is_dir):
            messagebox.showwarning(
                self.t("msg_format_warning_title"),
                self.t("msg_ab_type_mismatch"),
            )
            return

        try:
            self.compare_text.delete("1.0", tk.END)
            self._write_compare(f"{self.t('compare_ab_title')}\n")
            self._write_compare(f"{self.t('compare_ab_a')}: {a_path}\n")
            self._write_compare(f"{self.t('compare_ab_b')}: {b_path}\n\n")

            if a_is_file and b_is_file:
                hash_a = self.sha256_file(a_path)
                hash_b = self.sha256_file(b_path)

                self._write_compare(f"{self.t('compare_ab_sha_a')}: {hash_a}\n")
                self._write_compare(f"{self.t('compare_ab_sha_b')}: {hash_b}\n\n")

                if hash_a == hash_b:
                    self._write_compare(f"{self.t('compare_ab_judgement')}: {self.t('compare_ab_match')}\n")
                    self._set_status(self.t("status_ab_match"))
                else:
                    self._write_compare(f"{self.t('compare_ab_judgement')}: {self.t('compare_ab_no_match')}\n")
                    self._set_status(self.t("status_ab_no_match"))
                return

            if a_is_dir and b_is_dir:
                map_a = self.build_folder_map(a_path)
                map_b = self.build_folder_map(b_path)

                added = sorted(set(map_b) - set(map_a))
                removed = sorted(set(map_a) - set(map_b))
                common = sorted(set(map_a) & set(map_b))
                changed = [p for p in common if map_a[p].sha256 != map_b[p].sha256]
                unchanged = [p for p in common if map_a[p].sha256 == map_b[p].sha256]

                self._write_compare(f"{self.t('compare_ab_folder_summary')}\n")
                self._write_compare(f"{self.t('compare_added')}: {len(added)}\n")
                self._write_compare(f"{self.t('compare_removed')}: {len(removed)}\n")
                self._write_compare(f"{self.t('compare_changed')}: {len(changed)}\n")
                self._write_compare(f"{self.t('compare_unchanged')}: {len(unchanged)}\n\n")

                if added:
                    self._write_compare(f"{self.t('compare_added_title')}\n")
                    for p in added:
                        self._write_compare(f"+ {p}\n")
                    self._write_compare("\n")

                if removed:
                    self._write_compare(f"{self.t('compare_removed_title')}\n")
                    for p in removed:
                        self._write_compare(f"- {p}\n")
                    self._write_compare("\n")

                if changed:
                    self._write_compare(f"{self.t('compare_changed_title')}\n")
                    for p in changed:
                        self._write_compare(f"* {p}\n")
                        self._write_compare(f"  OLD: {map_a[p].sha256}\n")
                        self._write_compare(f"  NEW: {map_b[p].sha256}\n")
                    self._write_compare("\n")

                if not added and not removed and not changed:
                    self._write_compare(f"{self.t('compare_no_diff')}\n")
                    self._set_status(self.t("status_ab_match"))
                else:
                    self._set_status(self.t("status_ab_no_match"))

        except Exception as e:
            messagebox.showerror(
                self.t("msg_compare_error_title"),
                self.t("msg_ab_compare_error").format(error=e),
            )

    def compare_with_csv(self) -> None:
        """
        以前保存したCSVと現在結果を比較
        """
        if not self.current_records:
            messagebox.showinfo(self.t("msg_compare_title"), self.t("msg_no_current_for_compare"))
            return

        csv_path = filedialog.askopenfilename(
            title=self.t("open_compare_csv_title"),
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not csv_path:
            return

        try:
            old_version_name, old_map = self.load_csv_records(csv_path)
            new_map = {r.relative_path: r for r in self.current_records}

            added = sorted(set(new_map) - set(old_map))
            removed = sorted(set(old_map) - set(new_map))
            common = sorted(set(new_map) & set(old_map))
            changed = [p for p in common if new_map[p].sha256 != old_map[p].sha256]
            unchanged = [p for p in common if new_map[p].sha256 == old_map[p].sha256]

            self.compare_text.delete("1.0", tk.END)
            self._write_compare(f"{self.t('compare_csv_source')}: {csv_path}\n")
            self._write_compare(f"{self.t('compare_old_version')}: {old_version_name}\n")
            self._write_compare(
                f"{self.t('compare_new_version')}: {self.version_name_var.get().strip() or self.t('not_entered')}\n\n"
            )

            self._write_compare(f"{self.t('compare_summary')}\n")
            self._write_compare(f"{self.t('compare_added')}: {len(added)}\n")
            self._write_compare(f"{self.t('compare_removed')}: {len(removed)}\n")
            self._write_compare(f"{self.t('compare_changed')}: {len(changed)}\n")
            self._write_compare(f"{self.t('compare_unchanged')}: {len(unchanged)}\n\n")

            if added:
                self._write_compare(f"{self.t('compare_added_title')}\n")
                for p in added:
                    self._write_compare(f"+ {p}\n")
                self._write_compare("\n")

            if removed:
                self._write_compare(f"{self.t('compare_removed_title')}\n")
                for p in removed:
                    self._write_compare(f"- {p}\n")
                self._write_compare("\n")

            if changed:
                self._write_compare(f"{self.t('compare_changed_title')}\n")
                for p in changed:
                    self._write_compare(f"* {p}\n")
                    self._write_compare(f"  OLD: {old_map[p].sha256}\n")
                    self._write_compare(f"  NEW: {new_map[p].sha256}\n")
                self._write_compare("\n")

            if not added and not removed and not changed:
                self._write_compare(f"{self.t('compare_no_diff')}\n")

            self._set_status(self.t("status_compare_done"))

        except Exception as e:
            messagebox.showerror(
                self.t("msg_compare_error_title"),
                self.t("msg_compare_error").format(error=e),
            )

    def generate_release_hash(self) -> None:
        """
        Release 用のハッシュ一覧を生成
        """
        if not self.release_file_paths:
            messagebox.showwarning(self.t("msg_input_warning_title"), self.t("msg_need_release_files"))
            return

        version_name = self.version_name_var.get().strip()
        if not version_name:
            messagebox.showwarning(self.t("msg_input_warning_title"), self.t("msg_need_version"))
            return

        lines: list[str] = []
        lines.append(self.t("release_output_title"))
        lines.append(f"{self.t('release_version')}: {version_name}")
        lines.append(f"{self.t('release_file_count')}: {len(self.release_file_paths)}")
        lines.append("")

        for path in self.release_file_paths:
            file_name = os.path.basename(path)
            sha256 = self.sha256_file(path)

            lines.append(f"{self.t('release_target_file')}: {file_name}")
            lines.append(f"{self.t('release_sha256')}: {sha256}")
            lines.append("")

        output = "\n".join(lines).strip()

        self.release_output_var.set(output)
        self.release_output_text.delete("1.0", tk.END)
        self.release_output_text.insert(tk.END, output)

        self._set_status(self.t("status_release_generated"))
        messagebox.showinfo(self.t("msg_release_title"), self.t("msg_release_generated"))

    def load_csv_records(self, csv_path: str) -> tuple[str, dict[str, HashRecord]]:
        """
        CSVを読み込んで比較用データへ変換
        """
        result: dict[str, HashRecord] = {}
        version_name = self.t("unknown")

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                version_name = row.get("version_name", version_name)
                relative_path = row["relative_path"]
                result[relative_path] = HashRecord(
                    relative_path=relative_path,
                    full_path=row.get("full_path", ""),
                    file_size=int(row.get("file_size", 0) or 0),
                    last_modified=row.get("last_modified", ""),
                    sha256=row.get("sha256", ""),
                )

        return version_name, result


def create_root() -> tk.Tk:
    """
    tkinterdnd2 があれば DnD対応の root を作る
    """
    if DND_AVAILABLE and TkinterDnD is not None:
        return TkinterDnD.Tk()
    return tk.Tk()


def main() -> None:
    root = create_root()
    app = HashViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()