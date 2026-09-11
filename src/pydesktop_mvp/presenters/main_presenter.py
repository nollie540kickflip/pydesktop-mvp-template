"""メイン画面のPresenter.

- Viewからのユーザー操作を受け取り、Modelに処理を依頼する。
- Modelの非同期処理結果 (queue) をポーリングし、Viewを更新する。
- 処理完了後に on_result_added コールバックで ResultPresenter に通知し、
  navigate コールバックで結果画面に自動遷移する。
"""

from __future__ import annotations

import queue
import threading
from collections.abc import Callable
from tkinter import filedialog

from pydesktop_mvp.model.config_store import ConfigStore
from pydesktop_mvp.model.processor import DataProcessor
from pydesktop_mvp.views.main_view import MainView

_POLL_INTERVAL_MS = 100


class MainPresenter:
    """メイン画面のPresenter."""

    def __init__(
        self,
        view: MainView,
        model: DataProcessor,
        config_store: ConfigStore,
        navigate: Callable[[str], None],
        on_result_added: Callable[[str, str], None],
    ) -> None:
        """
        Args:
            view: メイン画面のView
            model: データ変換Model
            config_store: 設定の読み込みに使用する
            navigate: 画面遷移コールバック。navigate("result") のように呼ぶ
            on_result_added: 結果追加コールバック。(text, color) を受け取る
        """
        self._view = view
        self._model = model
        self._config_store = config_store
        self._navigate = navigate
        self._on_result_added = on_result_added
        self._queue: queue.Queue = queue.Queue()
        self._is_processing = False

        self._view.set_run_button_callback(self._on_run_clicked)
        self._view.set_input_browse_callback(self._on_input_browse)
        self._view.set_output_browse_callback(self._on_output_browse)

    # ------------------------------------------------------------------
    # Viewからのイベントハンドラ
    # ------------------------------------------------------------------

    def _on_input_browse(self) -> None:
        path = filedialog.askopenfilename(
            title="入力ファイルを選択",
            filetypes=[("すべてのファイル", "*.*")],
        )
        if path:
            self._view.set_input_path(path)

    def _on_output_browse(self) -> None:
        path = filedialog.askdirectory(title="出力先フォルダを選択")
        if path:
            self._view.set_output_path(path)

    def _on_run_clicked(self) -> None:
        """実行ボタンが押されたときの処理."""
        input_file = self._view.get_input_path()
        output_dir = self._view.get_output_path()
        param = self._view.get_param()

        if not input_file or not output_dir:
            self._view.set_status(
                "⚠ 入力ファイルと出力先を指定してください。", color="orange"
            )
            return

        # 実行のたびに最新の設定を読み込む（設定変更が即時反映される）
        config = self._config_store.load()

        self._is_processing = True
        self._view.set_run_button_state(enabled=False)
        self._view.set_progress(0.0)
        self._view.set_status("処理中...", color="dodger blue")

        thread = threading.Thread(
            target=self._model.run,
            args=(input_file, output_dir, param, config, self._queue),
            daemon=True,
        )
        thread.start()
        self._view.after(_POLL_INTERVAL_MS, self._poll_queue)

    # ------------------------------------------------------------------
    # キューのポーリング
    # ------------------------------------------------------------------

    def _poll_queue(self) -> None:
        try:
            while True:
                message = self._queue.get_nowait()
                self._handle_message(message)
        except queue.Empty:
            pass

        if self._is_processing:
            self._view.after(_POLL_INTERVAL_MS, self._poll_queue)

    def _handle_message(self, message: dict) -> None:
        msg_type = message.get("type")

        if msg_type == "progress":
            self._view.set_progress(message["value"])

        elif msg_type == "done":
            result: str = message["result"]
            self._is_processing = False
            self._view.set_progress(1.0)
            self._view.set_status(f"✓ 完了: {result}", color="green")
            self._view.set_run_button_state(enabled=True)
            # ResultPresenter に結果を通知してから結果画面へ遷移
            self._on_result_added(result, "green")
            self._navigate("result")

        elif msg_type == "error":
            error_msg: str = message["message"]
            self._is_processing = False
            self._view.set_status(f"✗ エラー: {error_msg}", color="red")
            self._view.set_run_button_state(enabled=True)
            self._on_result_added(f"エラー: {error_msg}", "red")
