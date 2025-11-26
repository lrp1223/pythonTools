import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re
from typing import Union, List

# ===== 常量定义 =====
WEIGHT = [1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28]
BASE_CODE = "0123456789ABCDEFGHJKLMNPQRTUWXY"
CODE_INDEX_MAP = {char: idx for idx, char in enumerate(BASE_CODE)}
CREDIT_CODE_PATTERN = re.compile(r'^[0-9A-HJ-NPQRTUWXY]{2}\d{6}[0-9A-HJ-NPQRTUWXY]{10}$')

# ===== 验证函数 =====
def is_credit_code_simple(credit_code: Union[str, None]) -> bool:
    """简单的正则校验（格式检查）"""
    if not credit_code or len(credit_code) != 18:
        return False
    return bool(CREDIT_CODE_PATTERN.match(credit_code))

def get_parity_bit(credit_code: str) -> int:
    """计算校验位索引"""
    if len(credit_code) < 17:
        return -1
    
    total = 0
    for i in range(17):
        char = credit_code[i]
        code_index = CODE_INDEX_MAP.get(char)
        if code_index is None:
            return -1
        total += code_index * WEIGHT[i]
    
    result = 31 - (total % 31)
    return 0 if result == 31 else result

def is_credit_code(credit_code: Union[str, None]) -> bool:
    """完整的统一社会信用代码校验"""
    if not is_credit_code_simple(credit_code):
        return False
    
    parity_bit = get_parity_bit(credit_code)
    if parity_bit < 0:
        return False
    
    return credit_code[17].upper() == BASE_CODE[parity_bit]

def validate_credit_codes(codes_text: str) -> dict:
    """验证输入的信用代码"""
    # 解析输入（支持逗号、空格、换行分隔）
    codes = []
    for line in codes_text.splitlines():
        line_codes = [code.strip() for code in re.split(r'[,，\s]+', line) if code.strip()]
        codes.extend(line_codes)
    
    if not codes:
        return {"error": "没有找到有效的信用代码", "valid": [], "invalid": []}
    
    # 验证每个代码
    valid_codes = []
    invalid_codes = []
    
    for code in codes:
        if is_credit_code(code):
            valid_codes.append(code)
        else:
            invalid_codes.append(code)
    
    return {
        "total": len(codes),
        "valid": valid_codes,
        "invalid": invalid_codes,
        "error": None
    }

class CreditCodeValidatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("统一社会信用代码验证工具")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)
        
        # 设置窗口图标（可选）
        try:
            self.root.iconbitmap(default='app.ico')
        except:
            pass
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="统一社会信用代码验证工具", 
                               font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # 输入区域
        input_frame = ttk.LabelFrame(main_frame, text="输入信用代码", padding="10")
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        
        # 输入说明
        input_tip = ttk.Label(input_frame, text="请输入信用代码，用逗号、空格或换行分隔", 
                             font=("微软雅黑", 9))
        input_tip.pack(anchor=tk.W, pady=(0, 5))
        
        # 输入文本框
        self.input_text = scrolledtext.ScrolledText(input_frame, width=40, height=20, 
                                                   font=("Consolas", 10))
        self.input_text.pack(fill=tk.BOTH, expand=True)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        self.validate_btn = ttk.Button(button_frame, text="开始验证", 
                                      command=self.validate_codes, style="Accent.TButton")
        self.validate_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(button_frame, text="清空", command=self.clear_all)
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        self.load_btn = ttk.Button(button_frame, text="加载文件", command=self.load_file)
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_btn = ttk.Button(button_frame, text="保存错误结果", command=self.save_results)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # 输出区域
        output_frame = ttk.LabelFrame(main_frame, text="验证结果", padding="10")
        output_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        
        # 统计信息
        self.stats_label = ttk.Label(output_frame, text="准备就绪", font=("微软雅黑", 10))
        self.stats_label.pack(anchor=tk.W, pady=(0, 5))
        
        # 输出文本框
        self.output_text = scrolledtext.ScrolledText(output_frame, width=40, height=20, 
                                                    font=("Consolas", 10), state=tk.DISABLED)
        self.output_text.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_bar = ttk.Label(main_frame, text="", font=("微软雅黑", 9))
        self.status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
    def validate_codes(self):
        """验证信用代码"""
        # 获取输入文本
        input_content = self.input_text.get("1.0", tk.END).strip()
        
        if not input_content:
            messagebox.showwarning("警告", "请输入要验证的信用代码")
            return
        
        # 开始验证
        self.set_status("正在验证...")
        self.validate_btn.config(state=tk.DISABLED)
        
        # 验证
        results = validate_credit_codes(input_content)
        
        # 恢复按钮状态
        self.validate_btn.config(state=tk.NORMAL)
        
        if results.get("error"):
            messagebox.showerror("错误", results["error"])
            self.set_status("验证失败")
            return
        
        # 更新统计信息
        stats_text = f"总共: {results['total']} 个 | 有效: {len(results['valid'])} 个 | 无效: {len(results['invalid'])} 个"
        self.stats_label.config(text=stats_text)
        
        # 显示错误结果
        self.display_results(results)
        
        if len(results['invalid']) == 0:
            self.set_status("验证完成 - 所有代码都有效！")
            messagebox.showinfo("完成", "所有信用代码都通过了验证！")
        else:
            self.set_status(f"验证完成 - 发现 {len(results['invalid'])} 个无效代码")
        
    def display_results(self, results):
        """显示验证结果"""
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        
        if results['invalid']:
            self.output_text.insert(tk.END, "❌ 以下是无效的信用代码：\n")
            self.output_text.insert(tk.END, "=" * 50 + "\n\n")
            
            for i, code in enumerate(results['invalid'], 1):
                # 分析错误原因
                error_reason = self.get_error_reason(code)
                self.output_text.insert(tk.END, f"{i}. {code}\n")
                self.output_text.insert(tk.END, f"   错误原因: {error_reason}\n\n")
        else:
            self.output_text.insert(tk.END, "✅ 所有信用代码都有效！\n")
            
        self.output_text.config(state=tk.DISABLED)
        
    def get_error_reason(self, code):
        """分析错误原因"""
        if not code or len(code) != 18:
            return "长度不是18位"
        
        if not is_credit_code_simple(code):
            # 检查包含的非法字符
            invalid_chars = []
            for char in code.upper():
                if char not in BASE_CODE:
                    invalid_chars.append(char)
            if invalid_chars:
                return f"包含非法字符: {', '.join(set(invalid_chars))}"
            return "格式不符合要求"
        
        # 校验位错误
        parity_bit = get_parity_bit(code)
        if parity_bit >= 0:
            expected_char = BASE_CODE[parity_bit]
            return f"校验位错误，应为 '{expected_char}'"
        
        return "未知错误"
        
    def clear_all(self):
        """清空所有内容"""
        self.input_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.NORMAL)
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state=tk.DISABLED)
        self.stats_label.config(text="准备就绪")
        self.set_status("已清空")
        
    def load_file(self):
        """加载文件"""
        filename = filedialog.askopenfilename(
            title="选择信用代码文件",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.set_status(f"已加载文件: {filename}")
            except Exception as e:
                messagebox.showerror("错误", f"加载文件失败: {str(e)}")
                
    def save_results(self):
        """保存错误结果"""
        output_content = self.output_text.get("1.0", tk.END).strip()
        
        if not output_content or output_content == "✅ 所有信用代码都有效！":
            messagebox.showinfo("提示", "没有错误结果需要保存")
            return
            
        filename = filedialog.asksaveasfilename(
            title="保存错误结果",
            defaultextension=".txt",
            filetypes=[
                ("文本文件", "*.txt"),
                ("所有文件", "*.*")
            ]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output_content)
                self.set_status(f"错误结果已保存到: {filename}")
                messagebox.showinfo("完成", "错误结果已保存")
            except Exception as e:
                messagebox.showerror("错误", f"保存文件失败: {str(e)}")
                
    def set_status(self, message):
        """设置状态栏信息"""
        self.status_bar.config(text=message)

def main():
    """主函数"""
    root = tk.Tk()
    app = CreditCodeValidatorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
