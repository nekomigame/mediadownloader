import sys
import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess

class DownloaderApp(tk.Tk):
    """
    gallery-dlのGUIラッパーアプリケーション
    """
    def __init__(self):
        super().__init__()
        self.title("X Media Downloader")
        self.geometry("600x450")
        self.create_widgets()

    def create_widgets(self):
        # --- UIフレームの作成 ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        main_frame.grid_columnconfigure(1, weight=1)

        # --- ウィジェットの作成 ---
        # ユーザーID
        ttk.Label(main_frame, text="ユーザーID (@不要):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.username_var = tk.StringVar(value="nasa")
        ttk.Entry(main_frame, textvariable=self.username_var).grid(row=0, column=1, sticky=tk.EW, pady=2)

        # Cookieファイル
        ttk.Label(main_frame, text="Cookieファイル:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cookie_path_var = tk.StringVar(value=os.path.abspath('cookies.txt'))
        cookie_frame = ttk.Frame(main_frame)
        cookie_frame.grid(row=1, column=1, sticky=tk.EW, pady=2)
        cookie_frame.columnconfigure(0, weight=1)
        ttk.Entry(cookie_frame, textvariable=self.cookie_path_var, state='readonly').grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(cookie_frame, text="選択...", command=self.select_cookie_file).grid(row=0, column=1, padx=(5, 0))

        # 保存先フォルダ
        ttk.Label(main_frame, text="保存先フォルダ:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.output_dir_var = tk.StringVar(value=os.path.abspath('./downloads'))
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, sticky=tk.EW, pady=2)
        output_frame.columnconfigure(0, weight=1)
        ttk.Entry(output_frame, textvariable=self.output_dir_var, state='readonly').grid(row=0, column=0, sticky=tk.EW)
        ttk.Button(output_frame, text="選択...", command=self.select_output_directory).grid(row=0, column=1, padx=(5, 0))

        # 待機時間
        ttk.Label(main_frame, text="ファイル間待機 (秒):").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.sleep_var = tk.IntVar(value=1)
        ttk.Spinbox(main_frame, from_=0, to=60, textvariable=self.sleep_var, width=5).grid(row=3, column=1, sticky=tk.W, pady=2)

        # ダウンロードボタン
        self.download_button = ttk.Button(main_frame, text="ダウンロード開始", command=self.start_download_thread)
        self.download_button.grid(row=5, column=0, columnspan=2, pady=10)

        # ログ表示エリア
        log_frame = ttk.LabelFrame(main_frame, text="ログ")
        log_frame.grid(row=6, column=0, columnspan=2, sticky=tk.NSEW, pady=5)
        log_frame.rowconfigure(0, weight=1)
        log_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = tk.Text(log_frame, height=10, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=tk.NSEW)
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.grid(row=0, column=1, sticky=tk.NS)
        self.log_text['yscrollcommand'] = scrollbar.set

    def select_cookie_file(self):
        path = filedialog.askopenfilename(title="cookies.txtを選択", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            self.cookie_path_var.set(os.path.abspath(path))

    def select_output_directory(self):
        path = filedialog.askdirectory(title="保存先フォルダを選択")
        if path:
            self.output_dir_var.set(os.path.abspath(path))

    def log_message(self, message):
        """スレッドセーフにログエリアにメッセージを追記する"""
        self.log_text.configure(state='normal')
        self.log_text.insert(tk.END, message)
        self.log_text.see(tk.END)
        self.log_text.configure(state='disabled')
    
    def start_download_thread(self):
        """ダウンロード処理を別スレッドで開始する"""
        if not self.username_var.get().strip():
            messagebox.showerror("エラー", "ユーザーIDを入力してください。")
            return
        if not os.path.exists(self.cookie_path_var.get()):
            messagebox.showerror("エラー", f"Cookieファイルが見つかりません:\n{self.cookie_path_var.get()}")
            return
            
        self.download_button.config(state='disabled', text="ダウンロード中...")
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
        
        thread = threading.Thread(target=self.run_download)
        thread.daemon = True
        thread.start()

    def enable_download_button(self):
        """ダウンロードボタンを有効化する (メインスレッドで呼び出す)"""
        self.download_button.config(state='normal', text="ダウンロード開始")

    def show_error_message(self, error_message):
        """エラーメッセージボックスを表示する (メインスレッドで呼び出す)"""
        messagebox.showerror("実行エラー", f"ダウンロード中にエラーが発生しました:\n{error_message}")
        
    def run_download(self):
        """gallery-dlを別プロセスとして実行する"""
        try:
            target_username = self.username_var.get().strip()
            cookie_path = self.cookie_path_var.get()
            output_dir_base = self.output_dir_var.get()
            sleep_seconds = self.sleep_var.get()
            
            output_directory = os.path.join(output_dir_base, target_username)
            os.makedirs(output_directory, exist_ok=True)
            
            url = f"https://twitter.com/{target_username}"

            self.after(0, self.log_message, f"対象: {url}\n")
            self.after(0, self.log_message, f"保存先: {output_directory}\n")
            self.after(0, self.log_message, "-" * 20 + "\n")

            # サブプロセスで実行するコマンドを構築
            command = [
                sys.executable, "-m", "gallery_dl",
                '--directory', output_directory,
                '--cookies', cookie_path,
            ]
            if sleep_seconds > 0:
                command.extend(['--sleep', str(sleep_seconds)])
            command.append(url)

            # Windowsでコンソールが一瞬表示されるのを防ぐ
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                startupinfo=startupinfo
            )

            # 出力をリアルタイムで読み取り、GUIのログに表示
            for line in iter(process.stdout.readline, ''):
                self.after(0, self.log_message, line)

            process.stdout.close()
            return_code = process.wait()

            # 終了コードに応じてメッセージを表示
            if return_code == 0:
                self.after(0, self.log_message, "\n" + "-" * 20 + "\n")
                self.after(0, self.log_message, "ダウンロードが完了しました。\n")
            else:
                error_msg = f"ダウンロードプロセスがエラーコード {return_code} で終了しました。\n"
                self.after(0, self.log_message, "\n" + "-" * 20 + "\n")
                self.after(0, self.log_message, error_msg)
                self.after(0, self.show_error_message, error_msg.strip())

        except Exception as e:
            self.after(0, self.log_message, f"\nプロセス開始エラー: {e}\n")
            self.after(0, self.show_error_message, e)
        finally:
            self.after(0, self.enable_download_button)

if __name__ == "__main__":
    app = DownloaderApp()
    app.mainloop()

