import os
from time import sleep
from utilities import check_active
from config import RESOURCES_PATH
from traceback import format_exc
from copy import copy

from mss import mss  # pip3.9 install mss
import numpy as np
import cv2 as cv
import pydirectinput
import asyncio



def apply_edge_filter(original_image, edge_filter=None):
    print(original_image.shape)
    # if we haven't been given a defined filter, use the filter values from the GUI
    if not edge_filter:
        edge_filter = {
            "kernelSize":5,
            "erodeIter":1,
            "dilateIter":1, 
            "canny1":0,
            "canny2":60
        }

    kernel = np.ones((edge_filter["kernelSize"], edge_filter["kernelSize"]), np.uint8)
    eroded_image = cv.erode(original_image, kernel, iterations=edge_filter["erodeIter"])
    dilated_image = cv.dilate(eroded_image, kernel, iterations=edge_filter["dilateIter"])

    # canny edge detection
    result = cv.Canny(dilated_image, edge_filter["canny1"], edge_filter["canny2"])
    print(result.shape)
    # convert single channel image back to BGR
    img = cv.cvtColor(result, cv.COLOR_GRAY2BGR)
    print(img.shape)

    return img


def get_screenshot():
    try:
        with mss() as sct:
            #asyncio.get_event_loop().run_until_complete(check_active())
            #sleep(0.25)
            #pydirectinput.press("tab")
            #sleep(0.25)
            monitor = mss().monitors[0]
            #print(mss().monitors)
            #left_cutoff = 320
            #monitor["left"] += left_cutoff
            #monitor["width"] -= left_cutoff
            #bottom_cutoff = 90
            #monitor["top"] -= bottom_cutoff
            #monitor["height"] -= bottom_cutoff*2
            #monitor["left"] = int(monitor["left"]/2)
            #print(monitor)
            return np.array(sct.grab(monitor))
    except Exception:
        print(f"Error with screenshot: {format_exc()}")
        return False


def main():
    font = cv.FONT_HERSHEY_COMPLEX_SMALL
    
    screenshot_img = get_screenshot()
    if screenshot_img is False:
        return False
    vis = copy(screenshot_img)
    cv.putText(vis, "SCANNING CURRENT LOCATION", (0, 650), font, 2, (0, 255, 0), 3, cv.LINE_AA)
    cv.imshow("Spawn Detection", vis)
    cv.waitKey(1000)
    
    
    ui_mask = cv.imread(str(RESOURCES_PATH / "spawns" / "ui_mask.jpg"),0)
    screenshot_img = cv.bitwise_and(screenshot_img, screenshot_img, mask = ui_mask)
    vis = copy(screenshot_img)
    cv.putText(vis, "SCANNING CURRENT LOCATION", (0, 650), font, 2, (0, 255, 0), 3, cv.LINE_AA)
    cv.imshow("Spawn Detection", vis)
    cv.waitKey(250)
    
    edge = apply_edge_filter(screenshot_img)
    vis = copy(screenshot_img)
    vis = cv.cvtColor(vis, cv.COLOR_BGRA2BGR)
    for row_number,pixel_row in enumerate(edge):
        vis[row_number] = pixel_row
        cv.putText(vis, "SCANNING CURRENT LOCATION", (0, 650), font, 2, (0, 255, 0), 3, cv.LINE_AA)
        if row_number % 5 == 0:
            cv.imshow("Spawn Detection", vis)
            cv.waitKey(1)
    cv.imshow("Spawn Detection", vis)
    cv.waitKey(500)
    screenshot_img = edge
    
    spawns = ["comedy_machine", "main", "tree_house"]
    current_best_match = {
        "label": "error",
        "confidence": 0
    }
    for spawn in spawns:
        samples_path = os.path.join(RESOURCES_PATH, "spawns", spawn)
        confidence_scores = []
        for file_name in os.listdir(samples_path):
            if not file_name.endswith(".jpg"):
                continue
            print(file_name)
            image_path = os.path.join(samples_path, file_name)
            needle_img = cv.imread(image_path, cv.IMREAD_UNCHANGED)
            needle_img = cv.bitwise_and(needle_img, needle_img, mask = ui_mask)
            needle_img = apply_edge_filter(needle_img)

            #cv.imshow("Spawn Detection", needle_img)
            #cv.waitKey(200)
            
            needle_mask = cv.bitwise_not(needle_img) / 255
            difference = (screenshot_img * needle_mask).clip(0, 255).astype(np.uint8)
            
            
            
            vis = copy(screenshot_img)
            vis = cv.cvtColor(vis, cv.COLOR_BGRA2BGR)
            for row_number,pixel_row in enumerate(difference):
                vis[row_number] = pixel_row
                if row_number % 15 == 0:
                    cv.imshow("Spawn Detection", vis)
                    cv.waitKey(1)
            
            
            #cv.waitKey(200)
            
            original_sum = np.sum(screenshot_img > 0)
            difference_sum = np.sum(difference > 0)
            print(original_sum)
            print(difference_sum)
            
            percentage = round(((original_sum-difference_sum)/original_sum)*100, 2)
            confidence_scores.append(percentage)
            print("")

            feature_label = f"{spawn.capitalize()} ({file_name.rsplit('.',1)[0].capitalize()}) #{len(confidence_scores)}"
            match_label = f"Match: {percentage}%"
            print(feature_label, match_label)

            cv.imshow("Spawn Detection", difference)
            cv.waitKey(100)
            
            difference = cv.putText(difference, feature_label, (0, 600), font, 2, (0, 255, 0), 2, cv.LINE_AA)
            difference = cv.putText(difference, match_label, (0, 650), font, 2, (0, 255, 0), 2, cv.LINE_AA)
            cv.imshow("Spawn Detection", difference)
            cv.waitKey(300)
        
        best_confidence_for_spawn = max(confidence_scores)
        print(f"Confidence for {spawn}: {best_confidence_for_spawn}%\n")
        if best_confidence_for_spawn <= current_best_match["confidence"]:
            continue
        current_best_match = {
            "label": spawn,
            "confidence": best_confidence_for_spawn
        }
    final_match_label = f"{current_best_match['label'].capitalize()} with {current_best_match['confidence']}% confidence"
    print(f"Identified spawn as:\n{final_match_label}")

    vis = copy(screenshot_img)
    cv.putText(vis, final_match_label, (0, 650), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2, cv.LINE_AA)
    cv.putText(vis, "Guessing location as:", (0, 600), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 255, 0), 2, cv.LINE_AA)

    cv.imshow("Spawn Detection", vis)
    cv.waitKey(1000)
    cv.destroyAllWindows()
    return final_match_label


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(check_active())
    main()
