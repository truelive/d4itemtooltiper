# -*- coding: utf-8 -*- 
import cv2
import numpy as np
import keyboard
import pyautogui
import datetime
import pytesseract
import re
import yaml
import TimerWidget
import configparser
from yaml.loader import BaseLoader
from functools import reduce
from multiprocessing import Pool
from PIL import Image

class d4_item:
    def __init__(self, lang_config, item_text):
        self.item_text = item_text
        res = re.search(lang_config['Game.Items']['item_power_regex'], item_text)
        if res is None:
            raise RuntimeError("No ItemPower is parsed from {", item_text, "}")
        self.item_power = res.group(1)
        print("ITEM POWER ", self.item_power)
        item_header = res.string[0:res.start()]
        item_header_l = item_header.lower()
        flty = list(filter(lambda tp: all(word.lower() in item_header_l for word in tp.split()), item_types_list))
        print("CHOOSING ITEM TYPE", flty)
        self.item_type = reduce(lambda a, b: a if len(a) > len(b) else b, flty)
        print("ITEM TYPE ", self.item_type, "is weapon =", self.item_type in weapon_types_list)

        last_stat_index = item_text.find(lang_config['Game.Items']['properties_lost'])
        if last_stat_index < 0:
            last_stat_index = item_text.find(lang_config['Game.Items']['requires_level'])
        item_stats = res.string[res.end():last_stat_index]
        self.affx = []
        item_filter = lambda x: x['item'].lower() == self.item_type.lower() or is_weapon(x['item'], self.item_type)
        if any(item_filter(x) for x in build):
            print(f"using {next(filter(item_filter, build))['item']} because {self.item_type.lower()} is w={is_weapon(self.item_type, next(filter(item_filter, build))['item'])}")
            affixes = next(filter(item_filter, build))['affixes']
            for affix in affixes:
                t = re.search('(\d+)'+affix['type'], item_stats)
                if t is not None:
                    self.affx.append((True, affix['type'], t.group(1)))
                else:
                    self.affx.append((False, affix['type']))
                    print(f"Affix {affix['type']} is not found")
        else:
            print(f"can't find the '{self.item_type}' in the build")
        print("______________________")

    def __str__(self):
        return f"ilvl {self.item_power} {self.item_type} aff: {self.affx}"

def is_weapon(s1, s2):
    return s1 in weapon_types_list and s2 in weapon_types_list

def rescale(x):
    return int(x)

def tess_ocr(img_b):
    img, img_box, tess_par, tess_lang = img_b
    img = img.crop(img_box)
    img = img.resize((rescale(img.width), rescale(img.height)))
    #img.show()
    return pytesseract.image_to_string(img, config=tess_par, lang=tess_lang)

def recognize_item(config):
    try:
        start_time = datetime.datetime.now()
        #screenshot = pyautogui.screenshot()
        screenshot = Image.open(base_lang_path + '/sample.png')
        #screenshot.show()
        screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)
        comparing_bot, equipped_top = pool.map(find_image, [(screen, comparing_bot_image),(screen, equipped_top_image)])

        if equipped_top is None:
            print("top left  NON FOUND")
        else:
            print("top left ", equipped_top)
        if comparing_bot is None:
            print("bot right NON FOUND")
        else:
            print("bot right ",comparing_bot)
        screen_captured = datetime.datetime.now()
        diff = screen_captured - start_time
        print("Result--------", int(diff.total_seconds() * 1000))
        width = comparing_bot_image.shape[1]
        
        new_item_box = (comparing_bot[0], equipped_top[1]+equipped_top_image.shape[0], comparing_bot[0]+width, comparing_bot[1])
        eq_item_box = (equipped_top[0], equipped_top[1]+equipped_top_image.shape[0], equipped_top[0]+equipped_top_image.shape[1], comparing_bot[1]+comparing_bot_image.shape[0])
        #custom_config = r'--oem 3 --psm 6'
        tess_par = config['tesseract']['params']
        tess_lang = config['tesseract']['lang']
        item_texts = pool.map(tess_ocr, [(screenshot, eq_item_box, tess_par, tess_lang), (screenshot, new_item_box, tess_par, tess_lang)])
        new_item_text = item_texts[1]
        eq_item_text = item_texts[0]
        text_captured = datetime.datetime.now()
        diff = text_captured - screen_captured
        print("Result CV \n ", eq_item_text + "\n" + new_item_text, "\n--- OCR time--", int(diff.total_seconds() * 1000))
        # separate - since both images are recognized
        d4_items = [] 
        d4_items.append(d4_item(lang_constants, new_item_text))
        d4_items.append(d4_item(lang_constants, eq_item_text))
        # parse text into sensible stats 
        # evaluate against a build according to slot
        # show overlay window with autohide to show evaluation
        if d4_items is None:
            return
        print(map(str, d4_items))
        w = TimerWidget.TimerWidget(config)
        w.renderItems(d4_items, pyautogui.position())
        diff = datetime.datetime.now() - text_captured
        print(f"Window showed {int(diff.total_seconds() * 1000 - w.windowcheck_millis)}")
    except Exception as e:
        print(e)
    finally:
        return

def parse_item_text(text):
    items_ends = {}
    search_start = 0
    while text.find("Sell Value:", search_start) != -1:
        result = text.find("Sell Value:", search_start)
        items_ends[len(items_ends)] = result
        search_start = result+1
    item_array = []
    if (len(items_ends) == 1):
        print("ONLY ONE ITEM FOUND")
        item_array.append(d4_item(text[0:items_ends[0]]))
    elif (len(items_ends) == 2):
        print("TWO ITEMS FOUND")
        item_array.append(d4_item(text[0:items_ends[0]]))
        item_array.append(d4_item(text[items_ends[0]+1:items_ends[1]]))
    else:
        print(f"not supported amount of items = {len(items_ends)}")
        return None
    return item_array


def find_image(arg):
    source, temp = arg
    res = cv2.matchTemplate(source, temp, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    return max_loc

if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config/config.ini', 'UTF-8')
    language = config['DEFAULT']['lang']
    lang_constants = configparser.ConfigParser()
    base_lang_path = f'config/lang/{language}'
    lang_constants.read(base_lang_path + '/constants.ini', 'UTF-8')

    equipped_top_image = cv2.imread(base_lang_path + '/equipped.png', cv2.IMREAD_GRAYSCALE)
    comparing_bot_image = cv2.imread(base_lang_path + '/stash_comparing.png', cv2.IMREAD_GRAYSCALE)

    weapon_types_list = lang_constants['Game.Items']['weapon_names'].split(',')
    item_types_list = lang_constants['Game.Items']['item_names'].split(',') 
    item_types_list.extend(weapon_types_list)

    build = yaml.load(open(config['DEFAULT']['build_path'],'r', encoding='utf8'), Loader=BaseLoader)
    build = build['build']['items']
    print(build)
    pool = Pool(2)
    func = lambda : recognize_item(config)
    # func()
    #freeze_support()
    keyboard.add_hotkey(config['DEFAULT']['parse_key'], func)
    keyboard.wait(config['DEFAULT']['exit_key'])