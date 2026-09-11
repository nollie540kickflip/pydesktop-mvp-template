"""メイン画面 (Passive View).

CustomTkinterによるUI構築のみを担う。
自己判断を持たず、ユーザー操作はすべて Presenter に委譲する。
元の view.py を CTkFrame として移植したもの。
"""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class MainView(ctk.CTkFrame):
    """データ変換処理のメイン画面.

    CTkFrame として実装することで、AppWindow のコンテンツエリアに
    差し込み可能な画面コンポーネントになっている。
    """

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self._build_widgets()

    # ------------------------------------------------------------------
    # ウィジェット構築
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        PAD_X_L = (20, 6)
        PAD_X_M = 6
        PAD_X_R = (6, 20)
        PAD_Y = 8

        # タイトル
        ctk.CTkLabel(
            self, text="データ変換", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=3, padx=20, pady=(20, 12), sticky="w")

        # ── 入力ファイル ─────────────────────────────────────────
        ctk.CTkLabel(self, text="入力ファイル:").grid(
            row=1, column=0, padx=PAD_X_L, pady=PAD_Y, sticky="e"
        )
        self.input_entry = ctk.CTkEntry(
            self, placeholder_text="ファイルを選択してください..."
        )
        self.input_entry.grid(row=1, column=1, padx=PAD_X_M, pady=PAD_Y, sticky="ew")
        self.input_browse_btn = ctk.CTkButton(self, text="参照", width=64)
        self.input_browse_btn.grid(row=1, column=2, padx=PAD_X_R, pady=PAD_Y)

        # ── 出力先 ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="出力先:").grid(
            row=2, column=0, padx=PAD_X_L, pady=PAD_Y, sticky="e"
        )
        self.output_entry = ctk.CTkEntry(
            self, placeholder_text="保存先フォルダを選択してください..."
        )
        self.output_entry.grid(row=2, column=1, padx=PAD_X_M, pady=PAD_Y, sticky="ew")
        self.output_browse_btn = ctk.CTkButton(self, text="参照", width=64)
        self.output_browse_btn.grid(row=2, column=2, padx=PAD_X_R, pady=PAD_Y)

        # ── パラメータ ────────────────────────────────────────────
        ctk.CTkLabel(self, text="パラメータ:").grid(
            row=3, column=0, padx=PAD_X_L, pady=PAD_Y, sticky="e"
        )
        self.param_entry = ctk.CTkEntry(self, placeholder_text="例: --quality 80")
        self.param_entry.grid(
            row=3, column=1, columnspan=2, padx=(PAD_X_M, 20), pady=PAD_Y, sticky="ew"
        )

        # ── 実行ボタン ────────────────────────────────────────────
        self.run_btn = ctk.CTkButton(self, text="実行", height=36)
        self.run_btn.grid(
            row=4, column=0, columnspan=3, padx=20, pady=(16, PAD_Y), sticky="ew"
        )

        # ── プログレスバー ──────────────────────────────────────
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(
            row=5, column=0, columnspan=3, padx=20, pady=PAD_Y, sticky="ew"
        )

        # ── ステータスラベル ────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="待機中...", text_color="gray")
        self.status_label.grid(row=6, column=0, columnspan=3, padx=20, pady=(4, 20))

    # ------------------------------------------------------------------
    # Presenter からのコールバック登録メソッド
    # ------------------------------------------------------------------

    def set_run_button_callback(self, callback: Callable[[], None]) -> None:
        self.run_btn.configure(command=callback)

    def set_input_browse_callback(self, callback: Callable[[], None]) -> None:
        self.input_browse_btn.configure(command=callback)

    def set_output_browse_callback(self, callback: Callable[[], None]) -> None:
        self.output_browse_btn.configure(command=callback)

    # ------------------------------------------------------------------
    # Getter / Setter
    # ------------------------------------------------------------------

    def get_input_path(self) -> str:
        return self.input_entry.get()

    def get_output_path(self) -> str:
        return self.output_entry.get()

    def get_param(self) -> str:
        return self.param_entry.get()

    def set_input_path(self, path: str) -> None:
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, path)

    def set_output_path(self, path: str) -> None:
        self.output_entry.delete(0, "end")
        self.output_entry.insert(0, path)

    def set_run_button_state(self, *, enabled: bool) -> None:
        self.run_btn.configure(state="normal" if enabled else "disabled")

    def set_progress(self, value: float) -> None:
        self.progress_bar.set(value)

    def set_status(self, text: str, color: str = "gray") -> None:
        self.status_label.configure(text=text, text_color=color)
