"""設定画面のPresenter.

設定値の読み込み・検証・保存を担う。
テーマ変更は即時反映のため customtkinter の API を直接呼ぶ。
"""
from __future__ import annotations

import customtkinter as ctk

from pydesktop_mvp.model.config_store import AppConfig, ConfigStore
from pydesktop_mvp.views.settings_view import SettingsView


class SettingsPresenter:
    """設定画面のPresenter."""

    def __init__(self, view: SettingsView, config_store: ConfigStore) -> None:
        self._view = view
        self._config_store = config_store

        self._view.set_save_callback(self._on_save_clicked)
        self._load_initial_settings()

    # ------------------------------------------------------------------
    # 初期化
    # ------------------------------------------------------------------

    def _load_initial_settings(self) -> None:
        """起動時に設定ファイルから値を読み込んでViewに反映する."""
        config = self._config_store.load()
        self._view.set_theme(config.theme)
        self._view.set_steps(config.processing_steps)

    # ------------------------------------------------------------------
    # Viewからのイベントハンドラ
    # ------------------------------------------------------------------

    def _on_save_clicked(self) -> None:
        """保存ボタンが押されたときの処理."""
        theme = self._view.get_theme()
        steps_str = self._view.get_steps()

        # 入力値の検証
        try:
            steps = int(steps_str)
            if steps <= 0:
                raise ValueError("ステップ数は1以上の整数が必要です。")
        except ValueError:
            self._view.set_status(
                "✗ ステップ数は正の整数で入力してください。", color="red"
            )
            return

        # 設定を保存
        config = AppConfig(theme=theme, processing_steps=steps)
        self._config_store.save(config)

        # テーマを即時反映
        ctk.set_appearance_mode(theme)

        self._view.set_status("✓ 設定を保存しました。", color="green")
