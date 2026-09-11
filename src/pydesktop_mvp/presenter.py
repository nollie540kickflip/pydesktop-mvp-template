"""Presenter層: ViewとModelの橋渡しと処理の指揮を担う.

- Viewからのユーザー操作を受け取り、Modelに処理を依頼する。
- Modelの非同期処理結果 (queue) をポーリングし、Viewを更新する。
- スレッドの生成や after() によるポーリングの起動もここで行う。
"""
from __future__ import annotations

import queue
import threading
from tkinter import filedialog

from .model import DataProcessor
from .view import AppView

# キューのポーリング間隔 (ミリ秒)
# 小さすぎるとCPUを浪費し、大きすぎるとUIの応答が遅くなる
_POLL_INTERVAL_MS = 100


class AppPresenter:
    """アプリケーションのPresenter.

    ViewとModelのインスタンスを保持し、
    Viewのコールバックを自身のメソッドに紐付けることで制御の中心となる。
    """

    def __init__(self, view: AppView, model: DataProcessor) -> None:
        self._view = view
        self._model = model
        self._queue: queue.Queue = queue.Queue()
        self._is_processing = False

        # Viewのコールバックを自身のハンドラメソッドに接続する (依存関係の解決)
        self._view.set_run_button_callback(self._on_run_clicked)
        self._view.set_input_browse_callback(self._on_input_browse)
        self._view.set_output_browse_callback(self._on_output_browse)

    # ------------------------------------------------------------------
    # Viewからのイベントハンドラ
    # ------------------------------------------------------------------

    def _on_input_browse(self) -> None:
        """入力ファイルの参照ボタンが押されたときの処理."""
        path = filedialog.askopenfilename(
            title="入力ファイルを選択",
            filetypes=[("すべてのファイル", "*.*")],
        )
        if path:
            self._view.set_input_path(path)

    def _on_output_browse(self) -> None:
        """出力先の参照ボタンが押されたときの処理."""
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if path:
            self._view.set_output_path(path)

    def _on_run_clicked(self) -> None:
        """実行ボタンが押されたときの処理.

        入力値を検証し、問題なければModelを別スレッドで起動して
        キューのポーリングを開始する。
        """
        input_file = self._view.get_input_path()
        output_dir = self._view.get_output_path()
        param = self._view.get_param()

        # 入力値の検証
        if not input_file or not output_dir:
            self._view.set_status(
                "⚠ 入力ファイルと出力先を指定してください。", color="orange"
            )
            return

        # UIを処理中状態に遷移させる
        self._is_processing = True
        self._view.set_run_button_state(enabled=False)
        self._view.set_progress(0.0)
        self._view.set_status("処理中...", color="dodger blue")

        # Modelを別スレッドで起動する
        # daemon=True により、メインウィンドウを閉じたときにスレッドも終了する
        thread = threading.Thread(
            target=self._model.run,
            args=(input_file, output_dir, param, self._queue),
            daemon=True,
        )
        thread.start()

        # after() でキューのポーリングを開始する
        # after() はメインスレッドで実行されるため、UIの安全な更新が保証される
        self._view.after(_POLL_INTERVAL_MS, self._poll_queue)

    # ------------------------------------------------------------------
    # キューのポーリング (after() によりメインスレッドで定期実行される)
    # ------------------------------------------------------------------

    def _poll_queue(self) -> None:
        """キューを確認し、受信した全メッセージを処理する.

        処理が継続中であれば、after() で自身を再スケジュールし
        次のポーリングタイミングまで待機する。
        """
        try:
            # キューが空になるまで、溜まっているメッセージをすべて処理する
            while True:
                message = self._queue.get_nowait()
                self._handle_message(message)
        except queue.Empty:
            pass

        # 処理中であれば、次のポーリングを予約する
        if self._is_processing:
            self._view.after(_POLL_INTERVAL_MS, self._poll_queue)

    def _handle_message(self, message: dict) -> None:
        """キューから受信した1件のメッセージを処理し、Viewを更新する."""
        msg_type = message.get("type")

        if msg_type == "progress":
            value: float = message["value"]
            self._view.set_progress(value)

        elif msg_type == "done":
            result: str = message["result"]
            self._is_processing = False
            self._view.set_progress(1.0)
            self._view.set_status(f"✓ 完了: {result}", color="green")
            self._view.set_run_button_state(enabled=True)

        elif msg_type == "error":
            error_msg: str = message["message"]
            self._is_processing = False
            self._view.set_status(f"✗ エラー: {error_msg}", color="red")
            self._view.set_run_button_state(enabled=True)
