"""ルートウィンドウ: サイドバーナビゲーションと画面切り替えを管理する.

各画面 (CTkFrame) は register_frame() で登録し、
show_screen() で表示を切り替える。
サイドバーボタンによる画面切り替えはUI上の操作なので、
Presenterを介さずここで完結させる。
"""

from __future__ import annotations

import customtkinter as ctk

# サイドバーに表示するナビゲーション項目 (screen_name, label_text)
_NAV_ITEMS: list[tuple[str, str]] = [
    ("main", "🏠  メイン"),
    ("settings", "⚙️  設定"),
    ("result", "📋  結果一覧"),
]


class AppWindow(ctk.CTk):
    """アプリのルートウィンドウ.

    左にサイドバー、右にコンテンツエリアを持つ。
    各画面フレームは content プロパティを親として生成し、
    register_frame() で登録することで管理下に置かれる。
    """

    def __init__(self) -> None:
        super().__init__()
        self.title("pydesktop-mvp")
        self.geometry("820x500")
        self.resizable(False, False)
        ctk.set_default_color_theme("blue")

        self._frames: dict[str, ctk.CTkFrame] = {}
        self._nav_buttons: dict[str, ctk.CTkButton] = {}

        self._build_layout()

    # ------------------------------------------------------------------
    # レイアウト構築
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ── サイドバー ────────────────────────────────────────────
        self._sidebar = ctk.CTkFrame(self, width=168, corner_radius=0)
        self._sidebar.grid(row=0, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.grid_rowconfigure(len(_NAV_ITEMS) + 1, weight=1)

        ctk.CTkLabel(
            self._sidebar,
            text="pydesktop\n-mvp",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, padx=16, pady=(24, 20))

        for i, (name, label) in enumerate(_NAV_ITEMS, start=1):
            btn = ctk.CTkButton(
                self._sidebar,
                text=label,
                anchor="w",
                corner_radius=6,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray80", "gray30"),
                command=lambda n=name: self.show_screen(n),
            )
            btn.grid(row=i, column=0, padx=8, pady=3, sticky="ew")
            self._nav_buttons[name] = btn

        # ── コンテンツエリア ─────────────────────────────────────
        self._content_frame = ctk.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self._content_frame.grid(row=0, column=1, sticky="nsew")
        self._content_frame.grid_rowconfigure(0, weight=1)
        self._content_frame.grid_columnconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # 公開 API
    # ------------------------------------------------------------------

    @property
    def content(self) -> ctk.CTkFrame:
        """各画面フレームの親となるコンテンツエリアを返す.

        main.py で各 View を生成するときに master として渡す。
        例: main_view = MainView(master=app_window.content)
        """
        return self._content_frame

    def register_frame(self, name: str, frame: ctk.CTkFrame) -> None:
        """画面フレームを登録する.

        登録した画面は show_screen(name) で表示できる。
        """
        self._frames[name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.grid_remove()

    def show_screen(self, name: str) -> None:
        """指定した名前の画面に切り替える.

        Presenter からロジック起因の遷移が必要な場合は、
        このメソッドを navigate コールバックとして DI する。
        """
        for frame in self._frames.values():
            frame.grid_remove()
        if name in self._frames:
            self._frames[name].grid()

        # サイドバーのアクティブ状態を更新
        for n, btn in self._nav_buttons.items():
            if n == name:
                btn.configure(
                    fg_color=("gray75", "gray25"),
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    font=ctk.CTkFont(size=13),
                )
