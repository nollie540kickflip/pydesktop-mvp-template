"""View層: CustomTkinterによるUI構築のみを担う (Passive View).

自己判断能力を持たず、ユーザー操作はすべて Presenter のコールバックに委譲する。
Presenterから呼ばれるアップデートメソッドのみが、UIの状態を変更する唯一の入口。
"""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk


class AppView(ctk.CTk):
    """アプリケーションのメインウィンドウ (Passive View).

    UIウィジェットの構築と、Presenterへのコールバック登録のみを行う。
    ボタンが押されたらPresenterに通知するだけで、自身では何も判断しない。
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("pydesktop-mvp")
        self.geometry("640x320")
        self.resizable(False, False)

        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self._build_widgets()

    # ------------------------------------------------------------------
    # ウィジェット構築 (内部メソッド)
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        """全ウィジェットを構築してグリッドに配置する."""
        # 中央カラムを伸縮させる
        self.grid_columnconfigure(1, weight=1)

        PAD_X_OUTER = (20, 6)
        PAD_X_MID = 6
        PAD_X_RIGHT = (6, 20)
        PAD_Y = 8

        # ── 入力ファイル ────────────────────────────────────────────
        ctk.CTkLabel(self, text="入力ファイル:").grid(
            row=0, column=0, padx=PAD_X_OUTER, pady=(24, PAD_Y), sticky="e"
        )
        self.input_entry = ctk.CTkEntry(
            self, placeholder_text="ファイルを選択してください..."
        )
        self.input_entry.grid(
            row=0, column=1, padx=PAD_X_MID, pady=(24, PAD_Y), sticky="ew"
        )
        self.input_browse_btn = ctk.CTkButton(self, text="参照", width=64)
        self.input_browse_btn.grid(
            row=0, column=2, padx=PAD_X_RIGHT, pady=(24, PAD_Y)
        )

        # ── 出力先 ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="出力先:").grid(
            row=1, column=0, padx=PAD_X_OUTER, pady=PAD_Y, sticky="e"
        )
        self.output_entry = ctk.CTkEntry(
            self, placeholder_text="保存先フォルダを選択してください..."
        )
        self.output_entry.grid(
            row=1, column=1, padx=PAD_X_MID, pady=PAD_Y, sticky="ew"
        )
        self.output_browse_btn = ctk.CTkButton(self, text="参照", width=64)
        self.output_browse_btn.grid(
            row=1, column=2, padx=PAD_X_RIGHT, pady=PAD_Y
        )

        # ── パラメータ ────────────────────────────────────────────
        ctk.CTkLabel(self, text="パラメータ:").grid(
            row=2, column=0, padx=PAD_X_OUTER, pady=PAD_Y, sticky="e"
        )
        self.param_entry = ctk.CTkEntry(
            self, placeholder_text="例: --quality 80"
        )
        self.param_entry.grid(
            row=2, column=1, columnspan=2, padx=(PAD_X_MID, 20),
            pady=PAD_Y, sticky="ew"
        )

        # ── 実行ボタン ────────────────────────────────────────────
        self.run_btn = ctk.CTkButton(self, text="実行", height=36)
        self.run_btn.grid(
            row=3, column=0, columnspan=3,
            padx=20, pady=(16, PAD_Y), sticky="ew"
        )

        # ── プログレスバー ──────────────────────────────────────
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.set(0)
        self.progress_bar.grid(
            row=4, column=0, columnspan=3,
            padx=20, pady=PAD_Y, sticky="ew"
        )

        # ── ステータスラベル ────────────────────────────────────
        self.status_label = ctk.CTkLabel(
            self, text="待機中...", text_color="gray"
        )
        self.status_label.grid(
            row=5, column=0, columnspan=3,
            padx=20, pady=(4, 20)
        )

    # ------------------------------------------------------------------
    # Presenter からのコールバック登録メソッド
    # ------------------------------------------------------------------

    def set_run_button_callback(self, callback: Callable[[], None]) -> None:
        """実行ボタン押下時のコールバックを設定する."""
        self.run_btn.configure(command=callback)

    def set_input_browse_callback(self, callback: Callable[[], None]) -> None:
        """入力ファイルの参照ボタン押下時のコールバックを設定する."""
        self.input_browse_btn.configure(command=callback)

    def set_output_browse_callback(self, callback: Callable[[], None]) -> None:
        """出力先の参照ボタン押下時のコールバックを設定する."""
        self.output_browse_btn.configure(command=callback)

    # ------------------------------------------------------------------
    # Presenter からのデータ取得メソッド (Getter)
    # ------------------------------------------------------------------

    def get_input_path(self) -> str:
        """入力ファイルパスを返す."""
        return self.input_entry.get()

    def get_output_path(self) -> str:
        """出力先パスを返す."""
        return self.output_entry.get()

    def get_param(self) -> str:
        """パラメータ文字列を返す."""
        return self.param_entry.get()

    # ------------------------------------------------------------------
    # Presenter からのUI更新メソッド (Setter / Updater)
    # ------------------------------------------------------------------

    def set_input_path(self, path: str) -> None:
        """入力ファイルパスの入力欄を更新する."""
        self.input_entry.delete(0, "end")
        self.input_entry.insert(0, path)

    def set_output_path(self, path: str) -> None:
        """出力先パスの入力欄を更新する."""
        self.output_entry.delete(0, "end")
        self.output_entry.insert(0, path)

    def set_run_button_state(self, *, enabled: bool) -> None:
        """実行ボタンの活性・非活性を切り替える."""
        self.run_btn.configure(state="normal" if enabled else "disabled")

    def set_progress(self, value: float) -> None:
        """プログレスバーの値を更新する (0.0 〜 1.0)."""
        self.progress_bar.set(value)

    def set_status(self, text: str, color: str = "gray") -> None:
        """ステータスラベルのテキストと文字色を更新する."""
        self.status_label.configure(text=text, text_color=color)
