"""エントリーポイント: 依存関係の注入とアプリケーションの起動を行う.

このファイルの責務:
1. 設定ファイルのパスを決定する。
2. Model / View / Presenter の全インスタンスを生成する。
3. 各 Presenter に View と Model を注入して接続する。
4. 画面間の連携 (navigate / on_result_added) を DI でつなぐ。
5. mainloop() でアプリを起動する。

処理フロー:
    main()
    ├─ ConfigStore / DataProcessor (Model)
    ├─ AppWindow (ルートウィンドウ)
    │   ├─ MainView     (content に配置)
    │   ├─ SettingsView (content に配置)
    │   └─ ResultView   (content に配置)
    ├─ ResultPresenter  ─── ResultView
    ├─ SettingsPresenter ── SettingsView + ConfigStore
    ├─ MainPresenter    ─── MainView + DataProcessor + ConfigStore
    │   ├─ navigate          = app_window.show_screen  (画面遷移)
    │   └─ on_result_added   = result_presenter.add_result (結果通知)
    └─ app_window.mainloop()
"""
from __future__ import annotations

import customtkinter as ctk
from pathlib import Path

from pydesktop_mvp.model.config_store import ConfigStore
from pydesktop_mvp.model.processor import DataProcessor
from pydesktop_mvp.presenters.main_presenter import MainPresenter
from pydesktop_mvp.presenters.result_presenter import ResultPresenter
from pydesktop_mvp.presenters.settings_presenter import SettingsPresenter
from pydesktop_mvp.views.app_window import AppWindow
from pydesktop_mvp.views.main_view import MainView
from pydesktop_mvp.views.result_view import ResultView
from pydesktop_mvp.views.settings_view import SettingsView


def main() -> None:
    """アプリケーションのエントリーポイント."""

    # ── 設定ファイルのパスを決定 ──────────────────────────────────
    config_path = Path.home() / ".config" / "pydesktop-mvp" / "config.json"

    # ── Model の生成 ──────────────────────────────────────────────
    config_store = ConfigStore(path=config_path)
    processor = DataProcessor()

    # ── 保存済みテーマを起動時に適用 ──────────────────────────────
    ctk.set_appearance_mode(config_store.load().theme)

    # ── View の生成 ───────────────────────────────────────────────
    app_window = AppWindow()

    # 各画面フレームは AppWindow のコンテンツエリアを親として生成する
    main_view     = MainView(master=app_window.content)
    settings_view = SettingsView(master=app_window.content)
    result_view   = ResultView(master=app_window.content)

    # 画面を AppWindow に登録し、初期画面を表示
    app_window.register_frame("main",     main_view)
    app_window.register_frame("settings", settings_view)
    app_window.register_frame("result",   result_view)
    app_window.show_screen("main")

    # ── Presenter の生成（依存関係の注入） ────────────────────────
    result_presenter = ResultPresenter(view=result_view)

    _settings_presenter = SettingsPresenter(
        view=settings_view,
        config_store=config_store,
    )

    _main_presenter = MainPresenter(
        view=main_view,
        model=processor,
        config_store=config_store,
        # 画面遷移コールバック: Presenter が "result" などを渡して遷移を指示
        navigate=app_window.show_screen,
        # 結果通知コールバック: 変換完了時に ResultPresenter へ委譲
        on_result_added=result_presenter.add_result,
    )

    # ── アプリ起動 ─────────────────────────────────────────────────
    app_window.mainloop()


if __name__ == "__main__":
    main()
