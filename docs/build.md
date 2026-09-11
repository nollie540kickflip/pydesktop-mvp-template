# Windows 用 exe のビルド手順

PyInstaller を使ってシングルバイナリ (`.exe`) を生成します。

> **重要:** PyInstaller はクロスコンパイル非対応です。  
> macOS・Linux 上では Windows 用 `.exe` をビルドできません。  
> **GitHub Actions（推奨）** か **Windows マシン上** でビルドしてください。

---

## 方法1: GitHub Actions で自動ビルド（推奨）

GitHub にリポジトリをプッシュすることで利用できます。

### 手動実行

GitHub リポジトリの **Actions タブ** → **"Build Windows EXE"** → **"Run workflow"**

### リリースビルド（タグプッシュ）

```bash
git tag v1.0.0
git push origin v1.0.0
```

タグをプッシュすると自動的に:

1. `windows-latest` ランナーで `pyinstaller pydesktop_mvp.spec` を実行
2. `pydesktop-mvp.exe` を GitHub Actions の Artifacts に保存
3. GitHub Releases にドラフトを作成して `.exe` を添付

---

## 方法2: Windows マシンで直接ビルド

```powershell
# 1. リポジトリをクローン
git clone <repo-url>
cd pydesktop-mvp-template

# 2. uv をインストール（未インストールの場合）
# https://docs.astral.sh/uv/getting-started/installation/

# 3. dev 依存（pyinstaller）を含めてインストール
uv sync --dev

# 4. ビルド実行
uv run pyinstaller pydesktop_mvp.spec

# 5. 生成された exe を確認
# dist/pydesktop-mvp.exe
```

---

## ビルド設定 (`pydesktop_mvp.spec`)

重要な設定項目を説明します。

### CustomTkinter のデータ同梱

CustomTkinter はテーマ・フォントファイルを含むため、`datas` に明示的に追加しています。  
これを省略すると起動時にエラーが発生します。

```python
datas=[
    (ctk_path, "customtkinter"),  # テーマ・フォントデータを同梱
],
```

### コンソールウィンドウの表示制御

```python
console=False   # 本番: コンソールウィンドウを非表示（GUIアプリに必須）
console=True    # 開発時: エラーメッセージを確認したいときはこちら
```

> **注意:** `console=False` のままクラッシュすると画面に何も表示されません。  
> 不具合調査時は一時的に `console=True` に変更してビルドしてください。

### アイコンの設定

```python
# pydesktop_mvp.spec
exe = EXE(
    ...
    icon="assets/icon.ico",  # .ico ファイルのパスを指定
)
```

`.ico` ファイルは Windows の標準形式です。PNG から変換するには次のツールが使えます:
- オンライン: https://convertico.com/
- Python: `pip install pillow` → `Image.open("icon.png").save("icon.ico")`

---

## トラブルシューティング

### `ModuleNotFoundError` が起きる

`hiddenimports` に追加します。

```python
# pydesktop_mvp.spec
hiddenimports=[
    "customtkinter",
    "darkdetect",
    "your_missing_module",  # ← 追加
],
```

### exe のサイズを小さくしたい

UPX 圧縮を有効にします（デフォルト: 有効）。UPX がインストールされていない場合は自動的にスキップされます。

```bash
# UPX のインストール（Windows）
winget install upx
```

### 起動が遅い（`--onefile` の仕様）

`--onefile`（シングルバイナリ）は実行時に一時フォルダへファイルを展開するため、  
初回起動に数秒かかります。これは仕様です。

起動速度を優先したい場合は `--onedir` に変更してフォルダごと配布する方法があります。

---

## GitHub Actions ワークフローの設定

`.github/workflows/build-windows.yml` に設定済みです。

カスタマイズしたい場合の例:

```yaml
# タグに加え、main ブランチへの push 時にもビルドする
on:
  push:
    branches: [main]
    tags: ["v*"]
  workflow_dispatch:
```
