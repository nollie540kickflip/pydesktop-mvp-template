"""Model層: ビジネスロジックのみを担う.

UIの存在を一切知らない。
処理の進捗と結果は queue.Queue を通じてのみ外部に通知する。
"""
from __future__ import annotations

import queue
import time


class DataProcessor:
    """データ変換を担うModelクラス.

    UIの存在を一切知らず、純粋なビジネスロジックのみを記述する。
    処理は別スレッドで実行されることを前提とし、
    進捗と結果を result_queue に put することで Presenter に通知する。

    キューに送信するメッセージのフォーマット:
        進捗通知: {"type": "progress", "value": float}  # 0.0 〜 1.0
        完了通知: {"type": "done",     "result": str}
        エラー通知: {"type": "error",  "message": str}
    """

    def run(
        self,
        input_file: str,
        output_dir: str,
        param: str,
        result_queue: queue.Queue,
    ) -> None:
        """ダミーのデータ変換処理（別スレッドで実行される）.

        Args:
            input_file: 入力ファイルのパス
            output_dir: 出力先ディレクトリのパス
            param: 変換パラメータ
            result_queue: 進捗と結果を通知するキュー
        """
        total_steps = 10

        try:
            for step in range(1, total_steps + 1):
                # ここに実際の重い処理を記述する（例: ファイルI/O、変換処理など）
                time.sleep(0.5)

                progress = step / total_steps
                result_queue.put({"type": "progress", "value": progress})

            # 全ステップ完了後に完了通知を送信
            result = (
                f"変換完了: '{input_file}' → '{output_dir}' "
                f"(パラメータ: {param!r})"
            )
            result_queue.put({"type": "done", "result": result})

        except Exception as exc:  # noqa: BLE001
            result_queue.put({"type": "error", "message": str(exc)})
