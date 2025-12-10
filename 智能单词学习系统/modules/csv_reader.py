import csv
import re
import os

class CSVReader:
    @staticmethod
    def read_csv(file_path):
        """读取CSV文件，自动识别单词或词组"""
        vocabulary = []
        
        try:
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312']
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        content = file.read()
                        content = content.replace('\ufeff', '').replace('\r\n', '\n').replace('\r', '\n')
                        lines = content.strip().split('\n')
                        
                        # 检测文件类型：通过分析第一行判断是单词还是词组
                        is_phrase_file = CSVReader.detect_file_type(lines)
                        
                        for line_num, line in enumerate(lines, 1):
                            if not line.strip():
                                continue
                            
                            # 使用csv.reader来正确解析包含引号和逗号的CSV
                            try:
                                import io
                                csv_line = io.StringIO(line)
                                reader = csv.reader(csv_line)
                                parts = next(reader)
                                parts = [part.strip() for part in parts if part.strip()]
                            except:
                                # 如果csv.reader失败，回退到原来的逻辑
                                if ',' in line:
                                    parts = [part.strip() for part in line.split(',')]
                                elif '|' in line:
                                    parts = [part.strip() for part in line.split('|')]
                                else:
                                    continue
                            
                            parts = [part for part in parts if part]
                            
                            if len(parts) < 2:
                                continue
                            
                            english = parts[0].strip()
                            if not english:
                                continue
                            
                            # 直接读取第二列作为音标
                            phonetic = parts[1].strip() if len(parts) > 1 else ""
                            
                            if is_phrase_file:
                                # 词组处理逻辑
                                item = CSVReader.process_phrase(parts, english, phonetic)
                            else:
                                # 单词处理逻辑
                                item = CSVReader.process_word(parts, english, phonetic)
                            
                            if item:
                                vocabulary.append(item)
                        
                        if vocabulary:
                            file_type = "词组" if is_phrase_file else "单词"
                            print(f"使用编码 {encoding} 成功读取 {len(vocabulary)} 个{file_type}")
                            return vocabulary
                            
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"编码 {encoding} 读取失败: {str(e)}")
                    continue
            
            if not vocabulary:
                raise Exception("无法读取文件，请检查文件格式和编码")
                
        except Exception as e:
            raise Exception(f"读取CSV文件失败: {str(e)}")
    
    @staticmethod
    def detect_file_type(lines):
        """检测文件类型：词组文件通常包含多个【】和空格分隔的英文"""
        if not lines:
            return False
        
        first_line = lines[0]
        # 检测标准：包含多个【】或者英文中有空格（词组特征）
        bracket_count = first_line.count('【')
        has_space_in_english = ' ' in first_line.split(',')[0] if ',' in first_line else ' ' in first_line.split('|')[0] if '|' in first_line else False
        
        return bracket_count >= 2 or has_space_in_english
    
    @staticmethod
    def process_phrase(parts, english, phonetic):
        """处理词组"""
        # 处理中文释义：只取第3列的基本释义，并移除【】内容
        chinese = ""
        if len(parts) > 2:
            chinese = parts[2].strip()
            # 从中文释义中移除【】内容
            chinese = CSVReader.remove_details(chinese)
            # 清理引号和特殊字符
            chinese = chinese.replace('"', '').replace("'", "").strip()
        
        # 提取详细解释：每个【】内容单独一行
        details = CSVReader.extract_phrase_details(parts)
        
        # 如果中文释义为空，使用"暂无释义"
        if not chinese:
            chinese = "暂无释义"
        
        return {
            'english': english,
            'phonetic': phonetic,  # 直接使用CSV第二列的音标
            'chinese': chinese,
            'details': details,
            'is_phrase': True  # 标记为词组
        }
    
    @staticmethod
    def process_word(parts, english, phonetic):
        """处理单词 - 每个翻译用 | 隔开"""
        # 处理中文释义：从第3列开始，每个单元格是一个翻译，用 | 连接
        meanings = []
        if len(parts) > 2:
            for i in range(2, len(parts)):
                meaning = parts[i].strip()
                if meaning:
                    # 移除【】内容，只保留基本释义
                    clean_meaning = CSVReader.remove_details(meaning)
                    clean_meaning = clean_meaning.replace('"', '').replace("'", "").strip()
                    if clean_meaning:
                        meanings.append(clean_meaning)
        
        # 用 | 连接所有翻译
        chinese = " | ".join(meanings) if meanings else "暂无释义"
        
        # 提取详细解释：从所有部分中提取【】内容
        details = CSVReader.extract_details_from_parts(parts)
        
        return {
            'english': english,
            'phonetic': phonetic,  # 直接使用CSV第二列的音标
            'chinese': chinese,
            'details': details,
            'is_phrase': False  # 标记为单词
        }
    
    @staticmethod
    def extract_phrase_details(parts):
        """为词组提取详细解释，每个【】内容占一行"""
        try:
            details_list = []
            # 合并所有部分
            full_text = ' '.join(parts)
            # 只匹配中文括号【】
            pattern = r'【(.*?)】'
            
            matches = re.findall(pattern, full_text)
            
            # 清理每个详细解释
            for detail in matches:
                detail = re.sub(r'\s+', ' ', detail).strip()
                detail = detail.replace('"', '').replace("'", "")
                if detail:
                    details_list.append(detail)
            
            # 用换行符连接，每个【】内容占一行
            return '\n'.join(details_list) if details_list else ""
        except:
            return ""
    
    @staticmethod
    def extract_details_from_parts(parts):
        """从所有部分中提取【】内的详细解释（单词用）"""
        try:
            details = []
            # 合并所有部分
            full_text = ' '.join(parts)
            # 只匹配中文括号【】
            pattern = r'【(.*?)】'
            
            matches = re.findall(pattern, full_text)
            details.extend(matches)
            
            # 清理详细解释
            cleaned_details = []
            for detail in details:
                detail = re.sub(r'\s+', ' ', detail).strip()
                detail = detail.replace('"', '').replace("'", "")
                if detail:
                    cleaned_details.append(detail)
            
            return " | ".join(cleaned_details) if cleaned_details else ""
        except:
            return ""
    
    @staticmethod
    def remove_details(text):
        """只移除【】内的详细解释，保留其他内容"""
        try:
            # 只移除中文括号【】及其内容
            pattern = r'【.*?】'
            
            cleaned = re.sub(pattern, '', text)
            
            # 清理多余的分隔符和空格
            cleaned = re.sub(r'\s*\|\s*', ' | ', cleaned).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = re.sub(r'^\||\|$', '', cleaned).strip()
            cleaned = cleaned.replace('"', '').replace("'", "")
            
            return cleaned if cleaned else ""
        except:
            return text