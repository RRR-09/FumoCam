import os
from time import sleep
from utilities import check_active
from config import RESOURCES_PATH
from traceback import format_exc

from mss import mss  # pip3.9 install mss
import numpy as np
import cv2 as cv
import pydirectinput


def filter_matches(kp1, kp2, matches, ratio=0.75):
    mkp1, mkp2 = [], []
    for m in matches:
        if len(m) == 2 and m[0].distance < m[1].distance * ratio:
            m = m[0]
            mkp1.append(kp1[m.queryIdx])
            mkp2.append(kp2[m.trainIdx])
    p1 = np.float32([kp.pt for kp in mkp1])
    p2 = np.float32([kp.pt for kp in mkp2])
    kp_pairs = zip(mkp1, mkp2)
    return p1, p2, list(kp_pairs)


def explore_match(win, img1, img2, kp_pairs, status=None, h=None):
    h1, w1 = img1.shape[:2]
    h2, w2 = img2.shape[:2]
    vis = np.zeros((max(h1, h2), w1 + w2), np.uint8)
    vis[:h1, :w1] = img1
    vis[:h2, w1:w1 + w2] = img2
    vis = cv.cvtColor(vis, cv.COLOR_GRAY2BGR)

    if h is not None:
        corners = np.float32([[0, 0], [w1, 0], [w1, h1], [0, h1]])
        corners = np.int32(cv.perspectiveTransform(corners.reshape(1, -1, 2), h).reshape(-1, 2) + (w1, 0))
        cv.polylines(vis, [corners], True, (255, 255, 255))

    if status is None:
        status = np.ones(len(kp_pairs), np.bool_)
    p1, p2 = [], []
    for kpp in kp_pairs:
        p1.append(np.int32(kpp[0].pt))
        p2.append(np.int32(np.array(kpp[1].pt) + [w1, 0]))

    green = (0, 255, 0)
    red = (0, 0, 255)
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            col = green
            cv.circle(vis, (x1, y1), 2, col, -1)
            cv.circle(vis, (x2, y2), 2, col, -1)
        else:
            col = red
            r = 2
            thickness = 3
            cv.line(vis, (x1 - r, y1 - r), (x1 + r, y1 + r), col, thickness)
            cv.line(vis, (x1 - r, y1 + r), (x1 + r, y1 - r), col, thickness)
            cv.line(vis, (x2 - r, y2 - r), (x2 + r, y2 + r), col, thickness)
            cv.line(vis, (x2 - r, y2 + r), (x2 + r, y2 - r), col, thickness)
    for (x1, y1), (x2, y2), inlier in zip(p1, p2, status):
        if inlier:
            cv.line(vis, (x1, y1), (x2, y2), green)
    return vis


def match_and_draw(img1_obj, img2_obj):
    raw_matches = cv.BFMatcher(cv.NORM_HAMMING).knnMatch(img1_obj["desc"], trainDescriptors=img2_obj["desc"], k=2)  # 2
    p1, p2, kp_pairs = filter_matches(img1_obj["kp"], img2_obj["kp"], raw_matches)
    if len(p1) >= 4:
        h, status = cv.findHomography(p1, p2, cv.RANSAC, 5.0)
        print(f"{np.sum(status)} / {len(status)} inliers")
        average_match = np.sum(status) / len(status)
    else:
        h, status = None, None
        print(f"Too few matches found ({len(p1)}), skipping homography estimation")
        average_match = 0

    vis = explore_match("Spawn point Match", img1_obj["img"], img2_obj["img"], kp_pairs, status, h)
    return vis, average_match


def get_screenshot():
    try:
        with mss() as sct:
            check_active()
            sleep(0.25)
            pydirectinput.press("tab")
            sleep(0.25)
            monitor = mss().monitors[0]
            left_cutoff = 175
            monitor["left"] += left_cutoff
            monitor["width"] -= left_cutoff
            print(monitor)
            return np.array(sct.grab(monitor))
    except Exception:
        print(f"Error with screenshot: {format_exc()}")
        return False


def main():
    vis = get_screenshot()
    if vis is False:
        return False
    font = cv.FONT_HERSHEY_COMPLEX_SMALL

    screenshot_img = cv.cvtColor(vis, cv.COLOR_BGRA2GRAY)
    img1_obj = {
        "img": screenshot_img
    }

    cv.putText(vis, "SCANNING CURRENT LOCATION", (0, 650), font, 2, (0, 255, 0), 3, cv.LINE_AA)
    cv.imshow("Spawn Detection", vis)
    cv.waitKey(1000)

    detector = cv.BRISK_create()
    img1_obj["kp"], img1_obj["desc"] = detector.detectAndCompute(img1_obj["img"], None)

    spawns = ["comedy_machine", "main", "tree_house"]
    current_best_match = {
        "label": "error",
        "confidence": 0
    }
    for spawn in spawns:
        lighting_matches = []
        for lighting_cycle in ["day", "night"]:
            features_path = os.path.join(RESOURCES_PATH, "spawns", spawn, lighting_cycle)
            confidence_scores = []
            for file_name in os.listdir(features_path):
                if not file_name.endswith(".png"):
                    continue
                print(file_name)
                image_path = os.path.join(features_path, file_name)
                img = cv.imread(image_path, cv.IMREAD_GRAYSCALE)
                img2_obj = {"img": img,
                            "kp": (detector.detectAndCompute(img, None))[0],
                            "desc": (detector.detectAndCompute(img, None))[1]}
                vis, average_match = match_and_draw(img1_obj, img2_obj)
                confidence_scores.append(average_match)
                average_match = round(average_match * 100, 2)

                feature_label = f"{spawn.capitalize()} ({lighting_cycle.capitalize()}) #{len(confidence_scores)}"
                match_label = f"Match: {average_match}%"
                print(feature_label, match_label)

                screen_width = 1920
                if vis.shape[1] > screen_width:
                    division_percent = vis.shape[1] / screen_width
                    new_height = int(vis.shape[0] / division_percent)
                    new_width = int(vis.shape[1] / division_percent)
                    new_dimensions = (new_width, new_height)
                    vis = cv.resize(vis, new_dimensions, interpolation=cv.INTER_AREA)
                vis = cv.putText(vis, feature_label, (0, 600), font, 2, (0, 255, 0), 2, cv.LINE_AA)
                vis = cv.putText(vis, match_label, (0, 650), font, 2, (0, 255, 0), 2, cv.LINE_AA)
                cv.imshow("Spawn Detection", vis)
                cv.waitKey(150)
            if len(confidence_scores) == 0:
                average_for_lighting = 0
            else:
                average_for_lighting = round((sum(confidence_scores) / len(confidence_scores)) * 100, 2)
            lighting_matches.append(average_for_lighting)
        best_confidence_for_spawn = max(lighting_matches)
        print(f"Confidence for {spawn}: {best_confidence_for_spawn}%\n")
        if best_confidence_for_spawn <= current_best_match["confidence"]:
            continue
        current_best_match = {
            "label": spawn,
            "confidence": best_confidence_for_spawn
        }
    final_match_label = f"{current_best_match['label'].capitalize()} with {current_best_match['confidence']}% confidence"
    print(f"Identified spawn as:\n{final_match_label}")

    vis = cv.cvtColor(img1_obj["img"], cv.COLOR_GRAY2BGR)
    cv.putText(vis, final_match_label, (0, 650), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2, cv.LINE_AA)
    cv.putText(vis, "Guessing location as:", (0, 600), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2, cv.LINE_AA)

    cv.imshow("Spawn Detection", vis)
    cv.waitKey(1000)
    sleep(1)
    check_active()
    sleep(0.25)
    pydirectinput.press("tab")
    cv.destroyAllWindows()


if __name__ == '__main__':
    main()
