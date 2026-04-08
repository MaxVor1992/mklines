from .resultobj import ParsingResult, SingleResult
import xlwt
import csv

colors = {
    "aqua": "#00ffff",
    "azure": "#f0ffff",
    "beige": "#f5f5dc",
    # "black": "#000000",
    "blue": "#0000ff",
    "brown": "#a52a2a",
    "cyan": "#00ffff",
    # "darkblue": "#00008b",
    "darkcyan": "#008b8b",
    "darkgrey": "#a9a9a9",
    # "darkgreen": "#006400",
    "darkkhaki": "#bdb76b",
    "darkmagenta": "#8b008b",
    # "darkolivegreen": "#556b2f",
    "darkorange": "#ff8c00",
    "darkorchid": "#9932cc",
    # "darkred": "#8b0000",
    "darksalmon": "#e9967a",
    "darkviolet": "#9400d3",
    "fuchsia": "#ff00ff",
    "gold": "#ffd700",
    "green": "#008000",
    # "indigo": "#4b0082",
    "khaki": "#f0e68c",
    "lightblue": "#add8e6",
    "lightcyan": "#e0ffff",
    "lightgreen": "#90ee90",
    "lightgrey": "#d3d3d3",
    "lightpink": "#ffb6c1",
    "lightyellow": "#ffffe0",
    "lime": "#00ff00",
    "magenta": "#ff00ff",
    "maroon": "#800000",
    # "navy": "#000080",
    "olive": "#808000",
    "orange": "#ffa500",
    "pink": "#ffc0cb",
    "purple": "#800080",
    "red": "#ff0000",
    "silver": "#c0c0c0",
    "white": "#ffffff",
    "yellow": "#ffff00"}

columns = ["#", "позиция", "url", "title", "request", "request position"]


def save_csv(res):
    file = open("results.csv", 'w')
    writer = csv.writer(file)
    writer.writerow(columns)
    inx = 1
    req_inx = 1

    for k in res.result:
        sp = res.result[k]
        inx_k = 1
        for item in sp:
            obj: SingleResult = item[0]
            position = int(item[1])
            tmp = [inx, position, obj.url, obj.title, k, req_inx]
            writer.writerow(tmp)
            inx += 1
            inx_k += 1
        req_inx += 1
    file.close()

def prepare_xls(res):
    d = {}.fromkeys(columns, [])
    inx = 1
    req_inx = 1
    for k in res.result:
        sp = res.result[k]
        inx_k = 1
        for item in sp:
            obj: SingleResult = item[0]
            position = int(item[1])
            d["#"].append(inx)
            d["позиция"].append(position)
            d["url"].append(obj.url)
            d["title"].append(obj.title)
            d["request"].append(k)
            d["request position"].append(req_inx)
            inx += 1
            inx_k += 1
        req_inx += 1
    return d

def save_xls(res: ParsingResult):
    print("test" * 100)
    print(res)
    print("test" * 100)
    book = xlwt.Workbook()
    sheet: xlwt.Worksheet = book.add_sheet("all")
    for i, s in enumerate(columns):
        sheet.write(0, i, s)
    inx = 1
    req_inx = 1
    for k in res.result:
        sp = res.result[k]
        sheet_k = book.add_sheet(f"{req_inx}")
        for i, s in enumerate(columns):
            sheet_k.write(0, i, s)

        inx_k = 1
        for item in sp:
            obj: SingleResult = item[0]
            position = int(item[1])
            sheet.write(inx, 0, position)
            sheet.write(inx, 1, obj.url)
            sheet.write(inx, 2, obj.title)
            sheet.write(inx, 3, k)
            sheet.write(inx, 4, req_inx)

            sheet_k.write(inx_k, 0, position)
            sheet_k.write(inx_k, 1, obj.url)
            sheet_k.write(inx_k, 2, obj.title)
            sheet_k.write(inx_k, 3, k)
            sheet_k.write(inx_k, 4, req_inx)
            inx += 1
            inx_k += 1
        req_inx += 1

    book.save("results.xls")

# res = {'окна': [(< resultobj.SingleResult object at 0x7f0a34ddef40 >, 1.0),
#                 (< resultobj.SingleResult object at 0x7f0a34ddefd0 >, 2.0),
#                 (< resultobj.SingleResult object at 0x7f0a34e168b0 >, 3.0),
#                 (< resultobj.SingleResult object at 0x7f0a34e161f0 >, 4.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de7190 >, 5.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de71f0 >, 6.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de7250 >, 7.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de72b0 >, 8.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de7310 >, 9.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de7370 >, 10.0),
#                 (< resultobj.SingleResult object at 0x7f0a34de73d0 >, 11.0)],
#        'пластиковые окна': [(< resultobj.SingleResult object at 0x7f0a34e715e0 >, 1.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e71400 >, 2.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e006a0 >, 3.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e00700 >, 4.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e00760 >, 5.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e007c0 >, 6.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e00820 >, 7.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e00880 >, 8.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e008e0 >, 9.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e00940 >, 10.0),
#                             (< resultobj.SingleResult object at 0x7f0a34e009a0 >, 11.0)],
#        'двери': [(< resultobj.SingleResult object at 0x7f0a34de7be0 >, 1.0),
#                  (< resultobj.SingleResult object at 0x7f0a34de7790 >, 2.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02880 >, 3.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e028e0 >, 4.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02940 >, 5.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e029a0 >, 6.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02a00 >, 7.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02a60 >, 8.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02ac0 >, 9.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02b20 >, 10.0),
#                  (< resultobj.SingleResult object at 0x7f0a34e02b80 >, 11.0)]}
