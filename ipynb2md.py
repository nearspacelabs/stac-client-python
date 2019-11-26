import argparse
from pathlib import Path
import re
import os
import tempfile

# https://regex101.com/r/ezekzs/1
regex = r"\n\n( {4}[\w\S]+[\w\S ]*((\n {4}([\w \S]*))|(\n {4})){0,})\n"

# TODO this regex will fail if the ``` is not preceded by a newline
py_regex = r"```python\n((^(?!```).+\n)|([\n ]+)){1,}```"

replace_pairs = []

class FileExists(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        file_path = values
        if os.path.exists(file_path):
            setattr(namespace, self.dest, file_path)
        else:
            raise argparse.ArgumentTypeError("metadata:{0} is not a file".format(file_path))


def prepare_parser():
    arg_parser = argparse.ArgumentParser(description="Convert Jupyter Notebooks into Markdown with Collapseable code "
                                                     "blocks")
    arg_parser.add_argument("--all", "-a", type=str, help="process all ipynb")
    arg_parser.add_argument("--ipynb", "-i", type=str, default="README.ipynb", action=FileExists,
                            help="name of the input jupyter notebook")
    arg_parser.add_argument("--test", "-t", action="store_true", help="test markdown against previous results")

    return arg_parser


def markdowner(input_filename, markdown_filename, test=False):
    compare_all_text = ""
    if test:
        with open(markdown_filename, 'rt') as file_obj:
            compare_all_text = file_obj.read()

    # requires nbconvert
    os.system('jupyter nbconvert --to MARKDOWN --execute {0} --output {1} --ExecutePreprocessor.kernel_name=python3'
              .format(input_filename, markdown_filename))

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

    if test:
        with tempfile.NamedTemporaryFile(mode="w+", suffix=".md") as temp:
            temp.seek(0)
            temp.write(compare_all_text)
            temp.truncate()
            temp.flush()
            os.system('diff -B {0} {1}'.format(temp.name, m_markdown_filename))
            os.system('diff -B -q {0} {1}'.format(temp.name, m_markdown_filename))


if __name__ == "__main__":
    m_arg_parser = prepare_parser()
    m_args = m_arg_parser.parse_args()

    if m_args.all:
        for path_obj in Path(m_args.all).glob("./*.ipynb"):
            m_input_filename = str(path_obj.relative_to(m_args.all))
            m_markdown_filename = '{}.md'.format(os.path.splitext(m_input_filename)[0])
            test = False
            if m_args.test and os.path.exists(m_markdown_filename):
                test = True
            markdowner(input_filename=m_input_filename, markdown_filename=m_markdown_filename, test=test)
    else:
        m_markdown_filename = '{}.md'.format(os.path.splitext(m_args.ipynb)[0])
        test = False
        if m_args.test and os.path.exists(m_markdown_filename):
            test = True
        markdowner(input_filename=m_args.ipynb, markdown_filename=m_args.name, test=test)



