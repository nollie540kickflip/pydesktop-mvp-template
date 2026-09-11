# pydesktop-mvp-template

CustomTkinter と **MVP (Model-View-Presenter)** パターンを使った、Pythonデスクトップ GUI アプリのテンプレートです。

## 設計思想

チームメンバーのスキル差を吸収し、**学習コストとメンテナンスの難易度を下げる**ことを最優先としています。  
複雑な自作バインディング機構を避け、Python標準ライブラリ (`threading`, `queue`) のみで非同期処理を実現しています。

## アーキテクチャ

```
┌─────────────────────────────────────────────────────┐
│  main.py  (エントリーポイント / 依存関係の注入)          │
└─────────────────────────────────────────────────────┘
         │ インスタンスを生成して注入
         ▼
┌──────────────────┐       ┌──────────────────┐
│   View (view.py) │◄─────►│Presenter          │
│                  │       │(presenter.py)     │
│ UIの構築のみ     │       │                  │
│ Passive View     │       │ ViewとModelの橋渡し│
│ 自己判断しない   │       │ スレッド起動      │
└──────────────────┘       │ キューポーリング  │
                           └────────┬─────────┘
                                    │ run() を別スレッドで呼ぶ
                                    ▼
                           ┌──────────────────┐
                           │  Model (model.py) │
                           │                  │
                           │ ビジネスロジックのみ│
                           │ UIを一切知らない  │
                           │ queue で通知      │
                           └──────────────────┘
```

### 非同期処理のフロー

```
[メインスレッド]                  [ワーカースレッド]
      │                                  │
      │ thread.start()                   │
      ├─────────────────────────────────►│ model.run() 開始
      │                                  │
      │ after(100ms, _poll_queue)         │   progress put(queue)
      │◄─────────────────── queue ───────┤
      │ view.set_progress(value)         │   progress put(queue)
      │◄─────────────────── queue ───────┤
      │ view.set_progress(value)         │
      │   ...                            │   done put(queue)
      │◄─────────────────── queue ───────┤
      │ view.set_status("完了")           │ スレッド終了
```

## ディレクトリ構成

```
pydesktop-mvp-template/
├── .python-version       # Python バージョン固定 (3.13)
├── pyproject.toml        # プロジェクト設定・依存関係
├── README.md
└── src/
    └── pydesktop_mvp/
        ├── __init__.py
        ├── main.py       # エントリーポイント (DI とアプリ起動)
        ├── model.py      # ビジネスロジック (UIを知らない)
        ├── presenter.py  # 橋渡し役 (スレッド起動 / キューポーリング)
        └── view.py       # UI構築のみ (Passive View)
```

## セットアップ & 起動

```bash
# 依存関係のインストール
uv sync

# アプリの起動
uv run pydesktop-mvp
```

## 拡張方法

| 変更内容 | 編集するファイル |
|---|---|
| 重い処理の内容を変える | `model.py` の `DataProcessor.run()` |
| UIにウィジェットを追加する | `view.py` の `_build_widgets()` + setter/getter |
| ウィジェット追加に伴う処理を追加する | `presenter.py` のイベントハンドラ |
| アプリ起動時の初期化処理 | `main.py` の `main()` |
