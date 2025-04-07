import sys
import time
from tqdm import tqdm

def parse_pyinstaller_output(line):
    """解析 PyInstaller 输出并返回进度增量"""
    if 'Analysis' in line:
        return 10
    elif 'Processing' in line:
        return 2
    elif 'Analyzing' in line:
        return 3
    elif 'Building' in line:
        return 5
    elif 'Copying' in line:
        return 2
    return 0

def main():
    with tqdm(total=100, desc='打包进度', ncols=80, bar_format='{desc}: {percentage:3.0f}%|{bar}|') as pbar:
        progress = 0
        last_update = time.time()
        
        for line in sys.stdin:
            line = line.strip()
            
            # 基于 PyInstaller 输出更新进度
            increment = parse_pyinstaller_output(line)
            if increment > 0 and progress < 95:
                progress += increment
                pbar.update(increment)
            
            # 每秒至少更新 1%，确保进度条不会卡住
            current_time = time.time()
            if current_time - last_update >= 1.0 and progress < 95:
                pbar.update(1)
                progress += 1
                last_update = current_time
        
        # 确保进度条完成
        if progress < 100:
            pbar.update(100 - progress)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"进度显示出错: {e}", file=sys.stderr)
        sys.exit(1)