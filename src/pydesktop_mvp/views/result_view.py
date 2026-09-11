"""結果一覧画面 (Passive View).

変換処理の履歴をスクロール可能なリストで表示する。
Presenter から add_result() / clear_results() を呼ばれるだけで、
自身では何も判断しない。
"""
from __future__ import annotations

import customtkinter as ctk


class ResultView(ctk.CTkFrame):
    """変換処理の結果一覧を表示する画面."""

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self._build_widgets()
        self._result_labels: list[ctk.CTkLabel] = []

    # ------------------------------------------------------------------
    # ウィジェット構築
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        # タイトル
        ctk.CTkLabel(
            self, text="結果一覧", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 8), sticky="w")

        # スクロール可能な結果リスト
        self._scroll_frame = ctk.CTkScrollableFrame(self)
        self._scroll_frame.grid(
            row=1, column=0, padx=20, pady=(0, 20), sticky="nsew"
        )
        self._scroll_frame.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Presenter からのUI更新メソッド
    # ------------------------------------------------------------------

    def add_result(self, text: str, color: str = "gray") -> None:
        """結果を1件追加する."""
        idx = len(self._result_labels)
        # 番号付きラベルで表示
        label = ctk.CTkLabel(
            self._scroll_frame,
            text=f"[{idx + 1}]  {text}",
            text_color=color,
            anchor="w",
            wraplength=540,
        )
        label.grid(row=idx, column=0, padx=8, pady=4, sticky="ew")
        self._result_labels.append(label)

    def clear_results(self) -> None:
        """結果一覧をクリアする."""
        for label in self._result_labels:
            label.destroy()
        self._result_labels.clear()
