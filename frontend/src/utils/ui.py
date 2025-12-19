import streamlit as st
import time

class TaskProgress:
    """
    统一进度条管理器 (支持平滑动画 + 百分比显示 + 智能ETA预估)
    修复了起始阶段显示 "0秒" 的问题
    """
    def __init__(self, title="准备开始...", total=100):
        self.start_time = time.time()
        self.title = title
        self.curr_percent = 0
        self.bar = st.progress(0, text=f"0% {title}")

    def _format_time(self, seconds):
        """将秒数格式化为易读字符串"""
        if seconds < 0: return "计算中..."
        # [优化] 剩余时间太短时，显示更友好的文案
        if seconds < 2: 
            return "即将完成"
        if seconds < 60:
            return f"{int(seconds)}秒"
        m, s = divmod(int(seconds), 60)
        return f"{m}分{s}秒"

    def _get_eta_str(self, target_percent):
        """根据当前耗时和目标进度，计算预计剩余时间"""
        if target_percent <= 0:
            return "计算中..."
        if target_percent >= 100:
            return ""
            
        elapsed = time.time() - self.start_time
        
        # [核心修复] 如果任务刚开始不到 1 秒，数据样本太少，估算不准，统一显示“计算中”
        # 这避免了“前处理”阶段瞬间完成导致误判整个任务只需 0 秒
        if elapsed < 1.0:
            return "计算中..."

        # 算法: (已用时间 / 已完成百分比) * 剩余百分比
        # 增加一个平滑因子，防止初始阶段波动过大
        estimated_total = elapsed / (target_percent / 100.0)
        remaining = estimated_total - elapsed
        
        return f"⏳ 预计剩余: {self._format_time(remaining)}"

    def _animate_to(self, target_percent: int, message: str, eta_str: str):
        """
        内部辅助函数：从当前进度平滑动画过渡到目标进度
        """
        start = self.curr_percent
        end = min(100, max(0, target_percent))
        
        if end <= start:
            return

        diff = end - start
        step = 1 if diff < 30 else 2 
        delay = 0.01 if diff < 50 else 0.005 
        
        txt_base = message if message else self.title

        for p in range(start + 1, end + 1, step):
            display_text = f"{p}% {txt_base}"
            if eta_str:
                display_text += f" | {eta_str}"
            
            self.bar.progress(p / 100.0, text=display_text)
            time.sleep(delay)
        
        # 最后定格
        final_text = f"{end}% {txt_base}"
        if eta_str:
            final_text += f" | {eta_str}"
        self.bar.progress(end / 100.0, text=final_text)
        
        self.curr_percent = end

    def update(self, percent: int, message: str = None):
        """
        更新进度
        """
        # 实时计算 ETA
        eta = self._get_eta_str(percent)
        
        if percent > self.curr_percent:
            self._animate_to(percent, message, eta)
        else:
            txt = message if message else self.title
            display_text = f"{percent}% {txt}"
            if eta:
                display_text += f" | {eta}"
            self.bar.progress(percent / 100.0, text=display_text)

    def finish(self, message: str = "✅ 任务完成！"):
        """
        任务完成
        """
        elapsed = time.time() - self.start_time
        time_str = self._format_time(elapsed)
        
        # 完成时显示总耗时，而不是剩余时间
        finish_msg = f"处理完毕 (总耗时 {time_str})"
        self._animate_to(100, message=finish_msg, eta_str="")
        
        self.bar.progress(1.0, text=f"100% {message} (总耗时: {time_str})")
        time.sleep(1.0) 
        self.bar.empty()

    def fail(self, message: str = "❌ 任务失败"):
        self.bar.progress(1.0, text=f"100% {message}")
        time.sleep(2.0)
        self.bar.empty()