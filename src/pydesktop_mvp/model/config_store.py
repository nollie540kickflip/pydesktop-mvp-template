"""設定の永続化を担うModel.

UIの存在を一切知らない。
設定値はデータクラスで表現し、JSONファイルで読み書きする。
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, fields
from pathlib import Path


@dataclass
class AppConfig:
    """アプリケーション設定のデータクラス.

    新しい設定項目を追加する場合は、ここにフィールドを追加するだけでよい。
    """

    theme: str = "system"           # "light" | "dark" | "system"
    processing_steps: int = 10      # ダミー処理のステップ数 (1〜)


class ConfigStore:
    """設定をJSONファイルで永続化するModelクラス.

    UIの存在を一切知らない。
    ファイルが存在しない・壊れている場合はデフォルト値を返す。
    """

    def __init__(self, path: Path) -> None:
        self._path = path

    def load(self) -> AppConfig:
        """設定ファイルを読み込む。存在しない/壊れている場合はデフォルトを返す."""
        if not self._path.exists():
            return AppConfig()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            # 既知のフィールドのみを取り込み、未知のキーは無視する
            known = {f.name for f in fields(AppConfig)}
            return AppConfig(**{k: v for k, v in data.items() if k in known})
        except Exception:  # noqa: BLE001
            return AppConfig()

    def save(self, config: AppConfig) -> None:
        """設定をJSONファイルに保存する."""
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(
            json.dumps(asdict(config), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
