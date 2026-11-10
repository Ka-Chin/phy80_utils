import argparse
import re
import typing as t
from pathlib import Path

import fc_excel


class MyArgs(argparse.Namespace):
    excel: str = ""
    input: str = ""
    output: str = ""


class State(t.NamedTuple):
    m1: int
    m2: int
    m3: int
    m4: int


class StateTransmit(t.NamedTuple):
    key: str
    next_state: State


class StateTransmitDef(t.NamedTuple):
    mode: str
    state: str
    current: State

    transmits: list[StateTransmit]


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


def read_file(file: Path) -> str:
    with file.open("r", encoding="utf-8") as f:
        return f.read()


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


def func_name(current: State, transmit: StateTransmit) -> str:
    return (
        f"__from__"
        + f"{current.m1}_{current.m2}_{current.m3}_{current.m4}"
        + "__to__"
        + f"{transmit.next_state.m1}_{transmit.next_state.m2}_{transmit.next_state.m3}_{transmit.next_state.m4}"
        + f"__by_{transmit.key}"
    )


def generate_func_def(out: t.TextIO, func_name: str, file_content: str) -> None:
    func_def = find_func_definition(file_content, func_name)
    if func_def is None:
        out.write(
            f"static ULONG {func_name}(ULONG state)\n{{\n    return UI_STATE_NULL;\n}}\n\n"
        )
        return

    out.write(func_def[0])
    out.write("\n")


def generate_trans(current: State, trans: StateTransmit) -> str:
    return (
        f"{{ UI_STATE({current.m1}, {current.m2}, {current.m3}, {current.m4}), "
        + f"KEY_MODE_LONG, "
        + f"UI_STATE({trans.next_state.m1}, {trans.next_state.m2}, {trans.next_state.m3}, {trans.next_state.m4}), {func_name(current, trans)} }},\n"
    )


def parse_excel(excel: str) -> list[StateTransmitDef]:
    class StateTransmitRaw(t.NamedTuple):
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

    template = fc_excel.ExcelTemplate(excel)

    data = fc_excel.create_named_tuple(
        StateTransmitRaw, template.get_table("state_transmit_def", width=41)
    )

    defs: list[StateTransmitDef] = []

    for x in data:
        defs.append(
            StateTransmitDef(
                x.mode,
                x.state,
                State(x.m1, x.m2, x.m3, x.m4),
                [
                    StateTransmit(
                        "long_mode",
                        State(
                            x.long_mode_m1,
                            x.long_mode_m2,
                            x.long_mode_m3,
                            x.long_mode_m4,
                        ),
                    ),
                    StateTransmit(
                        "short_mode",
                        State(
                            x.short_mode_m1,
                            x.short_mode_m2,
                            x.short_mode_m3,
                            x.short_mode_m4,
                        ),
                    ),
                    StateTransmit("up", State(x.up_m1, x.up_m2, x.up_m3, x.up_m4)),
                    StateTransmit(
                        "down", State(x.down_m1, x.down_m2, x.down_m3, x.down_m4)
                    ),
                    StateTransmit("set", State(x.set_m1, x.set_m2, x.set_m3, x.set_m4)),
                    StateTransmit(
                        "bz_stop",
                        State(x.bz_stop_m1, x.bz_stop_m2, x.bz_stop_m3, x.bz_stop_m4),
                    ),
                    StateTransmit(
                        "set_up",
                        State(x.set_up_m1, x.set_up_m2, x.set_up_m3, x.set_up_m4),
                    ),
                ],
            )
        )

    return defs


def generate_ui_state_def(excel: str, input: str, output: str) -> None:
    defs = parse_excel(excel)

    input_content = read_file(Path(input))
    out: t.TextIO = open(Path(output), "w+", encoding="utf-8")

    out.write('#include "ui_state.h"\n\n')
    out.write(find_user_block(input_content, "Header"))
    out.write("\n")
    out.write(find_user_block(input_content, "Code"))
    out.write("\n")

    for x in defs:
        for y in x.transmits:
            generate_func_def(out, func_name(x.current, y), input_content)

    out.write("/* clang-format off */\n")
    out.write("const state_def_t ui_state_defs[] = {\n")

    for x in defs:
        out.write(f"    // {x.mode} -- {x.state}\n")
        for y in x.transmits:
            out.write("    " + generate_trans(x.current, y))

    out.write("};\n")
    out.write("/* clang-format on */\n\n")
    out.write(f"const ULONG ui_state_defs_size = {len(defs) * 7};\n")


def main() -> None:
    args = handle_args()

    generate_ui_state_def(args.excel, args.input, args.output)


if __name__ == "__main__":
    main()
