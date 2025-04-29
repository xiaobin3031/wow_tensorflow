import threading
from concurrent.futures.thread import ThreadPoolExecutor

import pyscreenshot as ImageGrab
import time, os

from pynput.mouse import Listener as m_Listener, Button
from pynput.keyboard import Listener as k_Listener
from config import config_view

# 指定截全屏的范围，长度不为4，则默认截取全屏
g_all_img_points = None

g_keyboard_press = []
g_move_points = []
pool = ThreadPoolExecutor(max_workers=50)
# 文件跟目录
g_path_root = config_view['collect_file_root']
# 整个截图
g_path_all = os.path.join(g_path_root, 'all_screenshot')
os.makedirs(g_path_all, exist_ok=True)
# 左键点击保存的目录
g_path_left_click = os.path.join(g_path_root, 'left_click')
os.makedirs(g_path_left_click, exist_ok=True)
# 右键点击保存的目录
g_path_right_click = os.path.join(g_path_root, 'right_click')
os.makedirs(g_path_right_click, exist_ok=True)
# 鼠标和键盘信息目录
g_path_mouse_keyboard = os.path.join(g_path_root, 'mouse_keyboard')
os.makedirs(g_path_mouse_keyboard, exist_ok=True)

# 键盘按下的信息
g_press = {}

# 鼠标点击的目录
g_button_file_path = {
    Button.left: g_path_left_click, Button.right: g_path_right_click
}

# 移动应该没那么重要，只要计算出需要移动到的位置点就行了，至于中间
def on_move(x, y):
    if len(g_move_points) > 0:
        last_point = g_move_points[len(g_move_points) - 1]
        if abs(last_point[0] - x) > 10 or abs(last_point[1] - y) > 10:
            g_move_points.append([x, y])
    else:
        g_move_points.append([x, y])

def on_click(x, y, button, pressed):
    if button != Button.middle:
        move_points = g_move_points.copy()
        g_move_points.clear()
        # 如果最后一次按键是按下，还未释放，就不清空按键时间
        keyboard_press = g_keyboard_press.copy()
        if len(g_keyboard_press) > 0:
            if g_keyboard_press[len(g_keyboard_press) - 1][1] == "1":
                # 还未释放
                del g_keyboard_press[:len(g_keyboard_press) - 1]
            else:
                g_keyboard_press.clear()
        pool.submit(save_image_by_click_button, x, y, move_points, button, keyboard_press)

def save_image_by_click_button(x, y, move_points, button, keyboard_press):
    """
    点击鼠标后，保存图片
    :param x 点击坐标
    :param y 点击坐标
    :param move_points 上一次点击到这一次点击，鼠标移动的坐标
    :param button 鼠标点击的按钮
    :param keyboard_press 上一次点击到本次点击，简单的操作
    :return:
    """
    file_path = g_button_file_path[button]
    if file_path is None:
        return

    img = ImageGrab.grab(bbox=(min(max(x - 40, 0), x), min(max(y - 40, 0), y), x+40, y+40))
    prefix = 'fullscreen-' + time.strftime('%Y-%m-%d_%H-%M-%S')
    img_filename = 'fullscreen-' + time.strftime('%Y-%m-%d_%H-%M-%S') + '.png'
    # 保存点击图片
    img.save(os.path.join(file_path, img_filename))

    # 保存全屏图片
    img = ImageGrab.grab(bbox=g_all_img_points)
    img.save(os.path.join(g_path_all, img_filename))

    # todo 只取有效的坐标数，move_points

    datas = dict(
        x = x,
        y = y,
        button = str(button),
        move = move_points,
        key = keyboard_press
    )
    # 保存键盘鼠标信息
    with open(os.path.join(g_path_mouse_keyboard, prefix), 'w+') as file:
        file.write(str(datas))

def on_press(key):
    key_name = str(key)
    g_press[key_name] = time.time()

def on_release(key):
    key_name = str(key)
    if key_name in g_press:
        return
    p_time = g_press[key_name]
    del g_press[key_name]
    l_time = time.time()
    if l_time - p_time < 0.5:
        # 只是点击
        g_keyboard_press.append([key_name, "0"])

def listen_keyboard():
    with k_Listener(on_press=on_press, on_release=on_release) as listener:
        listener.run()

print('listen_mouse')
m_Listener(on_move=on_move, on_click=on_click).start()
# listen_mouse()
print('listen_keyboard')
listen_keyboard()
