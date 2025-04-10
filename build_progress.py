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
    # 使用更多的进度条配置选项
    with tqdm(total=100, desc='打包进度', ncols=80,
              bar_format='{desc}: {percentage:3.0f}%|{bar}| {elapsed}<{remaining}',
              colour='green', smoothing=0.1) as pbar:
        progress = 0
        last_update = time.time()
        last_line = ""
        stalled_count = 0
        max_stalled = 10  # 最大停滞计数

        try:
            for line in sys.stdin:
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
                        progress += auto_increment
                        last_update = current_time

                # 如果连续停滞过多，显示一些信息
                if stalled_count >= max_stalled:
                    print(f"\n打包进行中... 当前进度: {progress:.1f}%")
                    print(f"最后输出: {last_line[:80]}..." if len(last_line) > 80 else f"最后输出: {last_line}")
                    stalled_count = 0
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

        print("\n打包完成!")

if __name__ == '__main__':
    try:
        # 设置缓冲区模式，提高输出效率
        sys.stdout.reconfigure(line_buffering=True) if hasattr(sys.stdout, 'reconfigure') else None
        sys.stderr.reconfigure(line_buffering=True) if hasattr(sys.stderr, 'reconfigure') else None

        # 设置信号处理
        import signal
        def signal_handler(sig, frame):
            print('\n用户中断打包进程')
            sys.exit(0)

        # 注册 CTRL+C 处理程序
        signal.signal(signal.SIGINT, signal_handler)

        # 运行主程序
        main()
    except Exception as e:
        import traceback
        print(f"进度显示出错: {e}", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)