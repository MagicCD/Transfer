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
              smoothing=0.1,
              ascii=is_windows) as pbar:
        progress = 0
        last_update = time.time()
        last_line = ""
        stalled_count = 0
        max_stalled = 10  # 最大停滞计数

        try:
            # 在Windows上使用二进制模式读取标准输入，避免编码问题
            if is_windows:
                import io

                # 将标准输入设置为二进制模式
                sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8', errors='replace')

            # 强制刷新进度条
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
                    if increment > 0 and progress < 95:
                        progress += min(increment, 95 - progress)  # 防止超过95%
                        pbar.update(increment)
                        pbar.refresh()  # 强制刷新进度条
                        stalled_count = 0  # 重置停滞计数
                        last_update = time.time()
                    else:
                        # 检测停滞
                        stalled_count += 1

                    # 每秒至少更新一小部分，确保进度条不会卡住
                    current_time = time.time()
                    if current_time - last_update >= 2.0 and progress < 95:
                        # 根据停滞时间动态调整增量
                        time_diff = current_time - last_update
                        auto_increment = min(0.5 * time_diff, 95 - progress)  # 每2秒最多增加0.5%

                        if auto_increment > 0:
                            pbar.update(auto_increment)
                            pbar.refresh()  # 强制刷新进度条
                            progress += auto_increment
                            last_update = current_time

                    # 如果连续停滞过多，显示一些信息
                    if stalled_count >= max_stalled:
                        # 在Windows上使用简单的进度显示
                        if is_windows:
                            print(f"\r打包进行中... 当前进度: {progress:.1f}%", end="")
                        else:
                            print(f"\n打包进行中... 当前进度: {progress:.1f}%")
                            print(f"最后输出: {last_line[:80]}..." if len(last_line) > 80 else f"最后输出: {last_line}")
                        stalled_count = 0
                        sys.stdout.flush()  # 强制刷新输出
                except UnicodeDecodeError:
                    # 处理编码错误
                    print(f"\r警告: 编码错误，跳过此行", end="")
                    continue
        except KeyboardInterrupt:
            print("\n用户中断打包进程")
            return
        except Exception as e:
            print(f"\n进度显示出错: {e}")
            # 继续执行以完成进度条

        # 确保进度条完成
        remaining = 100 - progress
        if remaining > 0:
            pbar.update(remaining)
            pbar.refresh()  # 强制刷新进度条

        # 根据终端类型调整输出格式
        if is_windows:
            print("\r打包完成!" + " " * 50)  # 添加空格清除之前的输出
        else:
            print("\n打包完成!")

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
        print(f"进度显示出错: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)