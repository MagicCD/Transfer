import sys
import time
from tqdm import tqdm

# 使用字典来加速匹配过程
PROGRESS_INCREMENTS = {
    'Analysis': 10,
    'Processing': 2,
    'Analyzing': 3,
    'Building': 5,
    'Copying': 2,
    'EXE': 8,    # 添加更多关键词匹配
    'PKG': 7,
    'Bootloader': 4,
    'Archive': 6
}

def parse_pyinstaller_output(line):
    """解析 PyInstaller 输出并返回进度增量
    使用字典查找来提高效率
    """
    # 对于每个关键词，检查它是否在行中
    for keyword, increment in PROGRESS_INCREMENTS.items():
        if keyword in line:
            return increment
    return 0

def main():
    # 检测终端类型和颜色支持
    is_windows = sys.platform.startswith('win')
    supports_color = False

    # 在Windows上检测是否支持ANSI颜色
    if is_windows:
        import os
        supports_color = os.environ.get('ANSICON') is not None or \
                        'WT_SESSION' in os.environ or \
                        'ConEmuANSI' in os.environ or \
                        os.environ.get('TERM') == 'xterm'
    else:
        supports_color = True

    # 设置进度条格式
    if is_windows:
        # Windows终端使用更简单的进度条格式
        bar_format = '{desc}: {percentage:3.0f}% |{bar}| {elapsed}'
    else:
        bar_format = '{desc}: {percentage:3.0f}%|{bar}| {elapsed}<{remaining}'

    # 使用更多的进度条配置选项
    with tqdm(total=100, desc='打包进度', ncols=80,
              bar_format=bar_format,
              colour='green' if supports_color else None,
              smoothing=0,  # Disable smoothing for more direct feedback
              ascii=is_windows) as pbar:
        progress = 0
        # Remove last_update, stalled_count, max_stalled as auto-increment is removed
        last_line = ""

        try:
            # 在Windows上使用二进制模式读取标准输入，避免编码问题
            if is_windows:
                import io
                import os # Ensure os is imported here if not already

                # 将标准输入设置为二进制模式
                # Ensure the encoding is suitable for PyInstaller output, e.g., 'cp437' or 'utf-8' might be needed
                # Using 'utf-8' with 'replace' errors as a general approach
                sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

            # 强制刷新进度条 - Initial display
            pbar.refresh()

            for line in sys.stdin:
                try:
                    line = line.strip()

                    # 跳过空行
                    if not line:
                        continue

                    # 记录最后一行输出，用于调试
                    last_line = line

                    # 基于 PyInstaller 输出更新进度
                    increment = parse_pyinstaller_output(line)
                    if increment > 0:
                        new_progress = min(progress + increment, 95) # Cap progress at 95% until completion
                        if new_progress > progress:
                             update_amount = new_progress - progress
                             pbar.update(update_amount)
                             progress = new_progress
                             # No need to manually refresh here, tqdm handles it on update

                except UnicodeDecodeError:
                    # 处理编码错误
                    # Avoid printing potentially disruptive messages during progress bar display
                    # Maybe log this to a file or handle differently if needed
                    pass # Silently ignore decoding errors for now
        except KeyboardInterrupt:
            print("\n用户中断打包进程")
            pbar.close() # Close the progress bar properly
            return
        except Exception as e:
            # Close the bar and print error below it
            pbar.close()
            print(f"\n进度显示处理时出错: {e}")
            import traceback
            traceback.print_exc(file=sys.stderr)
            # Try to let the build finish if possible, but progress reporting stops

        # 确保进度条完成到100%
        # Use pbar.n which is the current progress value according to tqdm
        remaining = pbar.total - pbar.n
        if remaining > 0:
            pbar.update(remaining)
        pbar.close() # Close the progress bar cleanly

        # 根据终端类型调整输出格式
        # Clear the line after closing the progress bar
        clear_line = "\r" + " " * (pbar.ncols if pbar.ncols else 80) + "\r"
        print(clear_line, end="") # Clear the progress bar line

        if is_windows:
            print("打包完成!")
        else:
            print("打包完成!") # No need for newline as pbar.close() handles it

        sys.stdout.flush()  # 强制刷新输出

if __name__ == '__main__':
    try:
        # 设置缓冲区模式，提高输出效率
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(line_buffering=True)
        if hasattr(sys.stderr, 'reconfigure'):
            sys.stderr.reconfigure(line_buffering=True)

        # 检测是否为Windows系统
        is_windows = sys.platform.startswith('win')

        # 在非Windows系统上设置信号处理
        if not is_windows:
            try:
                import signal
                # 注册 CTRL+C 处理程序
                signal.signal(signal.SIGINT, signal.SIG_DFL)  # 使用默认处理程序
            except Exception:
                pass  # 忽略信号处理错误

        # 在Windows上设置控制台模式
        if is_windows:
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                # 启用ANSI转义序列处理
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            except Exception:
                # 如果设置失败，忽略错误
                pass

        # 运行主程序
        main()
    except Exception as e:
        import traceback
        print(f"\n进度显示脚本运行时出错: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)