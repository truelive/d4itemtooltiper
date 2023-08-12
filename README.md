# What is d4itemtooltiper
d4itemtooltiper - is a little program that shows a tooltip that lists affixes you are intrested in. 
At least for me it helps understand affixes at a glance.

This tool is accurate in most cases but still need some additional tuning.
# HOW TO START
- install python 3.8
- install tesseract from here https://github.com/tesseract-ocr/tesseract#installing-tesseract or https://tesseract-ocr.github.io/tessdoc/Installation.html
    - don't forget to select your desired language in data selection
    - you can add the tesseract installation directory to your PATH. To check that everything is working - `tesseract` command in your terminal should run succesfully
    - alternatively you can modify `tesseract_cmd` in `config.ini` to point at the tesseract itself
        - `tesseract_cmd = C:\Program Files\Tesseract-OCR\tesseract.exe`
- create you virtual env `python -m venv venv`
- activate it `venv\Scripts\activate`
- install requirements `pip install -r requirements.txt`
- run `python main.py`
- launch Diablo 4 (if not launched already)
- hover over an item and enable comparation
- hit `F1` and wait for a few seconds for window to appear to the left of your mouse cursor
    - you can hover over the window to close it immediately
- to exit the program hit `Shift+Esc`