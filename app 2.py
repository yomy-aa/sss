import os
import shutil
import pyudev
from datetime import datetime

def hide_console():
    """
    隐藏控制台窗口，确保程序在Windows系统上后台运行。
    """
    if os.name == 'nt':
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)

def copy_files(src, dst):
    """
    递归地将源目录中的所有文件复制到目标目录。
    如果目标目录不存在，则会自动创建。

    参数:
    src: str - 源目录路径（U盘挂载点）。
    dst: str - 目标目录路径（D盘中的备份路径）。
    """
    if not os.path.exists(dst):
        os.makedirs(dst)  # 如果目标目录不存在，创建它
    for item in os.listdir(src):  # 遍历源目录中的所有文件和文件夹
        source_item = os.path.join(src, item)
        dest_item = os.path.join(dst, item)
        if os.path.isdir(source_item):
            shutil.copytree(source_item, dest_item, False, None)  # 递归复制文件夹
        else:
            shutil.copy2(source_item, dest_item)  # 复制单个文件

def handle_usb_event(action, device):
    """
    处理U盘插入事件，将U盘中的文件复制到D盘的备份目录。

    参数:
    action: str - 设备的动作（插入或移除）。
    device: pyudev.Device - 设备信息，包含设备路径等信息。
    """
    if action == "add" and "ID_FS_TYPE" in device:
        # 获取U盘的挂载点
        mount_point = device.get('DEVNAME')

        # 设置备份目标目录（D盘中的 'bk' 文件夹）
        backup_dir = os.path.join("D:\\bk", f"usb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # 检查U盘是否已挂载
        if os.path.ismount(mount_point):
            copy_files(mount_point, backup_dir)  # 复制U盘文件到目标目录

def main():
    """
    主函数，负责隐藏控制台并启动监听器，等待U盘插入事件。
    """
    hide_console()  # 隐藏控制台窗口（仅适用于Windows系统）

    # 创建一个 pyudev 上下文，用于设备监控
    context = pyudev.Context()

    # 创建一个监控器，监听 'block' 子系统中的设备事件（如U盘插入）
    monitor = pyudev.Monitor.from_netlink(context)
    monitor.filter_by(subsystem="block")

    # 监听设备的插入和移除事件，处理U盘插入事件
    for device in iter(monitor.poll, None):
        handle_usb_event(device.action, device)

if __name__ == "__main__":
    main()