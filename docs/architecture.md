# アーキテクチャ解説

## 設計思想

このテンプレートの最優先事項は「**チームメンバーのスキル差を吸収し、学習コストとメンテナンスの難易度を下げること**」です。

Python の設計指針（PEP 20）には次のような言葉があります。

> *実装を説明するのが難しいなら、それは悪いアイデアだ。*  
> *実装を説明するのが簡単なら、それはいいアイデアかもしれない。*

この考えに基づき、以下を**意図的に採用しない**設計にしています。

- 自作のデータバインディング機構
- Observer パターン / イベントバス
- 複雑なリアクティブフレームワーク

代わりに、Python 標準ライブラリの `threading` と `queue` のみで非同期処理を実現しています。

---

## MVPパターンの役割分担

### Model（`model/` 以下）

**ビジネスロジックのみ**を記述します。

```python
# ✅ Model がやること
class DataProcessor:
    def run(self, input_file, output_dir, param, config, result_queue):
        # ファイルI/O、データ変換、計算など
        result_queue.put({"type": "progress", "value": 0.5})
        result_queue.put({"type": "done", "result": "..."})

# ❌ Model がやってはいけないこと
import customtkinter  # UIライブラリを一切 import しない
```

Model は `queue.Queue` にメッセージを `put` することだけが外部への通信手段です。  
これにより、**GUIなしで単体テストが書ける**状態を維持します。

### View（`views/` 以下）

**CustomTkinter によるUI構築のみ**を担います。「Passive View」とも呼ばれます。

```python
# ✅ View がやること（UIの構築と Setter/Getter のみ）
class MainView(ctk.CTkFrame):
    def set_status(self, text, color="gray"):
        self.status_label.configure(text=text, text_color=color)

    def get_input_path(self) -> str:
        return self.input_entry.get()

# ❌ View がやってはいけないこと
def on_run_clicked(self):
    if not self.input_entry.get():  # バリデーションは Presenter の仕事
        return
    self._process()  # 処理ロジックは Model の仕事
```

View は「状態を表示する」と「ユーザー操作を Presenter に伝える」だけです。  
自分で判断を下しません。

### Presenter（`presenters/` 以下）

**View と Model の橋渡し**と、**処理の進行管理（指揮）**を担います。

```python
class MainPresenter:
    def __init__(self, view, model, config_store, navigate, on_result_added):
        # View のコールバックを自身のメソッドに紐付ける
        self._view.set_run_button_callback(self._on_run_clicked)

    def _on_run_clicked(self):
        # 1. View から入力値を取得
        input_file = self._view.get_input_path()
        # 2. バリデーション
        if not input_file:
            self._view.set_status("⚠ ...", color="orange")
            return
        # 3. Model を別スレッドで起動
        threading.Thread(target=self._model.run, ...).start()
        # 4. ポーリング開始
        self._view.after(100, self._poll_queue)
```

---

## 非同期処理の仕組み

GUIアプリで「重い処理」を実行するとウィンドウがフリーズします。  
このテンプレートでは **3つの標準機能** だけでこれを解決しています。

```
threading.Thread  →  別スレッドで処理を実行
queue.Queue       →  スレッド間で安全にデータを受け渡す
tkinter.after()   →  メインスレッドで定期的にキューを確認する
```

### なぜ `after()` でポーリングするのか？

Tkinter（CustomTkinterの基盤）は**シングルスレッドのUIフレームワーク**です。  
ワーカースレッドから直接 `label.configure(...)` を呼ぶと、競合状態によりクラッシュや描画崩れが起きます。

`after()` を使うことで「UIの更新は必ずメインスレッドで行う」ことが保証されます。

```python
def _poll_queue(self):
    try:
        while True:
            message = self._queue.get_nowait()  # キューにあるだけ処理
            self._handle_message(message)
    except queue.Empty:
        pass

    if self._is_processing:
        self._view.after(100, self._poll_queue)  # 100ms後に自分を再スケジュール
```

---

## 画面間連携の設計

### ナビゲーション（UIの操作）

サイドバーボタンによる画面切り替えは **純粋なUI操作**なので、`AppWindow` が内部で完結させています。

```python
# app_window.py
btn.configure(command=lambda n=name: self.show_screen(n))
```

### ロジック起因の遷移（Presenterから）

「変換完了後に結果画面へ遷移」のように、ビジネスロジックの結果として画面遷移が必要な場合は、`navigate` コールバックを **Dependency Injection（依存性の注入）** で Presenter に渡します。

```python
# main.py
_main_presenter = MainPresenter(
    navigate=app_window.show_screen,  # ← コールバックとして渡す
    ...
)

# main_presenter.py（Presenterはコールバックを呼ぶだけ）
self._navigate("result")  # AppWindow のことを直接知らない
```

### Presenter 間のデータ連携

Presenter 同士は**直接参照しません**。コールバックを DI することで疎結合を維持します。

```python
# main.py
result_presenter = ResultPresenter(view=result_view)

_main_presenter = MainPresenter(
    on_result_added=result_presenter.add_result,  # ← コールバックとして渡す
    ...
)
```

---

## 設計ルール（変えてはいけないこと）

| ルール | 違反した場合のリスク |
|---|---|
| Model に `tkinter` / `customtkinter` を import しない | テスト不能になる、GUI依存が全体に伝染する |
| View にロジックを書かない | テストしにくくなる、Presenterとの責務が混在する |
| Presenter 同士を直接参照しない | 画面追加・削除のたびに他の Presenter を修正する必要が生じる |
| スレッドから UI を直接更新しない | クラッシュ・描画崩れの原因になる |
| スレッド間通信は `queue` のみ | 共有変数によるデータ競合が起きる |
