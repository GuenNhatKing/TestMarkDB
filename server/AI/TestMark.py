"""
test_omr_rotate4_final.py
- quay đủ 4 góc: 0, 90, 180, 270 -> góc nào cũng lưu ra out/angle_xxx/
- SBD: 10 hàng x 6 cột
- Mã đề: 10 hàng x 3 cột
- Đáp án: theo hàng, cứ 4 ô = 1 câu
"""

import cv2, os, re, shutil, numpy as np
from ultralytics import YOLO

# ===== CẤU HÌNH =====
REGION_MODEL = "best/regions/best.pt"
BUBBLE_MODEL = "best/bubbles/best.pt"

CLASSES = {0: "Answer_region", 1: "MaDe_region", 2: "SBD_region"}

OUT_DIR   = "out"
ROW_Y_TOL = 18
MAX_COLS_ANSWER = 4

VERBOSE = True
def vprint(*args, **kwargs):
    if VERBOSE: print(*args, **kwargs)

region_model = YOLO(REGION_MODEL)
bubble_model = YOLO(BUBBLE_MODEL)

# ===== TIỆN ÍCH FILE =====
def clear_output_dir(path="out"):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception:
            for root, dirs, files in os.walk(path, topdown=False):
                for f in files:
                    try: os.remove(os.path.join(root, f))
                    except: pass
                for d in dirs:
                    try: os.rmdir(os.path.join(root, d))
                    except: pass
            try: os.rmdir(path)
            except: pass
    os.makedirs(path, exist_ok=True)

# ===== XOAY =====
def rotate_by_90(img, k):
    k = k % 4
    if k == 0:
        return img
    elif k == 1:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif k == 2:
        return cv2.rotate(img, cv2.ROTATE_180)
    else:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)

# ===== BUBBLE BASE =====
def detect_bubbles(img, conf=0.5):
    res = bubble_model(img, conf=conf, verbose=False)[0]
    arr = []
    if res.boxes is None:
        return arr
    for box, cls in zip(res.boxes.xyxy, res.boxes.cls):
        x1, y1, x2, y2 = map(int, box.tolist())
        arr.append({
            "box": (x1, y1, x2, y2),
            "center": ((x1 + x2)//2, (y1 + y2)//2),
            "class": "filled" if int(cls) == 0 else "unfilled"
        })
    return arr

def filter_normal_bubbles(bubbles, scale_low=0.5, scale_high=1.8):
    # dùng để loại ô đen to khác thường
    if not bubbles:
        return []
    areas = [ (b["box"][2]-b["box"][0])*(b["box"][3]-b["box"][1]) for b in bubbles ]
    med = np.median(areas)
    good = []
    for b in bubbles:
        area = (b["box"][2]-b["box"][0])*(b["box"][3]-b["box"][1])
        if med*scale_low <= area <= med*scale_high:
            good.append(b)
    return good if good else bubbles

def group_by_axis(items, axis="y", tol=15):
    # gom theo Y (hàng) hoặc X (cột)
    if not items:
        return []
    key = 1 if axis == "y" else 0
    items = sorted(items, key=lambda b: b["center"][key])
    groups = []
    cur = [items[0]]
    for b in items[1:]:
        if abs(b["center"][key] - cur[-1]["center"][key]) <= tol:
            cur.append(b)
        else:
            groups.append(cur)
            cur = [b]
    groups.append(cur)
    return groups

# ====== ĐỌC SBD: 10 hàng x 6 cột ======
def read_sbd_10x6(crop):
    bubbles = detect_bubbles(crop, conf=0.5)
    if len(bubbles) < 5:
        bubbles = detect_bubbles(crop, conf=0.35)
    if not bubbles:
        return "-"

    bubbles = filter_normal_bubbles(bubbles)
    # gom theo cột
    cols = group_by_axis(bubbles, axis="x", tol=25)
    # sort trái sang phải
    cols = sorted(cols, key=lambda c: np.mean([b["center"][0] for b in c]))
    digits = []
    for col in cols[:6]:   # chỉ 6 cột thôi
        col = sorted(col, key=lambda b: b["center"][1])  # trên xuống
        # tìm dòng nào tô
        filled_rows = [i for i, b in enumerate(col) if b["class"] == "filled"]
        if len(filled_rows) == 1:
            digits.append(str(filled_rows[0]))
        elif len(filled_rows) > 1:
            # tô 2 dòng trong 1 cột -> ghép lại
            digits.append("".join(str(x) for x in filled_rows))
        else:
            digits.append("-")
    return "".join(digits)

# ====== ĐỌC MÃ ĐỀ: 10 hàng x 3 cột ======
def read_made_10x3(crop):
    bubbles = detect_bubbles(crop, conf=0.5)
    if len(bubbles) < 3:
        bubbles = detect_bubbles(crop, conf=0.35)
    if not bubbles:
        return "-"

    bubbles = filter_normal_bubbles(bubbles)
    cols = group_by_axis(bubbles, axis="x", tol=25)
    cols = sorted(cols, key=lambda c: np.mean([b["center"][0] for b in c]))
    digits = []
    for col in cols[:3]:
        col = sorted(col, key=lambda b: b["center"][1])
        filled_rows = [i for i, b in enumerate(col) if b["class"] == "filled"]
        if len(filled_rows) == 1:
            digits.append(str(filled_rows[0]))
        elif len(filled_rows) > 1:
            digits.append("".join(str(x) for x in filled_rows))
        else:
            digits.append("-")
    return "".join(digits)

# ====== ĐÁP ÁN: theo hàng, 4 ô = 1 câu ======
def group_rows_by_y(bubbles, tol=18):
    if not bubbles:
        return []
    bubbles = sorted(bubbles, key=lambda b: b["center"][1])
    rows, cur = [], [bubbles[0]]
    for b in bubbles[1:]:
        if abs(b["center"][1] - cur[-1]["center"][1]) <= tol:
            cur.append(b)
        else:
            rows.append(cur)
            cur = [b]
    rows.append(cur)
    return rows

def bubbles_row_to_chunks_exact(row, max_cols=4):
    row = sorted(row, key=lambda b: b["center"][0])
    n_full = len(row) // max_cols
    chunks = []
    for i in range(n_full):
        chunks.append(row[i*max_cols:(i+1)*max_cols])
    return chunks

def chunk_to_answer(chunk):
    letters = "ABCD"
    filled = []
    for i, b in enumerate(chunk):
        if b["class"] == "filled":
            filled.append(letters[i])
    if not filled:
        return "-"
    if len(filled) == 1:
        return filled[0]
    return ",".join(filled)

def is_valid_sbd(s): return bool(re.fullmatch(r"\d{6}", s or ""))
def is_valid_made(s): return bool(re.fullmatch(r"\d{3}", s or ""))

class No_Le_AI:
    def __init__(self):
        pass

    def image_process(self, image_path):
        clear_output_dir(OUT_DIR) 

        img0 = cv2.imread(image_path)
        if img0 is None:
            raise FileNotFoundError(f"Không tìm thấy ảnh: {image_path}")

        angle_infos = []
        best_info = None  # để lưu góc tốt nhất hiện tại

        # quay đủ 4 góc, nhưng sẽ dừng sớm nếu gặp góc đạt score=3
        for k in range(4):
            angle = (k * 90) % 360
            img_rot = rotate_by_90(img0, k)

            angle_dir = os.path.join(OUT_DIR, f"angle_{angle:03d}")
            os.makedirs(angle_dir, exist_ok=True)
            cv2.imwrite(os.path.join(angle_dir, "full.jpg"), img_rot)

            det = region_model(img_rot, verbose=False)[0]
            H, W = img_rot.shape[:2]
            regions = {}
            for box, cls in zip(det.boxes.xyxy, det.boxes.cls):
                x1, y1, x2, y2 = map(int, box.tolist())
                name = CLASSES.get(int(cls), f"class_{int(cls)}")
                pad = 4
                x1 = max(0, x1 - pad); y1 = max(0, y1 - pad)
                x2 = min(W, x2 + pad); y2 = min(H, y2 + pad)
                crop = img_rot[y1:y2, x1:x2]
                regions.setdefault(name, []).append({"crop": crop, "box": (x1, y1, x2, y2)})

            def first_by_top(vlist):
                if not vlist: return None
                return sorted(vlist, key=lambda e: e["box"][1])[0]

            sbd_ent  = first_by_top(regions.get("SBD_region", []))
            made_ent = first_by_top(regions.get("MaDe_region", []))

            sbd_txt  = read_sbd_10x6(sbd_ent["crop"]) if sbd_ent else "-"
            made_txt = read_made_10x3(made_ent["crop"]) if made_ent else "-"

            # lưu crop để xem
            if sbd_ent:
                cv2.imwrite(os.path.join(angle_dir, "SBD_crop.jpg"), sbd_ent["crop"])
            if made_ent:
                cv2.imwrite(os.path.join(angle_dir, "MaDe_crop.jpg"), made_ent["crop"])
            if "Answer_region" in regions:
                for i, ent in enumerate(regions["Answer_region"], 1):
                    cv2.imwrite(os.path.join(angle_dir, f"Answer_region_{i}.jpg"), ent["crop"])

            # check trái -> phải
            left_to_right = None
            if sbd_ent and made_ent:
                sbd_cx = (sbd_ent["box"][0] + sbd_ent["box"][2]) // 2
                made_cx = (made_ent["box"][0] + made_ent["box"][2]) // 2
                left_to_right = (sbd_cx < made_cx)

            # chấm điểm
            if is_valid_sbd(sbd_txt) and is_valid_made(made_txt) and (left_to_right is True):
                score = 3
            elif is_valid_sbd(sbd_txt) and (left_to_right is True):
                score = 2
            elif is_valid_sbd(sbd_txt):
                score = 1
            else:
                score = 0

            info = {
                "angle": angle,
                "img": img_rot,
                "regions": regions,
                "sbd": sbd_txt,
                "made": made_txt,
                "left_to_right": left_to_right,
                "score": score,
                "dir": angle_dir,
            }
            angle_infos.append(info)

            # cập nhật best hiện tại
            if (best_info is None) or (score > best_info["score"]):
                best_info = info

            # nếu đã đạt điều kiện tối đa thì dừng luôn
            if score == 3:
                vprint(f"[INFO] Góc {angle}° -> ok")
                break

        # nếu không break sớm thì best_info vẫn là góc tốt nhất trong những góc đã thử
        best = best_info
        print(f"[INFO] Chọn góc {best['angle']}° | score={best['score']} | SBD={best['sbd']} | MaDe={best['made']} | L→R={best['left_to_right']}")

        final_sbd  = best["sbd"] if is_valid_sbd(best["sbd"]) else "-"
        final_made = best["made"] if is_valid_made(best["made"]) else "-"
        regions    = best["regions"]
        angle_dir  = best["dir"]

        # đọc đáp án
        all_answers = {}
        if "Answer_region" in regions:
            regions["Answer_region"].sort(key=lambda e: e["box"][1])
            # Lấy kích thước các vùng
            box_sizes = []
            for idx, ent in enumerate(regions["Answer_region"], 1):
                crop = ent["crop"]
                bubbles = detect_bubbles(crop, conf=0.5)
                if len(bubbles) < 4:
                    bubbles = detect_bubbles(crop, conf=0.35)
                bubbles = filter_normal_bubbles(bubbles)
                rows = group_rows_by_y(bubbles, tol=ROW_Y_TOL)
                for row in rows:
                    chunks = bubbles_row_to_chunks_exact(row, max_cols=MAX_COLS_ANSWER)
                    box_sizes.append((len(rows), len(chunks)))
                    break
                    
            ans_size = 0
            for r, c in box_sizes:
                ans_size += r * c

            gnk_answers = [0] * ans_size
            print("Answers SIZE: ", ans_size)

            for idx, ent in enumerate(regions["Answer_region"], 1):
                q_counter = 1
                crop = ent["crop"]
                bubbles = detect_bubbles(crop, conf=0.5)
                if len(bubbles) < 4:
                    bubbles = detect_bubbles(crop, conf=0.35)
                bubbles = filter_normal_bubbles(bubbles)

                rows = group_rows_by_y(bubbles, tol=ROW_Y_TOL)
                debug = crop.copy()
                for row in rows:
                    chunks = bubbles_row_to_chunks_exact(row, max_cols=MAX_COLS_ANSWER)
                    row_size = len(rows)
                    col_size = len(chunks)
                    for chunk in chunks:
                        ans = chunk_to_answer(chunk)
                        all_answers[f"Q{q_counter}"] = ans
                        x = (q_counter - 1) // col_size
                        y = (q_counter - 1) % col_size
                        ans_key = y * row_size + x
                        if idx > 1:
                            ans_key += box_sizes[idx - 2][0] * box_sizes[idx - 2][1]
                        q_counter +=1
                        cnt = 0
                        for b in chunk:
                            x1, y1, x2, y2 = b["box"]
                            cnt += 1
                            color = (0, 0, 255) if b["class"] == "filled" else (0, 255, 0)
                            if b["class"] == "filled":
                                if ans_key < ans_size:
                                    gnk_answers[ans_key] = cnt
                            cv2.rectangle(debug, (x1, y1), (x2, y2), color, 2)

                cv2.imwrite(os.path.join(angle_dir, f"answer_region_{idx}_debug.jpg"), debug)

        return gnk_answers
    
    def print_answers(self, answers):
        print(f"Đáp án ({len(answers)} câu):")
        for i in range(len(answers)):
            if answers[i] == 0:
                print("Q" + str(i + 1) + ". " + "?")
            else:
                print("Q" + str(i + 1) + ". " + chr(ord('A') + answers[i] - 1))