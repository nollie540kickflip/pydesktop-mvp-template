# 新しい画面を追加する

このガイドでは「履歴画面」を例に、新しい画面を追加する手順を説明します。  
追加するのは **4つのファイル（+1ファイルの編集）** だけです。

---

## ステップ概要

```
1. views/history_view.py     を作成（Passive View）
2. presenters/history_presenter.py を作成
3. views/app_window.py       のサイドバー項目を追加（1行）
4. main.py                   で生成・DI・登録する
```

---

## Step 1: View を作成する

`src/pydesktop_mvp/views/history_view.py` を新規作成します。

既存の `result_view.py` などを参考に `CTkFrame` として実装します。

```python
# views/history_view.py
from __future__ import annotations
import customtkinter as ctk


class HistoryView(ctk.CTkFrame):

    def __init__(self, master: ctk.CTkFrame) -> None:
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        self._build_widgets()

    def _build_widgets(self) -> None:
        ctk.CTkLabel(
            self, text="履歴", font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=(20, 12), sticky="w")

        # ここに必要なウィジェットを追加する
        self.content_label = ctk.CTkLabel(self, text="（履歴なし）", text_color="gray")
        self.content_label.grid(row=1, column=0, padx=20, pady=8, sticky="w")

    # --- Setter（Presenter から呼ばれる） ---

    def set_content(self, text: str) -> None:
        self.content_label.configure(text=text)
```

**ルール:**
- `ctk.CTkFrame` を継承する（`ctk.CTk` ではない）
- ロジックを書かない。Setter/Getter のみを公開する

---

## Step 2: Presenter を作成する

`src/pydesktop_mvp/presenters/history_presenter.py` を新規作成します。

```python
# presenters/history_presenter.py
from __future__ import annotations

from pydesktop_mvp.views.history_view import HistoryView


class HistoryPresenter:

    def __init__(self, view: HistoryView) -> None:
        self._view = view
        # ここで View のコールバックを自身のメソッドに紐付ける
        # 例: self._view.set_some_button_callback(self._on_button_clicked)

    # --- View からのイベントハンドラ ---

    # def _on_button_clicked(self) -> None:
    #     ...
```

---

## Step 3: サイドバーに項目を追加する

`src/pydesktop_mvp/views/app_window.py` の `_NAV_ITEMS` に1行追加するだけです。

```python
# views/app_window.py

_NAV_ITEMS: list[tuple[str, str]] = [
    ("main",     "🏠  メイン"),
    ("settings", "⚙️  設定"),
    ("result",   "📋  結果一覧"),
    ("history",  "📁  履歴"),      # ← この1行を追加
]
```

---

## Step 4: main.py で組み立てる

`src/pydesktop_mvp/main.py` に以下を追記します。

```python
# main.py

# 1. import を追加
from pydesktop_mvp.views.history_view import HistoryView
from pydesktop_mvp.presenters.history_presenter import HistoryPresenter

def main() -> None:
    ...

    # 2. View を生成（content を親として渡す）
    history_view = HistoryView(master=app_window.content)

    # 3. AppWindow に登録
    app_window.register_frame("history", history_view)

    # 4. Presenter を生成して DI
    _history_presenter = HistoryPresenter(view=history_view)

    app_window.mainloop()
```

---

## 他の画面から新しい画面に連携する

他の Presenter からこの画面を操作したい場合は、コールバックで渡します。

```python
# main.py

history_presenter = HistoryPresenter(view=history_view)

_main_presenter = MainPresenter(
    ...
    on_history_updated=history_presenter.some_method,  # ← コールバックとして渡す
)
```

Presenter 同士を直接 import して参照することは**禁止**です。  
詳しくは [architecture.md](../architecture.md) の「設計ルール」を参照してください。

---

## チェックリスト

- [ ] `views/history_view.py` を作成した
- [ ] `presenters/history_presenter.py` を作成した
- [ ] `app_window.py` の `_NAV_ITEMS` に追加した
- [ ] `main.py` で View・Presenter を生成・登録した
- [ ] View にロジックを書いていない
- [ ] Presenter 同士を直接参照していない
