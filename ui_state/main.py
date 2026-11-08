import argparse
import re
import typing as t
from pathlib import Path

import fc_excel


class MyArgs(argparse.Namespace):
    excel: str = ""
    input: str = ""
    output: str = ""


class StateTransmitDef(t.NamedTuple):
    mode: str
    m1: int
    m2: int
    m3: int
    m4: int
    state: str
    space1: str
    long_mode_m1: int
    long_mode_m2: int
    long_mode_m3: int
    long_mode_m4: int
    space2: str
    short_mode_m1: int
    short_mode_m2: int
    short_mode_m3: int
    short_mode_m4: int
    space3: str
    up_m1: int
    up_m2: int
    up_m3: int
    up_m4: int
    space4: str
    down_m1: int
    down_m2: int
    down_m3: int
    down_m4: int
    space5: str
    set_m1: int
    set_m2: int
    set_m3: int
    set_m4: int
    space6: str
    bz_stop_m1: int
    bz_stop_m2: int
    bz_stop_m3: int
    bz_stop_m4: int
    space7: str
    set_up_m1: int
    set_up_m2: int
    set_up_m3: int
    set_up_m4: int


def handle_args() -> MyArgs:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-e",
        dest="excel",
        help="excel filename",
        default="table.xlsx",
    )
    parser.add_argument(
        "-i",
        dest="input",
        help="UI state definitions",
        default="input/ui_state_def.c",
    )
    parser.add_argument(
        "-o",
        dest="output",
        help="UI state definitions",
        default="output/ui_state_def.c",
    )

    return parser.parse_args(namespace=MyArgs())


# 读取整个文件的内容于一个str
def read_file(file: Path) -> str:
    with file.open("r", encoding="utf-8") as f:
        return f.read()


# 在一个str中使用正则表达式进行匹配，返回第一个匹配的结果和其位置
def regex_match(pattern: str, string: str) -> tuple[str, int] | None:
    match = re.search(pattern, string, re.MULTILINE)
    if match:
        return match.group(), match.start()
    return None


def find_func_definition(file_content: str, func_name: str) -> tuple[str, int] | None:
    pattern = rf"^static ULONG {func_name}\("
    start: tuple[str, int] | None = regex_match(pattern, file_content)

    if start is None:
        return None

    end: tuple[str, int] | None = regex_match("^}\n", file_content[start[1] :])

    if end is None:
        return None

    return file_content[start[1] : start[1] + end[1] + 2], start[1]


def find_user_block(file_content: str, block: str) -> str:
    start_pattern = rf"^/\* USER CODE BEGIN {block} \*/"
    end_pattern = rf"^/\* USER CODE END {block} \*/"

    start: tuple[str, int] | None = regex_match(start_pattern, file_content)

    if start is None:
        return f"/* USER CODE BEGIN {block} */\n/* USER CODE END {block} */\n"

    end: tuple[str, int] | None = regex_match(end_pattern, file_content[start[1] :])

    if end is None:
        return ""

    return file_content[start[1] : start[1] + end[1] + len(block) + 21]


def generate_func_def(out: t.TextIO, func_name: str, file_content: str) -> None:
    func_def = find_func_definition(file_content, func_name)
    if func_def is None:
        out.write(
            f"static ULONG {func_name}(ULONG state)\n{{\n    return UI_STATE_NULL;\n}}\n\n"
        )
        return

    out.write(func_def[0])
    out.write("\n")


def generate_ui_state_def(excel: str, input: str, output: str) -> None:
    template = fc_excel.ExcelTemplate(excel)

    state_defs = fc_excel.create_named_tuple(
        StateTransmitDef, template.get_table("state_transmit_def", width=41)
    )

    input_content = read_file(Path(input))
    out: t.TextIO = open(Path(output), "w+", encoding="utf-8")

    out.write('#include "ui_state.h"\n\n')
    out.write(find_user_block(input_content, "Header"))
    out.write("\n")
    out.write(find_user_block(input_content, "Code"))
    out.write("\n")

    for i in range(0, 2):
        if i == 1:
            out.write("/* clang-format off */\n")
            out.write("const state_def_t ui_state_defs[] = {\n")

        for x in state_defs:
            long_mode_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.long_mode_m1}_{x.long_mode_m2}_{x.long_mode_m3}_{x.long_mode_m4}_by_long_mode"
            short_mode_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.short_mode_m1}_{x.short_mode_m2}_{x.short_mode_m3}_{x.short_mode_m4}_by_short_mode"
            up_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.up_m1}_{x.up_m2}_{x.up_m3}_{x.up_m4}_by_up"
            down_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.down_m1}_{x.down_m2}_{x.down_m3}_{x.down_m4}_by_down"
            set_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.set_m1}_{x.set_m2}_{x.set_m3}_{x.set_m4}_by_set"
            bz_stop_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.bz_stop_m1}_{x.bz_stop_m2}_{x.bz_stop_m3}_{x.bz_stop_m4}_by_bz_stop"
            set_up_func_name = f"_from__{x.m1}_{x.m2}_{x.m3}_{x.m4}__to__{x.set_up_m1}_{x.set_up_m2}_{x.set_up_m3}_{x.set_up_m4}_by_set_up"

            if i == 0:
                for func_name in [
                    long_mode_func_name,
                    short_mode_func_name,
                    up_func_name,
                    down_func_name,
                    set_func_name,
                    bz_stop_func_name,
                    set_up_func_name,
                ]:
                    generate_func_def(out, func_name, input_content)
            elif i == 1:
                out.write(f"    // {x.mode} -- {x.state}\n")
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_MODE_LONG, UI_STATE({x.long_mode_m1}, {x.long_mode_m2}, {x.long_mode_m3}, {x.long_mode_m4}), {long_mode_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_MODE_SHORT, UI_STATE({x.short_mode_m1}, {x.short_mode_m2}, {x.short_mode_m3}, {x.short_mode_m4}), {short_mode_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_UP, UI_STATE({x.up_m1}, {x.up_m2}, {x.up_m3}, {x.up_m4}), {up_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_DOWN, UI_STATE({x.down_m1}, {x.down_m2}, {x.down_m3}, {x.down_m4}), {down_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_SET, UI_STATE({x.set_m1}, {x.set_m2}, {x.set_m3}, {x.set_m4}), {set_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_BZ_STOP, UI_STATE({x.bz_stop_m1}, {x.bz_stop_m2}, {x.bz_stop_m3}, {x.bz_stop_m4}), {bz_stop_func_name} }},\n"
                )
                out.write(
                    f"    {{ UI_STATE({x.m1}, {x.m2}, {x.m3}, {x.m4}), KEY_SET_UP, UI_STATE({x.set_up_m1}, {x.set_up_m2}, {x.set_up_m3}, {x.set_up_m4}), {set_up_func_name} }},\n"
                )

        if i == 1:
            out.write("};\n")
            out.write("/* clang-format on */\n\n")
            out.write(f"const ULONG ui_state_defs_size = {len(state_defs) * 6};\n")


def main() -> None:
    args = handle_args()

    generate_ui_state_def(args.excel, args.input, args.output)


if __name__ == "__main__":
    main()
