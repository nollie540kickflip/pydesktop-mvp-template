# 処理・データアクセスを追加する

このガイドでは Model 層の拡張パターンを説明します。  
「DBアクセス」「外部APIの呼び出し」「設定項目の追加」などのケースに対応しています。

---

## パターン 1: 処理クラスを追加する

例: SQLite データベースからデータを取得する `DatabaseReader` を追加する。

### ファイルを作成する

`src/pydesktop_mvp/model/database.py` を新規作成します。

```python
# model/database.py
from __future__ import annotations

import queue
import sqlite3
from pathlib import Path


class DatabaseReader:
    """SQLite からデータを読み込む Model クラス.

    UIの存在を一切知らない。
    処理結果は result_queue に put することで Presenter に通知する。
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def fetch_records(self, result_queue: queue.Queue) -> None:
        """レコードを取得する（別スレッドで実行される）."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                cursor = conn.execute("SELECT * FROM records")
                rows = cursor.fetchall()

            result_queue.put({"type": "done", "result": rows})

        except Exception as exc:  # noqa: BLE001
            result_queue.put({"type": "error", "message": str(exc)})
```

### main.py で生成して DI する

```python
# main.py
from pydesktop_mvp.model.database import DatabaseReader

def main() -> None:
    db = DatabaseReader(path=Path.home() / "myapp.db")

    _some_presenter = SomePresenter(
        view=some_view,
        db=db,
        ...
    )
```

---

## パターン 2: 設定項目を追加する

`AppConfig` にフィールドを追加するだけです。

### config_store.py を編集する

```python
# model/config_store.py

@dataclass
class AppConfig:
    theme: str = "system"
    processing_steps: int = 10
    output_format: str = "csv"     # ← 追加（デフォルト値を必ず設定すること）
    max_file_size_mb: int = 100    # ← 追加
```

> **注意:** フィールドには必ずデフォルト値を設定してください。  
> 設定ファイルが古いバージョンのままでも、`ConfigStore.load()` が安全に読み込めます。

### 設定画面に入力欄を追加する

`views/settings_view.py` にウィジェットを追加し、  
`presenters/settings_presenter.py` で読み書き処理を追加します。

```python
# views/settings_view.py（追加部分）
ctk.CTkLabel(self, text="出力フォーマット:").grid(...)
self.format_menu = ctk.CTkOptionMenu(self, values=["csv", "json", "tsv"])
self.format_menu.grid(...)

def get_format(self) -> str:
    return self.format_menu.get()

def set_format(self, value: str) -> None:
    self.format_menu.set(value)
```

```python
# presenters/settings_presenter.py（変更部分）
def _load_initial_settings(self) -> None:
    config = self._config_store.load()
    self._view.set_theme(config.theme)
    self._view.set_steps(config.processing_steps)
    self._view.set_format(config.output_format)   # ← 追加

def _on_save_clicked(self) -> None:
    config = AppConfig(
        theme=self._view.get_theme(),
        processing_steps=steps,
        output_format=self._view.get_format(),    # ← 追加
    )
```

---

## パターン 3: 既存の処理クラスを分割する

`processor.py` の処理が大きくなった場合、**ステップごと**に分割できます。

```
model/
├── processor.py          # DataProcessor（オーケストレーター）
├── file_reader.py        # ファイル読み込み処理
├── converter.py          # 変換処理
└── file_writer.py        # ファイル書き込み処理
```

`DataProcessor.run()` が各クラスを呼び出す形にします。

```python
# model/processor.py
from .file_reader import FileReader
from .converter import Converter
from .file_writer import FileWriter

class DataProcessor:
    def run(self, input_file, output_dir, param, config, result_queue):
        data = FileReader().read(input_file)

        result_queue.put({"type": "progress", "value": 0.33})

        converted = Converter().convert(data, param)

        result_queue.put({"type": "progress", "value": 0.66})

        FileWriter().write(converted, output_dir)

        result_queue.put({"type": "done", "result": "完了"})
```

**ルール:** 分割後も各クラスは UI を知らない状態を維持してください。

---

## チェックリスト（共通）

- [ ] 新しい Model クラスは `customtkinter` / `tkinter` を import していない
- [ ] 外部への通知は `result_queue.put(...)` のみ
- [ ] `main.py` でインスタンスを生成して Presenter に DI した
- [ ] `AppConfig` に追加したフィールドにデフォルト値を設定した
