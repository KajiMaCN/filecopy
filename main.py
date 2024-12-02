import tkinter as tk
from tkinter import filedialog, messagebox
import shutil
import glob
import os
import threading
import queue
import time
from tkinter import ttk
import locale

class FileCopyApp:
    def __init__(self, master):
        self.master = master
        master.title("文件复制器" if self.is_chinese() else "File Copy Tool")

        self.source_folders = []
        self.destination_folder = ""
        self.extension = ".JPG"  # 默认扩展名
        self.cancelled = False   # 取消标志
        self.overwrite_all = False  # 全部覆盖标志
        self.rename_all = False     # 全部重命名标志
        self.skip_all = False       # 全部跳过标志
        self.filename_counts = {}   # 文件名计数，用于重命名

        # 设置窗口最小尺寸
        self.master.update_idletasks()
        min_width = self.master.winfo_reqwidth()
        min_height = self.master.winfo_reqheight()
        self.master.minsize(min_width, min_height)

        # 创建菜单栏，添加“帮助”菜单
        self.create_menu()

        # 源文件夹按钮
        self.add_source_button = tk.Button(master, text=self.tr("添加源文件夹"), command=self.add_source_folder)
        self.add_source_button.pack(pady=5)

        self.remove_source_button = tk.Button(master, text=self.tr("移除源文件夹"), command=self.remove_source_folder)
        self.remove_source_button.pack(pady=5)

        self.source_label = tk.Label(master, text=self.tr("已选择的源文件夹："))
        self.source_label.pack(pady=5)

        # 源文件夹列表和滚动条
        self.source_frame = tk.Frame(master)
        self.source_frame.pack(pady=5)

        self.source_scrollbar = tk.Scrollbar(self.source_frame, orient=tk.VERTICAL)
        self.source_listbox = tk.Listbox(
            self.source_frame, width=50, yscrollcommand=self.source_scrollbar.set
        )
        self.source_scrollbar.config(command=self.source_listbox.yview)
        self.source_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.source_listbox.pack(side=tk.LEFT, fill=tk.BOTH)

        # 绑定双击事件，打开源文件夹
        self.source_listbox.bind("<Double-Button-1>", self.open_source_folder)

        # 目标文件夹选择按钮
        self.destination_button = tk.Button(master, text=self.tr("选择目标文件夹"), command=self.select_destination)
        self.destination_button.pack(pady=5)

        self.destination_label = tk.Label(master, text=self.tr("未选择目标文件夹"), fg="blue", cursor="hand2")
        self.destination_label.pack(pady=5)

        # 绑定点击事件，打开目标文件夹
        self.destination_label.bind("<Button-1>", self.open_destination_folder)

        # 文件扩展名输入
        self.extension_label = tk.Label(master, text=self.tr("文件扩展名（默认 .JPG）："))
        self.extension_label.pack(pady=5)

        self.extension_entry = tk.Entry(master)
        self.extension_entry.pack(pady=5)
        self.extension_entry.insert(0, ".JPG")  # 设置默认值

        # 复制和取消按钮
        self.button_frame = tk.Frame(master)
        self.button_frame.pack(pady=10)

        self.copy_button = tk.Button(self.button_frame, text=self.tr("复制文件"), command=self.start_copy_thread)
        self.copy_button.pack(side=tk.LEFT, padx=5)

        self.cancel_button = tk.Button(
            self.button_frame, text=self.tr("取消复制"), command=self.cancel_copy, state=tk.DISABLED
        )
        self.cancel_button.pack(side=tk.LEFT, padx=5)

        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            master, variable=self.progress_var, maximum=100
        )
        self.progress_bar.pack(pady=10, fill=tk.X, padx=20)

        # 进度标签
        self.progress_label = tk.Label(master, text=self.tr("进度：0% (0/0)"))
        self.progress_label.pack(pady=5)

        # 更新窗口最小尺寸
        self.update_min_size()

    def is_chinese(self):
        lang = locale.getdefaultlocale()[0]
        if lang and lang.startswith('zh'):
            return True
        return False

    def tr(self, text):
        # 简单的翻译函数
        translations = {
            "添加源文件夹": "Add Source Folder",
            "移除源文件夹": "Remove Source Folder",
            "已选择的源文件夹：": "Selected Source Folders:",
            "选择目标文件夹": "Select Destination Folder",
            "未选择目标文件夹": "Destination Folder Not Selected",
            "文件扩展名（默认 .JPG）：": "File Extension (default .JPG):",
            "复制文件": "Copy Files",
            "取消复制": "Cancel Copy",
            "进度：0% (0/0)": "Progress: 0% (0/0)",
            "文件复制器": "File Copy Tool",
            "帮助": "Help",
            "关于": "About",
            "警告": "Warning",
            "请选择要移除的源文件夹。": "Please select a source folder to remove.",
            "请选择至少一个源文件夹。": "Please select at least one source folder.",
            "请选择目标文件夹。": "Please select a destination folder.",
            "未找到扩展名为": "No files with extension",
            "的文件。": "were found.",
            "确认": "Confirm",
            "确定要复制扩展名为": "Are you sure you want to copy files with extension",
            "吗？": "?",
            "已完成": "Completed",
            "文件复制已完成。": "File copying has been completed.",
            "文件已存在": "File Exists",
            "文件": "File",
            "已存在，选择操作：": "already exists. Choose an action:",
            "覆盖": "Overwrite",
            "覆盖全部": "Overwrite All",
            "重命名": "Rename",
            "重命名全部": "Rename All",
            "跳过": "Skip",
            "跳过全部": "Skip All",
            "取消": "Cancel",
            "文件复制器\n版本 v1.0\n© 2024": "File Copy Tool\nVersion 1.0\n© 2024",
            "使用说明：": "Usage Instructions:",
            "版权信息：": "Copyright Information:",
            "联系方式：": "Contact Information:",
            "联系邮箱：moonlightshadowmzh@gmail.com": "Email: moonlightshadowmzh@gmail.com",
        }
        if self.is_chinese():
            return text
        else:
            return translations.get(text, text)

    def create_menu(self):
        # 创建菜单栏，添加“帮助”菜单
        self.menu_bar = tk.Menu(self.master)
        self.master.config(menu=self.menu_bar)

        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label=self.tr("帮助"), command=self.show_help)
        help_menu.add_command(label=self.tr("关于"), command=self.show_about)
        self.menu_bar.add_cascade(label=self.tr("帮助"), menu=help_menu)

    def show_help(self):
        help_text = self.tr("""使用说明：
        1. 点击“添加源文件夹”按钮添加一个或多个源文件夹。
        2. 选中源文件夹列表中的文件夹，点击“移除源文件夹”按钮移除。
        3. 点击“选择目标文件夹”按钮选择目标文件夹。
        4. 设置要复制的文件扩展名（例如：.JPG），默认为 .JPG。
        5. 点击“复制文件”按钮开始复制。
        6. 当检测到相同文件名时，选择如何处理。
        7. 点击“取消复制”按钮停止复制。
        """)

        copyright_text = self.tr("""版权信息：
        © 2024 文件复制器
        联系邮箱：moonlightshadowmzh@gmail.com
        """)

        help_window = tk.Toplevel(self.master)
        help_window.title(self.tr("帮助"))

        # Center the window
        help_window.update_idletasks()  # Ensure the window is created before calculating size
        self.center_window(help_window, 400, 300)  # Adjust the size and center the window

        help_label = tk.Label(help_window, text=help_text, justify=tk.LEFT, padx=10, pady=10)
        help_label.pack(fill=tk.BOTH, expand=True)

        copyright_label = tk.Label(help_window, text=copyright_text, justify=tk.LEFT, padx=10, pady=10)
        copyright_label.pack(fill=tk.BOTH, expand=True)

    def show_about(self):
        # 显示关于对话框
        about_text = self.tr("文件复制器\n版本 1.0\n© 2024")
        messagebox.showinfo(self.tr("关于"), about_text)

    def add_source_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected and folder_selected not in self.source_folders:
            self.source_folders.append(folder_selected)
            self.source_listbox.insert(tk.END, folder_selected)
            self.update_min_size()

    def remove_source_folder(self):
        selected_indices = self.source_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning(self.tr("警告"), self.tr("请选择要移除的源文件夹。"))
            return
        for index in reversed(selected_indices):
            folder = self.source_listbox.get(index)
            self.source_folders.remove(folder)
            self.source_listbox.delete(index)
        self.update_min_size()

    def select_destination(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.destination_folder = folder_selected
            self.destination_label.config(text=f"{self.tr('目标文件夹')}: {self.destination_folder}")
            self.update_min_size()

    def start_copy_thread(self):
        if not self.source_folders:
            messagebox.showwarning(self.tr("警告"), self.tr("请选择至少一个源文件夹。"))
            return
        if not self.destination_folder:
            messagebox.showwarning(self.tr("警告"), self.tr("请选择目标文件夹。"))
            return

        # 获取文件扩展名
        extension = self.extension_entry.get().strip()
        if not extension:
            extension = ".JPG"
        if not extension.startswith("."):
            extension = "." + extension
        self.extension = extension

        find_same_fold,hint_text=self.self_fold_check()
        if find_same_fold:
            messagebox.askyesno(self.tr("确认"), f"{hint_text}")
        if not self.source_folders:
            messagebox.askyesno(self.tr("确认"), "源文件夹为空，请重新设置")
            return

        # 弹出确认对话框
        confirm = messagebox.askyesno(self.tr("确认"),
                                      f"{self.tr('确定要复制扩展名为')} {self.extension} {self.tr('的文件吗？')}")
        if not confirm:
            return

        # 收集要复制的文件
        self.files_to_copy = []
        for folder in self.source_folders:
            # 匹配不同大小写的扩展名
            pattern1 = os.path.join(folder, f"*{self.extension}")
            pattern2 = os.path.join(folder, f"*{self.extension.lower()}")
            pattern3 = os.path.join(folder, f"*{self.extension.upper()}")
            self.files_to_copy.extend(glob.glob(pattern1))
            self.files_to_copy.extend(glob.glob(pattern2))
            self.files_to_copy.extend(glob.glob(pattern3))
        self.files_to_copy=set(self.files_to_copy)
        if not self.files_to_copy:
            messagebox.showwarning(self.tr("警告"), f"{self.tr('未找到扩展名为')} {self.extension} {self.tr('的文件。')}")
            return

        # 重置标志
        self.total_files = len(self.files_to_copy)
        self.copied_files = 0
        self.cancelled = False
        self.overwrite_all = False
        self.rename_all = False
        self.skip_all = False
        self.filename_counts = {}

        # 禁用复制按钮，启用取消按钮
        self.copy_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self.progress_var.set(0)
        self.progress_label.config(text=self.tr("进度：0% (0/{})").format(self.total_files))

        # 启动复制线程
        self.progress_queue = queue.Queue()
        copy_thread = threading.Thread(target=self.copy_files)
        copy_thread.start()
        self.master.after(100, self.update_progress)

    def copy_files(self):
        for idx, src_path in enumerate(self.files_to_copy):
            if self.cancelled:
                break

            # 确保目标文件夹存在
            if not os.path.exists(self.destination_folder):
                os.makedirs(self.destination_folder)

            filename = os.path.basename(src_path)
            dst_path = os.path.join(self.destination_folder, filename)

            # 检查目标文件是否存在
            if os.path.exists(dst_path):
                action = self.ask_user_for_action(filename)
                if action == "overwrite":
                    shutil.copy(src_path, dst_path)
                elif action == "rename":
                    new_name = self.get_new_filename(filename)
                    new_dst_path = os.path.join(self.destination_folder, new_name)
                    shutil.copy(src_path, new_dst_path)
                elif action == "skip":
                    pass  # 跳过此文件
                elif action == "cancel":
                    self.cancelled = True
                    break
                else:
                    pass  # 默认跳过
            else:
                shutil.copy(src_path, dst_path)

            # 更新进度
            self.copied_files += 1
            progress = (self.copied_files / self.total_files) * 100
            self.progress_queue.put((progress, self.copied_files, self.total_files))

            time.sleep(0.01)  # 可选的延迟

        self.progress_queue.put(None)  # 复制完成

    def update_progress(self):
        try:
            progress_data = self.progress_queue.get_nowait()
            if progress_data is None:
                # 复制完成
                self.cancel_button.config(state=tk.DISABLED)
                self.copy_button.config(state=tk.NORMAL)
                messagebox.showinfo(self.tr("已完成"), self.tr("文件复制已完成。"))
                return
            progress, current, total = progress_data
            self.progress_var.set(progress)
            self.progress_label.config(text=self.tr("进度：{:.2f}% ({}/{})").format(progress, current, total))
            self.master.after(100, self.update_progress)
        except queue.Empty:
            self.master.after(100, self.update_progress)

    def ask_user_for_action(self, filename):
        # 检查是否已选择“跳过全部”、“覆盖全部”或“重命名全部”
        if self.skip_all:
            return "skip"
        if self.overwrite_all:
            return "overwrite"
        if self.rename_all:
            return "rename"

        # 显示自定义对话框，提供选项
        action = self.show_conflict_dialog(filename)
        return action

    def show_conflict_dialog(self, filename):
        # Custom file conflict resolution dialog
        action = None
        dialog = tk.Toplevel(self.master)
        dialog.title(self.tr("文件已存在"))

        # Center the window
        dialog.update_idletasks()  # Ensure the window is created before calculating size
        self.center_window(dialog, 800, 150)  # Adjust the size and center the window

        tk.Label(dialog, text=f"{self.tr('文件')} '{filename}' {self.tr('已存在，选择操作：')}").pack(pady=10)

        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=5)

        def set_action(a):
            nonlocal action
            action = a
            dialog.destroy()

        tk.Button(button_frame, text=self.tr("覆盖"), width=12, command=lambda: set_action("overwrite")).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=self.tr("覆盖全部"), width=12, command=lambda: set_action("overwrite_all")).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=self.tr("重命名"), width=12, command=lambda: set_action("rename")).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=self.tr("重命名全部"), width=12, command=lambda: set_action("rename_all")).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=self.tr("跳过"), width=12, command=lambda: set_action("skip")).pack(side=tk.LEFT,
                                                                                                         padx=5)
        tk.Button(button_frame, text=self.tr("跳过全部"), width=12, command=lambda: set_action("skip_all")).pack(
            side=tk.LEFT, padx=5)
        tk.Button(button_frame, text=self.tr("取消"), width=12, command=lambda: set_action("cancel")).pack(side=tk.LEFT,
                                                                                                           padx=5)

        dialog.wait_window()

        # Set flags based on user's choice
        if action == "overwrite_all":
            self.overwrite_all = True
            return "overwrite"
        elif action == "rename_all":
            self.rename_all = True
            return "rename"
        elif action == "skip_all":
            self.skip_all = True
            return "skip"
        elif action == "cancel":
            self.cancelled = True
            return "cancel"
        else:
            return action

    def get_new_filename(self, filename):
        # 通过添加计数生成新文件名
        base_name, ext = os.path.splitext(filename)
        count = self.filename_counts.get(base_name, 1)
        new_filename = f"{base_name}({count}){ext}"
        self.filename_counts[base_name] = count + 1
        return new_filename

    def cancel_copy(self):
        self.cancelled = True
        self.cancel_button.config(state=tk.DISABLED)

    def open_source_folder(self, event):
        try:
            index = self.source_listbox.curselection()[0]
            folder_path = self.source_listbox.get(index)
            if os.path.exists(folder_path):
                os.startfile(folder_path)
            else:
                messagebox.showwarning(self.tr("警告"), f"{self.tr('文件夹')} '{folder_path}' {self.tr('不存在。')}")
        except IndexError:
            pass

    def open_destination_folder(self, event):
        if self.destination_folder and os.path.exists(self.destination_folder):
            os.startfile(self.destination_folder)
        else:
            messagebox.showwarning(self.tr("警告"), self.tr("目标文件夹未选择或不存在。"))

    def update_min_size(self):
        self.master.update_idletasks()
        min_width = self.master.winfo_width()
        min_height = self.master.winfo_height()
        self.master.minsize(min_width, min_height)

    def center_window(self,window, width, height):
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        position_top = int(screen_height / 2 - height / 2)
        position_right = int(screen_width / 2 - width / 2)
        window.geometry(f'{width}x{height}+{position_right}+{position_top}')

    def self_fold_check(self):
        find_same = False
        text=""
        for index,folder in enumerate(self.source_folders):
            if folder == self.destination_folder:
                self.source_folders.remove(self.destination_folder)
                self.source_listbox.delete(index)
                find_same=True
                text=f"检测到相同的源文件夹和目标文件夹:\n {self.destination_folder}\n已删除相同文件夹"
        return find_same,text


def main():
    root = tk.Tk()
    app = FileCopyApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
