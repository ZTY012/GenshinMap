import httpx
import json
from rich import print
from PIL import Image
from os import get_terminal_size, listdir, mkdir
from typing import Literal, List
from keyboard import wait, hook, KeyboardEvent, KEY_UP
from time import sleep

MapId = Literal[2, 7, 9]
POINT_WIDTH = 3
BLANK_LINES = 0

def download_map(map_id: MapId, use_temp=True):
    global size
    files = []
    resp = httpx.get(f"https://api-takumi.mihoyo.com/common/map_user/ys_obc/v1/map/info?map_id={map_id}&app_sn=ys_obc&lang=zh-cn").json()
    if resp["message"] == "OK":
        detail: dict = json.loads(resp["data"]["info"]["detail"])
        size = [detail["total_size"][0] / 4096, detail["total_size"][1] / 4096]
        for i in detail["slices"]:
            line = []
            for j in i:
                j = j["url"]
                filename = f"{map_id}_{j.split('/')[-1]}"
                if not (use_temp and filename in listdir("img")):
                    resp_ = httpx.get(j).read()
                    with open(f"img/{filename}", "wb") as fp:
                        fp.write(resp_)
                line.append(f"img/{filename}")
            files.append(line)
    return files

def draw_image(path: str):
    img = Image.open(path)
    img = img.convert("RGBA")
    img = img.resize((int(get_terminal_size().columns / POINT_WIDTH), get_terminal_size().lines - BLANK_LINES), Image.ANTIALIAS)

    for y in range(img.height):
        line = ""
        for x in range(img.width):
            r, g, b, _ = img.getpixel((x, y))
            if (r, g, b) == (0, 0, 0):
                line += " " * POINT_WIDTH
            else:
                line += f"[#ffffff on rgb({r},{g},{b})]{' ' * POINT_WIDTH}[/#ffffff on rgb({r},{g},{b})]"
        print(line)

def key_callback(e: KeyboardEvent):
    global x, y
    if e.event_type != KEY_UP:
        return
    if e.name == "up":
        if y > 0:
            y -= 1
    elif e.name == "down":
        if y < size[1]:
            y += 1
    elif e.name == "left":
        if x > 0:
            x -= 1
    elif e.name == "right":
        if x < size[1]:
            x += 1
    else:
        return
    try:
        draw_image(maps[y][x])
    except IndexError:
        ...

x = 0
y = 0
size = [0, 0]
maps: List[List[str]] = []

print("[yellow]GenshinMap 1.0 By shikukuya[/yellow]")
print("[blue]上下左右键移动，ctrl+c退出[/blue]")
sleep(1)
print("[red]正在下载地图[/red]")

if "img" not in listdir():
    mkdir("img")

maps = download_map(2)

draw_image(maps[y][x])
hook(key_callback)
wait()