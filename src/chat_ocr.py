from asyncio import sleep as async_sleep
from datetime import datetime
from time import time

import cv2 as cv

# import mss.tools
import numpy as np
import pytesseract

from config import CFG
from utilities import check_active, take_screenshot_binary

pytesseract.pytesseract.tesseract_cmd = CFG.pytesseract_path


async def levenshtein(s, t, ratio_calc=False):
    s = s.lower().replace(" ", "")
    t = t.lower().replace(" ", "")
    # end customization
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows, cols), dtype=int)

    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0
            else:
                cost = 2 if ratio_calc else 1
            distance[row][col] = min(
                distance[row - 1][col] + 1,
                distance[row][col - 1] + 1,
                distance[row - 1][col - 1] + cost,
            )

    if ratio_calc:
        ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return ratio
    else:
        return distance[row][col]  # amount of edits away


async def do_chat_ocr(screenshot=None):
    CFG.chat_start_ocr_time = time()
    screenshot = await take_screenshot_binary(CFG.chat_dimensions)
    # Beep(100, 500)
    # mss.tools.to_png(screenshot.rgb, screenshot.size, output="test_cap.png")
    screenshot = np.array(screenshot)
    # cv.imwrite("test_cap.jpg", screenshot)

    scale = 3
    screenshot = cv.resize(
        screenshot, None, fx=scale, fy=scale, interpolation=cv.INTER_CUBIC
    )
    # cv.imshow("original", screenshot)
    # cv.waitKey(0)
    colors_to_replace = [
        {"name": "purple", "low": (150, 78, 58), "high": (158, 183, 139)},
        {"name": "green", "low": (46, 206, 128), "high": (48, 255, 218)},
    ]
    screenshot_hsv = cv.cvtColor(screenshot, cv.COLOR_RGB2HSV)
    for color_obj in colors_to_replace:
        color_threshold = cv.inRange(
            screenshot_hsv, color_obj["low"], color_obj["high"]
        )
        screenshot_hsv[color_threshold > 0] = (0, 0, 255)
        # cv.imshow(color_obj["name"], cv.cvtColor(screenshot_hsv, cv.COLOR_HSV2RGB))
        # cv.waitKey(0)

    color_threshold = cv.inRange(screenshot_hsv, (0, 0, 145), (180, 255, 255))
    screenshot_hsv[color_threshold > 0] = (0, 0, 255)
    screenshot_hsv[color_threshold <= 0] = (0, 0, 0)
    screenshot = cv.cvtColor(screenshot_hsv, cv.COLOR_HSV2RGB)
    # cv.imwrite("test_colors.jpg", screenshot)

    # screenshot = cv.resize(screenshot, None, fx=3, fy=3, interpolation=cv.INTER_CUBIC)
    img = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)  # PyTesseract
    _, img = cv.threshold(img, 150, 255, cv.THRESH_BINARY)
    img = cv.bitwise_not(img)
    # cv.imshow("thresh", img)
    # cv.waitKey(0)
    # kernel = np.ones((1, 1), np.uint8)
    # kernel_big = np.ones((2, 1), np.uint8)
    # img = cv.dilate(img, kernel_big, iterations=1)
    # img = cv.erode(img, kernel_big, iterations=1)

    ocr_data = pytesseract.image_to_data(
        img, config="--oem 1 --psm 6", output_type=pytesseract.Output.DICT
    )
    await process_ocr_data(ocr_data)
    # cv.imshow("final", img)
    # cv.waitKey(0)


async def process_ocr_data(ocr_data):
    lines = []
    line = []
    for word in ocr_data["text"]:
        if word.strip() == "":
            lines.append(" ".join(line))
            line = []
        else:
            line.append(word)

    messages = []
    last_clear = True
    for line_unstripped in lines:
        line = line_unstripped.strip()
        if line.strip() == "":
            last_clear = True
            continue
        author_confidence = 0 if not last_clear else 40
        found_likely_name_start = False
        found_likely_name_end = False

        potential_split = ":" in line
        if potential_split:
            author, message = line.split(":", 1)
            author_confidence += 30
        else:  # very low confidence
            first_chars_trimmed = line[2:]  # dont detect opening bracket by mistake
            for character in CFG.chat_bracket_like_chars_right:
                if character in first_chars_trimmed:
                    end_index = first_chars_trimmed.index(character) + 2
                    author, message = [line[:end_index], line[end_index:]]
                    found_likely_name_end = True
                    author_confidence += 5
                    break
            if not found_likely_name_end:
                print("giveup1")
                if len(messages) > 0:
                    messages[-1]["message"] += f" {line}"
                last_clear = False
                continue  # give up

        # first 2 chars
        for pos, character in enumerate(author[:2]):
            if character in CFG.chat_bracket_like_chars_left:
                found_likely_name_start = True
                author = author[pos + 1 :]  # cutoff where we found it
                author_confidence += 20 if pos == 0 else 10
                break

        if not found_likely_name_start and found_likely_name_end:
            # if we couldnt find ":", finding "]" was a stretch, and we cant find "[" in the first 2,
            # its probably a continuation of the previous message
            if len(messages) > 0:
                messages[-1]["message"] += f" {line}"
            last_clear = False
            print("giveup2")
            print(line)
            continue  # give up

        if not found_likely_name_end:
            # last 2 chars, reverse order
            for pos, character in enumerate(author[-2:][::-1]):
                if character in CFG.chat_bracket_like_chars_right:
                    found_likely_name_end = True
                    author = author[: ((pos + 1) * -1)]  # cutoff where we found it
                    author_confidence += 20 if pos == 0 else 10
                    break

        if (
            potential_split
            and found_likely_name_start
            and found_likely_name_end
            and author_confidence < 100
        ):
            author_confidence += 30
        if author_confidence < 50:  # likely a continuation of the message
            if len(messages) > 0:
                messages[-1]["message"] += f" {line}"
            print("giveup3")
            print(line)
        else:
            messages.append(
                {
                    "author": author,
                    "author_confidence": author_confidence,
                    "message": message.strip(),
                }
            )

        last_clear = False

    await log_processed_messages(messages)


async def log_processed_messages(messages):
    linked_to_past_messages = False
    if len(CFG.chat_messages_in_memory) != 0:
        last_messages = CFG.chat_messages_in_memory[-8:]
        matches = {}
        proc_time_start = time()
        for new_index, new_msg in enumerate(messages):
            for old_index, old_msg in last_messages:
                if old_index in matches:
                    continue
                if (
                    new_msg["message"] == old_msg["message"]
                    and new_msg["author"] == old_msg["author"]
                ):
                    matches[old_index] = new_index
                    break
                else:
                    message_ratio = levenshtein(new_msg["message"], old_msg["message"])
                    author_ratio = levenshtein(new_msg["author"], old_msg["author"])
                    if (
                        message_ratio > CFG.chat_fuzzy_threshold
                        and author_ratio > CFG.chat_fuzzy_threshold
                    ):
                        matches[old_index] = new_index
                        break

        proc_time_end = time()
        print(f"Time for lookup: {proc_time_end-proc_time_start}")

        if len(matches) >= 3:
            linked_to_past_messages = True
            last_known_message_index = sorted(matches.items())[-1][0]
            last_known_time = float(last_messages[last_known_message_index]["time"])
            indexes_to_remove = list(matches.values())
            new_messages = []
            for index, message in enumerate(messages):
                if index not in indexes_to_remove:
                    new_messages.append(message)
            if len(new_messages) == 0:
                return  # no new messages have been found

            # equally distribute times between known messages
            for index, _ in enumerate(new_messages):
                if index == 0:
                    new_messages[index]["time"] = last_known_time
                    friendly_time = datetime.fromtimestamp(last_known_time).strftime(
                        "%Y-%m-%d %I:%M:%S%p"
                    )
                    new_messages[index]["time_friendly"] = friendly_time
                    continue
                subtr = CFG.chat_start_ocr_time - last_known_time
                percentage = index / (len(new_messages) - 1)
                estimated_time = last_known_time + (subtr * percentage)
                new_messages[index]["time"] = estimated_time
                friendly_time = datetime.fromtimestamp(estimated_time).strftime(
                    "%Y-%m-%d %I:%M:%S%p"
                )
                new_messages[index]["time_friendly"] = friendly_time
            # for i in new_messages:
            #     print(i)
            CFG.chat_messages_in_memory += new_messages
            await insert_messages_to_db(new_messages)

    if len(CFG.chat_messages_in_memory) == 0 or not linked_to_past_messages:
        messages_with_times = []
        # We're certain of one time, fake the rest
        for index, message in enumerate(messages[::-1]):
            message_obj = message
            message_obj["time"] = CFG.chat_start_ocr_time - index

            friendly_time = datetime.fromtimestamp(message_obj["time"]).strftime(
                "%Y-%m-%d %I:%M:%S%p"
            )
            message_obj["time_friendly"] = friendly_time
            messages_with_times.append(message_obj)
        messages_with_times = messages_with_times[::-1]
        for i in messages_with_times:
            print(i)
        CFG.chat_messages_in_memory += messages_with_times
        await insert_messages_to_db(messages_with_times)


async def insert_messages_to_db(messages):
    message_sets = []
    for msg in messages:
        message_set = (
            msg["time"],
            msg["time_friendly"],
            msg["author"],
            msg["message"],
            msg["author_confidence"],
        )
        message_sets.append(message_set)

    CFG.chat_db_cursor.executemany(
        "INSERT INTO messages VALUES(?,?,?,?,?);", message_sets
    )
    CFG.chat_db.commit()


if __name__ == "__main__":
    import asyncio

    async def test():
        await check_active(force_fullscreen=False)
        await async_sleep(2)
        await do_chat_ocr()

    asyncio.get_event_loop().run_until_complete(test())
