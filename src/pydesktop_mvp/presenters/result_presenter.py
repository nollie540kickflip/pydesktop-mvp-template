"""結果一覧画面のPresenter.

MainPresenter からのコールバックで結果を受け取り、
ResultView に表示を委譲する。
"""
from __future__ import annotations

from pydesktop_mvp.views.result_view import ResultView


class ResultPresenter:
    """結果一覧画面のPresenter."""

    def __init__(self, view: ResultView) -> None:
        self._view = view

    def add_result(self, text: str, color: str = "gray") -> None:
        """新しい結果を一覧に追加する.

        MainPresenter の on_result_added コールバックとして DI される。
        シグネチャ: (text: str, color: str) -> None
        """
        self._view.add_result(text, color)

    def clear_results(self) -> None:
        """結果一覧をクリアする."""
        self._view.clear_results()
