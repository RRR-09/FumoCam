import os
from copy import copy
from pathlib import Path
from traceback import format_exc
from typing import Dict

import cv2 as cv
import numpy as np

from utilities import check_active, take_screenshot_binary_blocking


def apply_edge_filter(original_image: np.ndarray, edge_filter: Dict = {}) -> np.ndarray:
    # if we haven't been given a defined filter, use the filter values from the GUI
    if not edge_filter:
        edge_filter = {
            "kernelSize": 5,
            "erodeIter": 1,
            "dilateIter": 1,
            "canny1": 0,
            "canny2": 60,
        }

    kernel = np.ones((edge_filter["kernelSize"], edge_filter["kernelSize"]), np.uint8)
    eroded_image = cv.erode(original_image, kernel, iterations=edge_filter["erodeIter"])
    dilated_image = cv.dilate(
        eroded_image, kernel, iterations=edge_filter["dilateIter"]
    )

    # canny edge detection
    result = cv.Canny(dilated_image, edge_filter["canny1"], edge_filter["canny2"])
    # convert single channel image back to BGR
    img = cv.cvtColor(result, cv.COLOR_GRAY2BGR)

    return img


def get_screenshot():
    try:
        return np.array(take_screenshot_binary_blocking())
    except Exception:
        print(f"Error with screenshot: {format_exc()}")
        return False


def spawn_detection_main(
    resources_path: Path,
    slow: bool = True,
) -> str:
    font = cv.FONT_HERSHEY_COMPLEX_SMALL

    screenshot_img = get_screenshot()
    if screenshot_img is False:
        return "ERROR"
    vis = copy(screenshot_img)
    cv.putText(
        vis, "SCANNING CURRENT LOCATION", (0, 650), font, 2, (0, 255, 0), 3, cv.LINE_AA
    )
    if slow:
        cv.imshow("Spawn Detection", vis)
        cv.waitKey(1000)

    ui_mask = cv.imread(str(resources_path / "spawns" / "ui_mask.jpg"), 0)
    screenshot_img = cv.bitwise_and(screenshot_img, screenshot_img, mask=ui_mask)
    vis = copy(screenshot_img)
    if slow:
        cv.putText(
            vis,
            "SCANNING CURRENT LOCATION",
            (0, 650),
            font,
            2,
            (0, 255, 0),
            3,
            cv.LINE_AA,
        )
        cv.imshow("Spawn Detection", vis)
        cv.waitKey(250)

    edge = apply_edge_filter(screenshot_img)
    vis = copy(screenshot_img)
    vis = cv.cvtColor(vis, cv.COLOR_BGRA2BGR)
    if slow:
        for row_number, pixel_row in enumerate(edge):
            vis[row_number] = pixel_row
            cv.putText(
                vis,
                "SCANNING CURRENT LOCATION",
                (0, 650),
                font,
                2,
                (0, 255, 0),
                3,
                cv.LINE_AA,
            )
            if row_number % 10 == 0:
                cv.imshow("Spawn Detection", vis)
                cv.waitKey(1)
        cv.imshow("Spawn Detection", vis)
        cv.waitKey(250)
    screenshot_img = edge

    spawns = ["comedy_machine", "main", "tree_house"]
    best_match_label = "ERROR"
    best_match_confidence = 0
    for spawn in spawns:
        samples_path = os.path.join(resources_path, "spawns", spawn)
        confidence_scores = []
        for file_name in os.listdir(samples_path):
            if not file_name.endswith(".jpg"):
                continue
            image_path = os.path.join(samples_path, file_name)
            needle_img = cv.imread(image_path, cv.IMREAD_UNCHANGED)
            needle_img = cv.bitwise_and(needle_img, needle_img, mask=ui_mask)
            needle_img = apply_edge_filter(needle_img)

            needle_mask = cv.bitwise_not(needle_img) / 255
            difference = (screenshot_img * needle_mask).clip(0, 255).astype(np.uint8)

            vis = copy(screenshot_img)
            vis = cv.cvtColor(vis, cv.COLOR_BGRA2BGR)
            if slow:
                for row_number, pixel_row in enumerate(difference):
                    vis[row_number] = pixel_row
                    if row_number % 15 == 0:
                        cv.imshow("Spawn Detection", vis)
                        cv.waitKey(1)
            else:
                vis = difference

            original_sum = np.sum(screenshot_img > 0)
            difference_sum = np.sum(difference > 0)

            percentage = round(
                ((original_sum - difference_sum) / original_sum) * 100, 2
            )
            confidence_scores.append(percentage)
            friendly_name = file_name.rsplit(".", 1)[0].capitalize()
            feature_label = (
                f"{spawn.capitalize()} ({friendly_name}) #{len(confidence_scores)}"
            )
            match_label = f"Match: {percentage}%"
            print(feature_label, match_label)

            difference = cv.putText(
                difference, feature_label, (0, 600), font, 2, (0, 255, 0), 2, cv.LINE_AA
            )
            difference = cv.putText(
                difference, match_label, (0, 650), font, 2, (0, 255, 0), 2, cv.LINE_AA
            )
            if slow:
                cv.imshow("Spawn Detection", difference)
                cv.waitKey(150)

        best_confidence_for_spawn = max(confidence_scores)
        print(f"Confidence for {spawn}: {best_confidence_for_spawn}%\n")
        if best_confidence_for_spawn <= best_match_confidence:
            continue
        best_match_label = spawn
        best_match_confidence = best_confidence_for_spawn
    final_match_label = f"{best_match_label} with {best_match_confidence}% confidence"
    print(f"Identified spawn as:\n{final_match_label}")
    if slow:
        vis = copy(screenshot_img)
        cv.putText(
            vis,
            final_match_label,
            (0, 650),
            cv.FONT_HERSHEY_COMPLEX_SMALL,
            2,
            (0, 255, 0),
            2,
            cv.LINE_AA,
        )
        cv.putText(
            vis,
            "Guessing location as:",
            (0, 600),
            cv.FONT_HERSHEY_COMPLEX_SMALL,
            2,
            (0, 255, 0),
            2,
            cv.LINE_AA,
        )

        cv.imshow("Spawn Detection", vis)
        cv.waitKey(1000)
    cv.destroyAllWindows()
    return best_match_label


if __name__ == "__main__":
    import asyncio

    asyncio.get_event_loop().run_until_complete(check_active(force_fullscreen=False))
    # spawn_detection_main()
