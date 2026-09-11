"""設定画面 (Passive View).

テーマや処理パラメータを変更するUI。
Presenterが呼ぶ Setter で初期値を設定し、
ユーザーが「保存」を押したら Presenter に委譲する。
"""
from __future__ import annotations

from typing import Callable

import customtkinter as ctk


class SettingsView(ctk.CTkFrame):
    """アプリ設定の画面."""

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(1, weight=1)
        self._build_widgets()

    # ------------------------------------------------------------------
    # ウィジェット構築
    # ------------------------------------------------------------------

    def _build_widgets(self) -> None:
        PAD_Y = 12

        # タイトル
        ctk.CTkLabel(
            self, text="設定", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 16), sticky="w")

        # ── テーマ ────────────────────────────────────────────────
        ctk.CTkLabel(self, text="テーマ:").grid(
            row=1, column=0, padx=(20, 8), pady=PAD_Y, sticky="e"
        )
        self.theme_menu = ctk.CTkOptionMenu(
            self, values=["system", "light", "dark"], width=140
        )
        self.theme_menu.grid(row=1, column=1, padx=(0, 20), pady=PAD_Y, sticky="w")

        # ── 処理ステップ数 ────────────────────────────────────────
        ctk.CTkLabel(self, text="処理ステップ数:").grid(
            row=2, column=0, padx=(20, 8), pady=PAD_Y, sticky="e"
        )
        steps_frame = ctk.CTkFrame(self, fg_color="transparent")
        steps_frame.grid(row=2, column=1, padx=(0, 20), pady=PAD_Y, sticky="w")
        self.steps_entry = ctk.CTkEntry(steps_frame, width=80)
        self.steps_entry.pack(side="left")
        ctk.CTkLabel(steps_frame, text="ステップ (×0.5秒)", text_color="gray").pack(
            side="left", padx=(8, 0)
        )

        # ── 保存ボタン ────────────────────────────────────────────
        self.save_btn = ctk.CTkButton(self, text="設定を保存", width=120)
        self.save_btn.grid(
            row=3, column=0, columnspan=2, padx=20, pady=(24, 8), sticky="w"
        )

        # ── ステータスラベル ────────────────────────────────────
        self.status_label = ctk.CTkLabel(self, text="", text_color="gray")
        self.status_label.grid(
            row=4, column=0, columnspan=2, padx=20, pady=(4, 20), sticky="w"
        )

    # ------------------------------------------------------------------
    # Presenter からのコールバック登録
    # ------------------------------------------------------------------

    def set_save_callback(self, callback: Callable[[], None]) -> None:
        self.save_btn.configure(command=callback)

    # ------------------------------------------------------------------
    # Getter / Setter
    # ------------------------------------------------------------------

    def get_theme(self) -> str:
        return self.theme_menu.get()

    def get_steps(self) -> str:
        return self.steps_entry.get()

    def set_theme(self, value: str) -> None:
        self.theme_menu.set(value)

    def set_steps(self, value: int) -> None:
        self.steps_entry.delete(0, "end")
        self.steps_entry.insert(0, str(value))

    def set_status(self, text: str, color: str = "gray") -> None:
        self.status_label.configure(text=text, text_color=color)
