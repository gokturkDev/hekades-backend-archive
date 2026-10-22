import logging
import re
from business.entity.source.source_chunk import SourceChunk

logger = logging.getLogger("hekades")


def consolidate_sources(sources: dict[str, list[SourceChunk]], answers: dict[str, str]) -> list[SourceChunk]:
    source_pattern = re.compile(r"\[([0-9, ]+)\]")
    curr_source_num = 1
    new_sources = []

    for tag, answer in answers.items():
        old_to_new_num_mapping = {}
        curr_answer = answer
        while True:
            match = source_pattern.search(curr_answer)
            if not match:
                break
            nums = match.group(0).replace("[", "").replace("]", "").split(",")
            new_nums = []
            for num in nums:
                if num not in old_to_new_num_mapping:
                    try:
                        chunk = sources[tag][int(num) - 1]
                    except IndexError:
                        logger.info(f"IndexError: {tag} {str(num)} \nIgnoring this source.")
                        continue
                    old_to_new_num_mapping[num] = str(curr_source_num)
                    new_nums.append(str(curr_source_num))

                    new_sources.append(chunk)
                    curr_source_num += 1
                else:
                    new_nums.append(old_to_new_num_mapping[num])

            curr_answer = curr_answer.replace(match.group(0), f"🍏{','.join(new_nums)}🍏")
        answers[tag] = curr_answer

    temp_source_pattern = re.compile(r"🍏([0-9, ]+)🍏")
    for tag, answer in answers.items():
        curr_answer = answer
        while True:
            match = temp_source_pattern.search(curr_answer)
            if not match:
                break
            nums = match.group(0).replace("🍏", "").replace("🍏", "").split(",")
            curr_answer = curr_answer.replace(match.group(0), f"[{",".join(nums)}]")

        curr_answer = curr_answer.replace("🍏", "")  # ensure no residue is left
        answers[tag] = curr_answer

    return new_sources
