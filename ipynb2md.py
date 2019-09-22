import sys
import re
import os

# https://regex101.com/r/ezekzs/1
regex = r"\n\n( {4}[\w\S]+[\w\S ]*((\n {4}([\w \S]*))|(\n {4})){0,})\n"

# TODO this regex will fail if the ``` is not preceded by a newline
py_regex = r"```python\n((^(?!```).+\n)|([\n ]+)){1,}```"


if __name__ == "__main__":
    input_filename = 'README.ipynb'
    if len(sys.argv) >= 2:
        input_filename = sys.argv[1]

    if len(sys.argv) == 3:
        markdown_filename = sys.argv[2]
    else:
        markdown_filename = '{}.md'.format(os.path.splitext(input_filename)[0])

    # requires nbconvert
    os.system('jupyter nbconvert --to MARKDOWN --execute {0} --output {1} --ExecutePreprocessor.kernel_name=python3'.format(input_filename, markdown_filename))
    with open(markdown_filename, 'r+') as f:
        print("code collapse section re-write for file {}".format(markdown_filename))

        all_text = f.read()

        matches = re.finditer(regex, all_text, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            temp = "\n\n\n<details><summary>Python Print-out</summary>\n\n\n```text\n{}\n```\n\n\n</details>\n\n".format(
                match.group(1))
            all_text = all_text.replace(match.group(0), temp)

        matches = re.finditer(py_regex, all_text, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            temp = "\n\n\n<details><summary>Python Code Sample</summary>\n\n\n{}\n\n\n</details>\n\n".format(
                match.group(0))
            all_text = all_text.replace(match.group(0), temp)

        f.seek(0)
        f.write(all_text)
        f.truncate()
