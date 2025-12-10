import platform
import threading
import subprocess
import os
import re

class TextToSpeech:
    def __init__(self):
        self.system = platform.system()
        self.available = self.check_availability()
    
    def check_availability(self):
        """检查系统语音功能"""
        try:
            if self.system == "Windows":
                return True  # Windows自带语音功能
            elif self.system == "Darwin":  # macOS
                result = subprocess.run(["which", "say"], capture_output=True)
                return result.returncode == 0
            elif self.system == "Linux":
                result = subprocess.run(["which", "espeak"], capture_output=True)
                return result.returncode == 0
            return False
        except:
            return False
    
    def speak(self, text):
        """朗读文本"""
        if not self.available or not text:
            return
        
        # 清理文本，移除特殊字符
        text = self.clean_text(text)
        
        def _speak():
            try:
                if self.system == "Windows":
                    self._speak_windows(text)
                elif self.system == "Darwin":
                    self._speak_macos(text)
                elif self.system == "Linux":
                    self._speak_linux(text)
            except Exception as e:
                print(f"语音合成失败: {str(e)}")
        
        thread = threading.Thread(target=_speak)
        thread.daemon = True
        thread.start()
    
    def clean_text(self, text):
        """清理文本，移除特殊字符，但保留完整词组"""
        if not text:
            return ""
        
        # 移除音标标记和特殊字符，但保留空格（词组的完整性）
        text = text.replace('/', '').replace('#', '')
        text = re.sub(r'\[.*?\]', '', text)  # 移除方括号内容
        text = re.sub(r'【.*?】', '', text)   # 移除中文括号内容
        text = text.replace('"', '').replace("'", "")
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _speak_windows(self, text):
        """Windows语音合成"""
        try:
            # 清理文本中的特殊字符
            text = text.replace('"', '').replace("'", "")
            
            # 使用VBScript
            vbs_code = f'CreateObject("SAPI.SpVoice").Speak "{text}"'
            with open("temp_speak.vbs", "w", encoding="gbk") as f:
                f.write(vbs_code)
            subprocess.run(["cscript", "//Nologo", "temp_speak.vbs"], 
                         capture_output=True, timeout=10)
            if os.path.exists("temp_speak.vbs"):
                os.remove("temp_speak.vbs")
        except subprocess.TimeoutExpired:
            print("语音合成超时")
        except Exception as e:
            print(f"Windows语音合成失败: {str(e)}")
    
    def _speak_macos(self, text):
        """macOS语音合成"""
        try:
            subprocess.run(["say", text], timeout=10)
        except subprocess.TimeoutExpired:
            print("语音合成超时")
        except Exception as e:
            print(f"macOS语音合成失败: {str(e)}")
    
    def _speak_linux(self, text):
        """Linux语音合成"""
        try:
            subprocess.run(["espeak", text], timeout=10)
        except subprocess.TimeoutExpired:
            print("语音合成超时")
        except Exception as e:
            print(f"Linux语音合成失败: {str(e)}")