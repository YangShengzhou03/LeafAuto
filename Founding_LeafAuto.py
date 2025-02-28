import os
import sys
import threading
import heapq
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from wxauto import WeChat

"""
pyinstaller App.spec
"""


def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path).replace(os.sep, '/')


class WeChatSender:
    def __init__(self, log_callback):
        self.wx = None
        self.lock = threading.Lock()
        self.log_callback = log_callback

    def send_file(self, file_path, receiver):
        try:
            with self.lock:
                if not self.wx:
                    self.wx = WeChat()
                self.wx.SendFiles(file_path, receiver)
                return True
        except Exception as e:
            self.log_callback(f"发送文件时出现错误: {str(e)}", 'error')
            return False


class TaskManagerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("枫叶信息创始版 LeafAuto Founding")
        self.geometry("680x600")
        try:
            self.iconbitmap(get_resource_path('logo.ico'))
        except Exception:
            pass
        self.resizable(False, False)
        self.tasks = []
        self.sender = WeChatSender(self._log)
        self.running = False
        self.timers = []
        self._setup_ui()
        self._log("欢迎使用枫叶信息创始版", "success")

    def _setup_ui(self):
        main_frame = self._create_main_frame()
        input_frame = self._create_input_frame(main_frame)
        self._create_file_frame(main_frame)
        self._create_task_tree_frame(main_frame)
        self._create_button_frame(main_frame)
        self._create_log_frame(main_frame)
        self._create_copyright_frame(main_frame)
        self._create_context_menu()

    def _create_main_frame(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        main_frame.rowconfigure(2, weight=1)
        main_frame.columnconfigure(0, weight=1)
        return main_frame

    def _create_input_frame(self, main_frame):
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=0, column=0, sticky='ew')

        ttk.Label(input_frame, text="接收人:").grid(row=0, column=0, sticky='w', padx=5)
        self.recipient_entry = ttk.Entry(input_frame, width=18)
        self.recipient_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="发送时间:").grid(row=0, column=2, padx=5)
        self.time_entry = ttk.Entry(input_frame, width=20)
        self.time_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.time_entry.grid(row=0, column=3, padx=5)
        return input_frame

    def _create_file_frame(self, main_frame):
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, sticky='ew', pady=5)
        ttk.Button(file_frame, text="选择文件", command=self._select_file).grid(row=0, column=0, padx=5)
        self.file_label = ttk.Label(file_frame, text="未选择文件", foreground="blue")
        self.file_label.grid(row=0, column=1, sticky='w', padx=5)

    def _create_task_tree_frame(self, main_frame):
        tree_frame = ttk.Frame(main_frame)
        tree_frame.grid(row=2, column=0, sticky='nsew', pady=5)
        # 减少列表高度
        self.task_tree = ttk.Treeview(tree_frame, columns=('status', 'recipient', 'time', 'file'), show='headings',
                                      height=4)
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=vsb.set)
        self.task_tree.heading('status', text='状态')
        self.task_tree.heading('recipient', text='接收人')
        self.task_tree.heading('time', text='发送时间')
        self.task_tree.heading('file', text='文件')
        self.task_tree.column('status', width=80, anchor='center')
        self.task_tree.pack(side='left', fill='both', expand=True)
        vsb.pack(side='right', fill='y')

    def _create_button_frame(self, main_frame):
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=3, column=0, pady=10)
        ttk.Button(btn_frame, text="添加任务", command=self._add_task).grid(row=0, column=0, padx=5)
        self.start_btn = ttk.Button(btn_frame, text="开始执行", command=self._toggle_schedule)
        self.start_btn.grid(row=0, column=1, padx=5)

    def _create_log_frame(self, main_frame):
        log_frame = ttk.LabelFrame(main_frame, text="操作日志")
        log_frame.grid(row=4, column=0, sticky='nsew')
        # 增加日志高度
        self.log_text = tk.Text(log_frame, height=18, state='disabled')
        log_sb = ttk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        self.log_text.pack(side='left', fill='both', expand=True)
        log_sb.pack(side='right', fill='y')

        self.log_text.tag_config('success', foreground='green')
        self.log_text.tag_config('error', foreground='red')
        self.log_text.tag_config('info', foreground='black')

    def _create_copyright_frame(self, main_frame):
        copyright_frame = ttk.Frame(main_frame)
        copyright_frame.grid(row=5, column=0, pady=5, sticky='s')
        copyright_label = ttk.Label(copyright_frame, text="Copyright © 2025 LeafAuto (YangShengZhou). All rights "
                                                          "reserved.")
        copyright_label.pack()

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="删除任务", command=self._delete_selected_task)
        self.task_tree.bind("<Button-3>", self._show_context_menu)

    def _show_context_menu(self, event):
        item = self.task_tree.identify_row(event.y)
        if item:
            self.context_menu.post(event.x_root, event.y_root)

    def _delete_selected_task(self):
        selected_items = self.task_tree.selection()
        if not selected_items:
            return
        for item in selected_items:
            index = self.task_tree.index(item)
            if self.tasks[index]['status'] == '执行中':
                messagebox.showwarning("警告", "运行中的任务不可删除")
                self._log("尝试删除运行中的任务，被警告阻止", 'error')
                return
        confirm = messagebox.askyesno("确认", "确定删除选中任务？")
        if confirm:
            for item in reversed(selected_items):
                index = self.task_tree.index(item)
                del self.tasks[index]
            self._update_task_view()
            self._log("成功删除选中任务", 'info')

    def _select_file(self):
        path = filedialog.askopenfilename()
        if path:
            self.file_label.config(text=os.path.basename(path))
            self.current_file = path
            self._log(f"选择文件: {os.path.basename(path)}", 'info')

    def _add_task(self):
        recipient = self.recipient_entry.get().strip()
        if not recipient:
            messagebox.showerror("错误", "请输入有效的接收人")
            self._log("添加任务失败，未输入有效的接收人", 'error')
            return
        if not hasattr(self, 'current_file') or not os.path.exists(self.current_file):
            messagebox.showerror("错误", "请先选择有效文件")
            self._log("添加任务失败，未选择有效文件", 'error')
            return
        try:
            send_time_str = self.time_entry.get()
            task_send_time = datetime.strptime(send_time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            messagebox.showerror("错误", "时间格式应为 2025-02-28 14:26:54")
            self._log("添加任务失败，时间格式错误", 'error')
            return
        task = {
            'recipient': recipient,
            'time': task_send_time,
            'file': self.current_file,
            'status': '等待中'
        }
        self.tasks.append(task)
        self._update_task_view()
        self._log(
            f"添加任务: 接收人 {task['recipient']}, 发送时间 {task['time'].strftime('%Y-%m-%d %H:%M:%S')}, 文件 {os.path.basename(task['file'])}",
            'info')
        new_send_time = task_send_time + timedelta(minutes=30)
        new_send_time_str = new_send_time.strftime("%Y-%m-%d %H:%M:%S")
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, new_send_time_str)

    def _toggle_schedule(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._schedule_worker, daemon=True).start()
            self.start_btn.config(text="停止执行")
            self._log("开始执行任务调度", 'info')
        else:
            self.running = False
            self._cancel_timers()
            self.start_btn.config(text="开始执行")
            self._log("停止执行任务调度", 'info')

    def _schedule_worker(self):
        queue = [(task['time'], idx) for idx, task in enumerate(self.tasks)]
        heapq.heapify(queue)
        while self.running and queue:
            next_time, task_idx = heapq.heappop(queue)
            delta = (next_time - datetime.now()).total_seconds()
            if delta > 0:
                timer = threading.Timer(delta, self._execute_task, args=(task_idx,))
                self.timers.append(timer)
                timer.start()
                self.tasks[task_idx]['status'] = '执行中'
                self._update_task_view()
                self._log(f"任务 {os.path.basename(self.tasks[task_idx]['file'])} 开始等待执行，剩余时间 {delta} 秒",
                          'info')
                timer.join()
            else:
                self.tasks[task_idx]['status'] = '执行中'
                self._update_task_view()
                self._log(f"任务 {os.path.basename(self.tasks[task_idx]['file'])} 立即开始执行", 'info')
                self._execute_task(task_idx)

        all_tasks_completed = all(task['status'] in ['✓ 成功', '✗ 失败'] for task in self.tasks)
        if all_tasks_completed:
            self.running = False
            self.start_btn.config(text="开始执行")
            self._log("所有任务执行完毕", 'info')

    def _execute_task(self, task_idx):
        task = self.tasks[task_idx]
        try:
            result = self.sender.send_file(task['file'], task['recipient'])
            if result:
                self.tasks[task_idx]['status'] = '✓ 成功'
                self._log(f"任务 {os.path.basename(task['file'])} 发送成功，接收人: {task['recipient']}", 'success')
            else:
                self.tasks[task_idx]['status'] = '✗ 失败'
                self._log(f"任务 {os.path.basename(task['file'])} 发送失败，接收人: {task['recipient']}", 'error')
        except Exception as e:
            self.tasks[task_idx]['status'] = '✗ 失败'
            self._log(f"任务 {os.path.basename(task['file'])} 发送失败，接收人: {task['recipient']}, 错误信息: {str(e)}",
                      'error')
        finally:
            self._update_task_view()

    def _update_task_view(self):
        self.task_tree.delete(*self.task_tree.get_children())
        for task in self.tasks:
            item = self.task_tree.insert('', 'end', values=(
                task['status'],
                task['recipient'],
                task['time'].strftime("%Y-%m-%d %H:%M:%S"),
                os.path.basename(task['file'])
            ))
            if task['status'] == '✓ 成功':
                self.task_tree.item(item, tags=('success',))
            elif task['status'] == '✗ 失败':
                self.task_tree.item(item, tags=('error',))
        self.task_tree.tag_configure('success', foreground='green')
        self.task_tree.tag_configure('error', foreground='red')

    def _log(self, message, level='info'):
        self.log_text.config(state='normal')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        full_message = f"{timestamp} - {message}\n"
        self.log_text.insert(tk.END, full_message, level)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def _cancel_timers(self):
        for timer in self.timers:
            if timer.is_alive():
                timer.cancel()
        self.timers = []

    def destroy(self):
        self._cancel_timers()
        super().destroy()


if __name__ == "__main__":
    app = TaskManagerApp()
    app.mainloop()
