import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import random
from modules.csv_reader import CSVReader
from modules.tts import TextToSpeech

class VocabUI:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.init_data()
        self.init_modules()
        self.create_ui()
        self.update_display()
    
    def setup_window(self):
        """设置窗口"""
        self.root.title("智能单词学习系统")
        self.root.geometry("900x650")
        self.root.configure(bg="#f5f5f5")
        self.root.minsize(850, 600)
        
    def init_data(self):
        """初始化数据"""
        self.vocabulary = []
        self.current_index = 0
        self.hide_chinese = False
        self.hide_english = False
        self.hide_details = False
        self.quiz_mode = False
        self.theme_mode = "light"
        
    def init_modules(self):
        """初始化模块"""
        self.tts = TextToSpeech()
        self.load_sample_words()
    
    def load_sample_words(self):
        """加载示例单词"""
        self.vocabulary = [
            {"english": "apple", "phonetic": "/ˈæpl/", "chinese": "苹果", "details": "n.水果", "is_phrase": False},
            {"english": "book", "phonetic": "/bʊk/", "chinese": "书", "details": "n.阅读材料", "is_phrase": False},
            {"english": "computer", "phonetic": "/kəmˈpjuːtər/", "chinese": "电脑", "details": "n.电子设备", "is_phrase": False},
            {"english": "beautiful", "phonetic": "/ˈbjuːtɪfl/", "chinese": "美丽的", "details": "adj.漂亮的", "is_phrase": False},
            {"english": "run", "phonetic": "/rʌn/", "chinese": "跑步", "details": "v.运动", "is_phrase": False}
        ]
    
    def create_ui(self):
        """创建界面"""
        self.create_main_frame()
        self.create_header()
        self.create_word_card()
        self.create_quiz_panel()
        self.create_control_panel()
        self.create_status_bar()
    
    def create_main_frame(self):
        """创建主框架"""
        self.main_frame = ttk.Frame(self.root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(2, weight=1)
    
    def create_header(self):
        """创建标题栏"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        header_frame.columnconfigure(0, weight=1)
        
        title_label = ttk.Label(header_frame, text="📚 智能单词学习系统", 
                               font=("微软雅黑", 18, "bold"), foreground="#2c3e50")
        title_label.grid(row=0, column=0, sticky="w")
        
        self.theme_btn = ttk.Button(header_frame, text="🌙 暗色模式", 
                                   command=self.toggle_theme, width=12)
        self.theme_btn.grid(row=0, column=1, sticky="e")
        
        header_frame.columnconfigure(0, weight=1)
    
    def create_word_card(self):
        """创建单词卡片"""
        self.card_frame = ttk.LabelFrame(self.main_frame, text="单词学习", padding="25")
        self.card_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # 创建一个内部框架来更好地控制布局
        content_frame = ttk.Frame(self.card_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        self.word_label = ttk.Label(content_frame, text="", 
                                   font=("Arial", 28, "bold"), foreground="#2c3e50")
        self.word_label.pack(pady=(10, 5))
        
        phonetic_frame = ttk.Frame(content_frame)
        phonetic_frame.pack(pady=5)
        
        self.phonetic_label = ttk.Label(phonetic_frame, text="", 
                                       font=("Arial", 14, "italic"), foreground="#7f8c8d")
        self.phonetic_label.pack(side=tk.LEFT)
        
        self.speak_btn = ttk.Button(phonetic_frame, text="🔊 发音", 
                                   command=self.speak_word, width=8)
        self.speak_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        self.chinese_label = ttk.Label(content_frame, text="", 
                                      font=("微软雅黑", 16), foreground="#34495e")
        self.chinese_label.pack(pady=10)
        
        # 详细解释标签 - 使用框架确保居中
        details_container = ttk.Frame(content_frame)
        details_container.pack(pady=5, fill=tk.BOTH, expand=True)
        
        self.details_label = ttk.Label(details_container, text="", 
                                      font=("微软雅黑", 11), 
                                      foreground="#95a5a6",
                                      wraplength=500,
                                      justify=tk.CENTER)
        self.details_label.pack(expand=True)
        
        if not self.tts.available:
            self.speak_btn.config(state="disabled", text="🔇 发音")
    
    def create_quiz_panel(self):
        """创建默写面板"""
        self.quiz_frame = ttk.Frame(self.main_frame)
        self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
        self.quiz_frame.columnconfigure(1, weight=1)
        
        input_frame = ttk.Frame(self.quiz_frame)
        input_frame.pack(fill=tk.X, pady=5)
        input_frame.columnconfigure(1, weight=1)
        
        ttk.Label(input_frame, text="请输入英文单词:", 
                 font=("微软雅黑", 10)).grid(row=0, column=0, padx=(0, 10), sticky="w")
        
        self.quiz_entry = ttk.Entry(input_frame, font=("Arial", 12))
        self.quiz_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.quiz_entry.bind("<Return>", self.check_quiz_answer)
        
        self.check_btn = ttk.Button(input_frame, text="✅ 检查答案", 
                                   command=self.check_quiz_answer, width=12)
        self.check_btn.grid(row=0, column=2, sticky="e")
        
        self.hint_label = ttk.Label(self.quiz_frame, text="", 
                                   font=("微软雅黑", 10), foreground="#e74c3c")
        self.hint_label.pack(pady=5)
        
        self.quiz_frame.pack_forget()
    
    def create_control_panel(self):
        """创建控制面板"""
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=10)
        control_frame.columnconfigure(0, weight=1)
        
        main_control_frame = ttk.Frame(control_frame)
        main_control_frame.pack(pady=5)
        
        # 文件操作按钮
        file_frame = ttk.Frame(main_control_frame)
        file_frame.pack(pady=5)
        
        ttk.Button(file_frame, text="📁 导入CSV", 
                  command=self.import_csv, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(file_frame, text="🔄 随机打乱", 
                  command=self.shuffle_words, width=12).pack(side=tk.LEFT, padx=3)
        
        # 模式切换按钮
        mode_frame = ttk.Frame(main_control_frame)
        mode_frame.pack(pady=5)
        
        self.quiz_btn = ttk.Button(mode_frame, text="✏️ 开始默写", 
                                  command=self.toggle_quiz_mode, width=12)
        self.quiz_btn.pack(side=tk.LEFT, padx=3)
        
        # 显示控制按钮
        display_frame = ttk.Frame(main_control_frame)
        display_frame.pack(pady=5)
        
        # 第一个按钮：显示英文
        self.english_btn = ttk.Button(display_frame, text="👁️ 显示英文", 
                                     command=self.toggle_english, width=12)
        self.english_btn.pack(side=tk.LEFT, padx=3)
        
        # 第二个按钮：显示中文
        self.chinese_btn = ttk.Button(display_frame, text="👁️ 显示中文", 
                                     command=self.toggle_chinese, width=12)
        self.chinese_btn.pack(side=tk.LEFT, padx=3)
        
        # 第三个按钮：显示解释
        self.details_btn = ttk.Button(display_frame, text="📖 显示解释", 
                                     command=self.toggle_details, width=12)
        self.details_btn.pack(side=tk.LEFT, padx=3)
        
        # 导航按钮
        nav_frame = ttk.Frame(main_control_frame)
        nav_frame.pack(pady=5)
        
        ttk.Button(nav_frame, text="⬅️ 上一个", 
                  command=self.prev_word, width=12).pack(side=tk.LEFT, padx=3)
        ttk.Button(nav_frame, text="下一个 ➡️", 
                  command=self.next_word, width=12).pack(side=tk.LEFT, padx=3)
    
    def create_status_bar(self):
        """创建状态栏"""
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.columnconfigure(0, weight=1)
        
        self.status_label = ttk.Label(status_frame, text="👋 欢迎使用单词学习系统", 
                                     font=("微软雅黑", 9), foreground="#7f8c8d")
        self.status_label.grid(row=0, column=0, sticky="w")
        
        self.count_label = ttk.Label(status_frame, text="0/0", 
                                    font=("微软雅黑", 9), foreground="#7f8c8d")
        self.count_label.grid(row=0, column=1, padx=10)
        
        self.progress = ttk.Progressbar(status_frame, length=120, mode='determinate')
        self.progress.grid(row=0, column=2, sticky="e")
    
    def toggle_quiz_mode(self):
        """切换默写模式"""
        if not self.vocabulary:
            messagebox.showwarning("提示", "请先导入单词")
            return
        
        self.quiz_mode = not self.quiz_mode
        
        if self.quiz_mode:
            self.quiz_btn.config(text="📚 学习模式")
            self.quiz_frame.pack(fill=tk.X, pady=(0, 10))
            self.quiz_entry.focus()
            self.hint_label.config(text="")
            self.status_label.config(text="✏️ 默写模式 - 根据中文意思输入英文单词")
        else:
            self.quiz_btn.config(text="✏️ 开始默写")
            self.quiz_frame.pack_forget()
            self.quiz_entry.delete(0, tk.END)
            self.hint_label.config(text="")
            self.status_label.config(text="📚 学习模式")
        
        self.update_display()
    
    def check_quiz_answer(self, event=None):
        """检查默写答案"""
        if not self.quiz_mode or not self.vocabulary:
            return
        
        user_answer = self.quiz_entry.get().strip()
        correct_answer = self.vocabulary[self.current_index]['english']
        
        if not user_answer:
            self.hint_label.config(text="⚠️ 请输入答案", foreground="#f39c12")
            return
        
        user_clean = user_answer.lower().strip()
        correct_clean = correct_answer.lower().strip()
        
        if user_clean == correct_clean:
            self.hint_label.config(text="✅ 回答正确！", foreground="#27ae60")
            self.status_label.config(text=f"✅ 回答正确: {correct_answer}")
            self.root.after(800, self.next_quiz_word)
        else:
            self.hint_label.config(
                text=f"❌ 错误！正确答案: {correct_answer} ({self.vocabulary[self.current_index]['phonetic']})", 
                foreground="#e74c3c"
            )
            self.quiz_entry.delete(0, tk.END)
            self.quiz_entry.focus()
    
    def next_quiz_word(self):
        """默写模式下跳到下一个单词"""
        if self.quiz_mode and self.vocabulary:
            self.next_word()
            self.quiz_entry.delete(0, tk.END)
            self.hint_label.config(text="")
            self.quiz_entry.focus()
    
    def import_csv(self):
        """导入CSV文件"""
        file_path = filedialog.askopenfilename(
            title="选择单词文件",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
        
        if not file_path:
            return
        
        try:
            self.vocabulary = CSVReader.read_csv(file_path)
            self.current_index = 0
            self.hide_chinese = False
            self.hide_english = False
            self.hide_details = False
            self.quiz_mode = False
            self.quiz_frame.pack_forget()
            self.quiz_btn.config(text="✏️ 开始默写")
            self.update_display()
            self.update_button_text()
            
            # 检测文件类型并显示相应提示
            if self.vocabulary and self.vocabulary[0].get('is_phrase', False):
                self.status_label.config(text=f"✅ 成功导入 {len(self.vocabulary)} 个词组")
            else:
                self.status_label.config(text=f"✅ 成功导入 {len(self.vocabulary)} 个单词")
                
        except Exception as e:
            messagebox.showerror("导入错误", f"导入失败：\n{str(e)}")
    
    def speak_word(self):
        """朗读当前单词或词组"""
        if self.vocabulary and self.tts.available:
            word = self.vocabulary[self.current_index]
            
            # 直接朗读完整的英文内容（无论是单词还是词组）
            speak_text = word['english']
            
            self.tts.speak(speak_text)
            self.status_label.config(text=f"🔊 正在朗读: {speak_text}")
    
    def toggle_chinese(self):
        """切换中文显示"""
        if not self.quiz_mode:
            self.hide_chinese = not self.hide_chinese
            self.update_display()
            self.update_button_text()
    
    def toggle_english(self):
        """切换英文显示"""
        if not self.quiz_mode:
            self.hide_english = not self.hide_english
            self.update_display()
            self.update_button_text()
    
    def toggle_details(self):
        """切换解释显示"""
        self.hide_details = not self.hide_details
        self.update_display()
        self.update_button_text()
    
    def update_button_text(self):
        """更新按钮文本"""
        self.english_btn.config(text="🙈 隐藏英文" if not self.hide_english else "👁️ 显示英文")
        self.chinese_btn.config(text="🙈 隐藏中文" if not self.hide_chinese else "👁️ 显示中文")
        self.details_btn.config(text="📕 隐藏解释" if not self.hide_details else "📖 显示解释")
    
    def shuffle_words(self):
        """随机打乱单词顺序"""
        if self.vocabulary:
            random.shuffle(self.vocabulary)
            self.current_index = 0
            self.update_display()
            self.status_label.config(text="🔀 单词顺序已打乱")
    
    def prev_word(self):
        """上一个单词"""
        if self.vocabulary:
            self.current_index = (self.current_index - 1) % len(self.vocabulary)
            self.quiz_entry.delete(0, tk.END)
            self.hint_label.config(text="")
            self.update_display()
    
    def next_word(self):
        """下一个单词"""
        if self.vocabulary:
            self.current_index = (self.current_index + 1) % len(self.vocabulary)
            self.quiz_entry.delete(0, tk.END)
            self.hint_label.config(text="")
            self.update_display()
    
    def update_display(self):
        """更新显示"""
        if not self.vocabulary:
            self.show_welcome()
            return
        
        word = self.vocabulary[self.current_index]
        
        # 检查是否是词组
        is_phrase = word.get('is_phrase', False)
        
        if self.quiz_mode:
            # 默写模式显示
            self.word_label.config(text="✏️ 请根据中文意思输入英文单词", foreground="#8e44ad")
            self.phonetic_label.config(text="")
            self.chinese_label.config(text=word['chinese'], foreground="#e74c3c")
            
            # 在默写模式下，解释可以根据按钮状态显示/隐藏
            display_details = "" if self.hide_details else word['details']
            
            # 设置解释标签的格式
            if is_phrase and display_details:
                self.details_label.config(
                    text=display_details,
                    font=("微软雅黑", 10),
                    justify=tk.LEFT,
                    wraplength=600
                )
            else:
                self.details_label.config(
                    text=display_details,
                    font=("微软雅黑", 11),
                    justify=tk.CENTER,
                    wraplength=500
                )
            
            # 在默写模式下只禁用中文和英文按钮，解释按钮保持可用
            self.chinese_btn.config(state="disabled")
            self.english_btn.config(state="disabled")
            self.details_btn.config(state="normal")
            
        else:
            # 学习模式显示
            # 显示/隐藏英文单词（独立控制）
            display_word = "?????" if self.hide_english else word['english']
            self.word_label.config(text=display_word, foreground="#2c3e50")
            
            # 显示/隐藏音标（跟随英文显示状态）
            display_phonetic = "" if self.hide_english else word['phonetic']
            self.phonetic_label.config(text=display_phonetic)
            
            # 显示/隐藏中文意思
            display_chinese = "????" if self.hide_chinese else word['chinese']
            self.chinese_label.config(text=display_chinese, foreground="#34495e")
            
            # 显示/隐藏详细解释
            # 简化逻辑：只有当显示解释按钮为显示状态，且中文也是显示状态时，才显示解释
            if not self.hide_details and not self.hide_chinese:
                display_details = word['details']
            else:
                display_details = ""
            
            # 设置解释标签的格式
            if is_phrase and display_details:
                # 为词组设置不同的字体和换行
                self.details_label.config(
                    text=display_details,
                    font=("微软雅黑", 10),
                    justify=tk.LEFT,
                    wraplength=600
                )
            else:
                # 单词保持原来的格式
                self.details_label.config(
                    text=display_details,
                    font=("微软雅黑", 11),
                    justify=tk.CENTER,
                    wraplength=500
                )
            
            # 在学习模式下启用所有显示控制按钮
            self.chinese_btn.config(state="normal")
            self.english_btn.config(state="normal")
            self.details_btn.config(state="normal")
        
        # 更新状态
        self.update_status()
    
    def show_welcome(self):
        """显示欢迎界面"""
        self.word_label.config(text="📚 单词学习系统", foreground="#2c3e50")
        self.phonetic_label.config(text="")
        self.chinese_label.config(text="点击'导入CSV'开始学习单词", foreground="#34495e")
        self.details_label.config(text="支持格式：英文,音标,中文意思1,中文意思2,...", foreground="#95a5a6")
        self.details_label.config(font=("微软雅黑", 11), justify=tk.CENTER, wraplength=500)
        self.progress['value'] = 0
        self.count_label.config(text="0/0")
        self.chinese_btn.config(state="disabled")
        self.english_btn.config(state="disabled")
        self.details_btn.config(state="disabled")
        self.quiz_btn.config(state="disabled")
    
    def update_status(self):
        """更新状态信息"""
        total = len(self.vocabulary)
        current = self.current_index + 1
        progress = (current / total) * 100
        
        mode_text = "✏️ 默写模式" if self.quiz_mode else "📚 学习模式"
        self.status_label.config(text=f"{mode_text} - 进度: {current}/{total}")
        self.count_label.config(text=f"{current}/{total}")
        self.progress['value'] = progress
        
        state = "normal" if self.vocabulary else "disabled"
        self.quiz_btn.config(state=state)
    
    def toggle_theme(self):
        """切换主题"""
        if self.theme_mode == "light":
            self.theme_mode = "dark"
            self.theme_btn.config(text="☀️ 亮色模式")
            self.root.configure(bg="#2c3e50")
            self.status_label.config(foreground="#bdc3c7")
        else:
            self.theme_mode = "light"
            self.theme_btn.config(text="🌙 暗色模式")
            self.root.configure(bg="#f5f5f5")
            self.status_label.config(foreground="#7f8c8d")