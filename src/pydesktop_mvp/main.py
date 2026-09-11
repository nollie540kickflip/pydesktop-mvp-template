"""エントリーポイント: 依存関係の注入とアプリケーションの起動を行う.

このファイルの責務は以下の2点のみ:
1. 各レイヤー (View / Model / Presenter) のインスタンスを生成する。
2. Presenterに ViewとModelを注入して接続し、アプリを起動する。

アプリの処理フロー:
    main()
    └─ AppView        (CTk ウィンドウを生成)
    └─ DataProcessor  (Modelを生成)
    └─ AppPresenter   (ViewとModelを注入・接続)
    └─ view.mainloop() (Tkinter イベントループ開始)
"""
from __future__ import annotations

from pydesktop_mvp.model import DataProcessor
from pydesktop_mvp.presenter import AppPresenter
from pydesktop_mvp.view import AppView


def main() -> None:
    """アプリケーションのエントリーポイント."""
    # 各レイヤーのインスタンスを生成
    view = AppView()
    model = DataProcessor()

    # PresenterにViewとModelを注入して接続する (Dependency Injection)
    # _presenter はローカル変数だが、Viewのコールバック経由で参照が保持されるため
    # GCに回収される心配はない
    _presenter = AppPresenter(view=view, model=model)

    # Tkinterのメインイベントループを開始する
    view.mainloop()


if __name__ == "__main__":
    main()
