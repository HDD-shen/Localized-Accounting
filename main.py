# -*- coding: utf-8 -*-
"""
纯Tkinter版个人记账本系统 V1.0
作者：[你的名字]
特点：仅使用Python标准库，无第三方依赖
功能：记账、统计、导出、分类管理
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import csv
import os
import json
from datetime import datetime

# 全局路径配置
DATA_DIR = "data"
RECORDS_FILE = os.path.join(DATA_DIR, "records.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.json")


def init_app():
    """初始化数据目录和文件"""
    os.makedirs(DATA_DIR, exist_ok=True)

    # 初始化分类
    if not os.path.exists(CATEGORIES_FILE):
        default_cats = {
            "支出": ["餐饮", "交通", "购物", "娱乐", "医疗", "房租", "其他"],
            "收入": ["工资", "兼职", "理财", "红包", "其他"]
        }
        with open(CATEGORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_cats, f, ensure_ascii=False, indent=2)

    # 初始化记录文件
    if not os.path.exists(RECORDS_FILE):
        with open(RECORDS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "类型", "金额", "类别", "备注"])


def load_categories():
    """加载分类配置"""
    with open(CATEGORIES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_records():
    """从CSV加载所有记录"""
    records = []
    if not os.path.exists(RECORDS_FILE):
        return records
    with open(RECORDS_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # 跳过标题行
        for row in reader:
            if len(row) == 5:
                try:
                    amount = float(row[2])
                    records.append([row[0], row[1], amount, row[3], row[4]])
                except ValueError:
                    continue  # 跳过无效金额
    return records


def save_record(date, r_type, amount, category, note):
    """保存新记录到CSV"""
    try:
        amount = float(amount)
        if amount <= 0:
            raise ValueError("金额必须大于0")
        with open(RECORDS_FILE, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([date, r_type, amount, category, note])
        return True
    except Exception as e:
        messagebox.showerror("错误", f"保存失败：{e}")
        return False


def delete_record(index):
    """删除指定索引的记录"""
    records = load_records()
    if 0 <= index < len(records):
        del records[index]
        # 重新写入文件
        with open(RECORDS_FILE, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["日期", "类型", "金额", "类别", "备注"])
            for r in records:
                writer.writerow(r)
        return True
    return False


def export_to_csv():
    """导出所有记录为CSV"""
    records = load_records()
    if not records:
        messagebox.showinfo("提示", "没有数据可导出")
        return
    filepath = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV 文件", "*.csv")],
        title="导出为CSV"
    )
    if filepath:
        try:
            with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(["日期", "类型", "金额", "类别", "备注"])
                for r in records:
                    writer.writerow(r)
            messagebox.showinfo("成功", f"已导出至：\n{filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{e}")


class ExpenseTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("个人记账本系统  V1.0")
        self.root.geometry("900x650")
        self.root.minsize(800, 500)

        # 初始化数据
        init_app()
        self.categories = load_categories()

        # 创建状态栏
        self.status_var = tk.StringVar(value="就绪")
        status_bar = tk.Label(root, textvariable=self.status_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 主框架
        main_frame = ttk.Frame(root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 左侧控制面板
        control_frame = ttk.LabelFrame(main_frame, text="操作区", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 添加记录区域
        add_frame = ttk.LabelFrame(control_frame, text="添加新记录", padding=10)
        add_frame.pack(fill=tk.X, pady=(0, 10))

        # 日期
        ttk.Label(add_frame, text="日期:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(add_frame, textvariable=self.date_var, width=12).grid(row=0, column=1, sticky=tk.W, padx=(5, 0))

        # 类型
        ttk.Label(add_frame, text="类型:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.type_var = tk.StringVar(value="支出")
        type_combo = ttk.Combobox(add_frame, textvariable=self.type_var, values=["收入", "支出"], state="readonly",
                                  width=10)
        type_combo.grid(row=1, column=1, sticky=tk.W, padx=(5, 0))
        type_combo.bind('<<ComboboxSelected>>', self.on_type_change)

        # 类别
        ttk.Label(add_frame, text="类别:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.category_var = tk.StringVar()
        self.cat_combo = ttk.Combobox(add_frame, textvariable=self.category_var, state="readonly", width=12)
        self.cat_combo.grid(row=2, column=1, sticky=tk.W, padx=(5, 0))
        self.update_category_combo()

        # 金额 & 备注
        ttk.Label(add_frame, text="金额:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.amount_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.amount_var, width=15).grid(row=3, column=1, sticky=tk.W, padx=(5, 0))

        ttk.Label(add_frame, text="备注:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.note_var = tk.StringVar()
        ttk.Entry(add_frame, textvariable=self.note_var, width=15).grid(row=4, column=1, sticky=tk.W, padx=(5, 0))

        ttk.Button(add_frame, text="添加记录", command=self.add_record, style="Accent.TButton").grid(row=5, column=0,
                                                                                                     columnspan=2,
                                                                                                     pady=(10, 0))

        # 功能按钮
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Button(btn_frame, text="刷新数据", command=self.refresh_all).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="导出 CSV", command=export_to_csv).pack(fill=tk.X, pady=2)
        ttk.Button(btn_frame, text="清空所有数据", command=self.clear_all).pack(fill=tk.X, pady=2)

        # 主显示区
        display_frame = ttk.Frame(main_frame)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 统计信息文本框
        self.stat_text = tk.Text(display_frame, height=4, state=tk.DISABLED, font=("Microsoft YaHei", 10))
        self.stat_text.pack(fill=tk.X, pady=(0, 10))

        # 记录表格
        tree_frame = ttk.Frame(display_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("日期", "类型", "金额", "类别", "备注")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            width = 100 if col == "日期" else 80 if col in ["类型", "金额", "类别"] else 200
            self.tree.column(col, width=width, anchor=tk.CENTER if col != "备注" else tk.W)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        hsb.pack(side=tk.BOTTOM, fill=tk.X)

        # 右键菜单
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="删除选中记录", command=self.delete_selected)

        # 初始加载
        self.refresh_all()

    def on_type_change(self, event=None):
        self.update_category_combo()

    def update_category_combo(self):
        r_type = self.type_var.get()
        cats = self.categories.get(r_type, [])
        self.cat_combo['values'] = cats
        if cats:
            self.category_var.set(cats[0])

    def add_record(self):
        date = self.date_var.get().strip()
        r_type = self.type_var.get()
        amount = self.amount_var.get().strip()
        category = self.category_var.get()
        note = self.note_var.get().strip()

        if not date or not amount:
            messagebox.showwarning("输入错误", "日期和金额不能为空！")
            return
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("格式错误", "日期格式应为 YYYY-MM-DD")
            return

        if save_record(date, r_type, amount, category, note):
            self.status_var.set(f"✅ 记录已添加：{r_type} ¥{amount} ({category})")
            self.refresh_all()
            self.clear_inputs()
        else:
            self.status_var.set("❌ 添加失败")

    def clear_inputs(self):
        self.amount_var.set("")
        self.note_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))

    def refresh_all(self):
        self.load_tree_data()
        self.update_statistics()

    def load_tree_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        records = load_records()
        for rec in records:
            amount_str = f"¥{rec[2]:.2f}"
            self.tree.insert("", tk.END, values=(rec[0], rec[1], amount_str, rec[3], rec[4]))

    def update_statistics(self):
        records = load_records()
        total_income = sum(r[2] for r in records if r[1] == "收入")
        total_expense = sum(r[2] for r in records if r[1] == "支出")
        balance = total_income - total_expense

        current_month = datetime.now().strftime("%Y-%m")
        month_income = sum(r[2] for r in records if r[1] == "收入" and r[0].startswith(current_month))
        month_expense = sum(r[2] for r in records if r[1] == "支出" and r[0].startswith(current_month))

        stat_info = (
            f"📊 总览：总收入 ¥{total_income:.2f} | 总支出 ¥{total_expense:.2f} | 结余 ¥{balance:.2f}\n"
            f"📅 本月：收入 ¥{month_income:.2f} | 支出 ¥{month_expense:.2f} | 月结余 ¥{month_income - month_expense:.2f}"
        )

        self.stat_text.config(state=tk.NORMAL)
        self.stat_text.delete(1.0, tk.END)
        self.stat_text.insert(tk.END, stat_info)
        self.stat_text.config(state=tk.DISABLED)

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            return
        confirm = messagebox.askyesno("确认删除", "确定要删除选中的记录吗？")
        if confirm:
            index = self.tree.index(selected[0])
            if delete_record(index):
                self.status_var.set("✅ 记录已删除")
                self.refresh_all()
            else:
                messagebox.showerror("错误", "删除失败")

    def clear_all(self):
        confirm = messagebox.askyesno("危险操作", "此操作将清空所有记录并无法恢复！\n确定继续？")
        if confirm:
            if os.path.exists(RECORDS_FILE):
                os.remove(RECORDS_FILE)
            init_app()
            self.refresh_all()
            self.status_var.set("🗑️ 所有数据已清空")


if __name__ == "__main__":
    root = tk.Tk()
    # 设置默认字体（可选）
    default_font = ("Microsoft YaHei", 9)
    root.option_add("*Font", default_font)

    app = ExpenseTrackerApp(root)
    root.mainloop()