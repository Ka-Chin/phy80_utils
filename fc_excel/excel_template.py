from __future__ import annotations

import collections.abc as c
import re
import typing as t

import openpyxl as xl
import openpyxl.styles as styles
import openpyxl.utils as utils
from openpyxl.cell.cell import Cell
from openpyxl.comments import Comment
from openpyxl.styles.borders import Border, Side
from openpyxl.workbook.defined_name import DefinedNameDict
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet


class CellPos(t.NamedTuple):
    name: str
    row_delta: int
    col_delta: int

    @classmethod
    def simple(cls, name: str) -> CellPos:
        return CellPos(name, 0, 0)

    @classmethod
    def extend(cls, base: CellPos | str, row_delta: int, col_delta: int) -> CellPos:
        match (base):
            case CellPos():
                return CellPos(
                    base.name, base.row_delta + row_delta, base.col_delta + col_delta
                )
            case _:
                return CellPos(base, row_delta, col_delta)

    @t.override
    def __str__(self) -> str:
        return f"--Cell {self.name}, {self.row_delta}, {self.col_delta}--"


CellValue = float | int | str | None
NamePos = str | CellPos
CellStyle = dict[str, t.Any]


def filter_out_none_xml_char(text: str):
    return re.sub(
        "[^\u0020-\ud7ff\u0009\u000a\u000d\ue000-\ufffd\U00010000-\U0010ffff]+",
        "",
        text,
    )


class ExcelTemplate:
    def __init__(self, template: str) -> None:
        self.template: str = template
        self.wb: Workbook = xl.load_workbook(template)
        self.ws: Worksheet | None = None

        self.thin_border: Border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        self.t_origin: Cell | None = None
        self.t_cell: Cell | None = None
        self.t_width: int = 0
        self.t_ws: Worksheet | None = None

    def style(self, name_pos: NamePos, style: CellStyle) -> None:
        self.style_cell(self.cell(name_pos), style)

    def style_cell(self, cell: Cell, style: CellStyle) -> None:
        if "bg" in style:
            cell.fill = styles.fills.PatternFill(
                "solid", start_color=t.cast(str, style["bg"])
            )

        if "halign" in style or "valign" in style or "wrap" in style:
            cell.alignment = styles.alignment.Alignment(
                horizontal=style.get("halign", None),
                vertical=style.get("valign", None),
                wrapText=t.cast(bool, style.get("wrap", False)),
            )

        if "border" in style:
            cell.border = self.thin_border

    def _to_pos(self, name_pos: NamePos) -> CellPos:
        match (name_pos):
            case str():
                return CellPos.simple(name_pos)
            case _:
                return name_pos

    def cell(self, name_pos: NamePos) -> Cell:
        pos = self._to_pos(name_pos)

        defined_names: DefinedNameDict = t.cast(DefinedNameDict, self.wb.defined_names)

        if pos.name not in defined_names:
            raise KeyError(f"{pos} is not found!")

        p: list[str] = t.cast(str, defined_names[pos.name].attr_text).split("!")
        self.ws = self.wb[p[0]]
        cell_str: list[str] = p[1].split("$")

        return t.cast(
            Cell,
            self.ws.cell(
                row=int(cell_str[2]) + pos.row_delta,
                column=utils.column_index_from_string(cell_str[1]) + pos.col_delta,
            ),
        )

    def set_comment(self, name_pos: NamePos, comment: str | None) -> None:
        if comment is not None:
            self.set_cell_comment(self.cell(name_pos), comment)

    def set_cell_comment(self, cell: Cell, comment: str) -> None:
        cell.comment = Comment(filter_out_none_xml_char(comment), "bot")
        cell.comment.width = 1024

    def get_int_value(self, name_pos: NamePos, default: int = 0) -> int:
        try:
            return cell2int(t.cast(CellValue, self.cell(name_pos).value), default)
        except KeyError:
            return default

    def get_float_value(self, name_pos: NamePos, default: float = 0) -> float:
        try:
            return cell2float(t.cast(CellValue, self.cell(name_pos).value), default)
        except KeyError:
            return default

    def get_str_value(self, name_pos: NamePos, default: str = "") -> str:
        try:
            return cell2str(
                t.cast(CellValue, self.cell(name_pos).value), default=default
            )
        except KeyError:
            return default

    def set_value(
        self,
        name_pos: NamePos,
        v: int | str | float,
        style: CellStyle | None = None,
        comment: str | None = None,
    ) -> None:
        pos = self._to_pos(name_pos)

        cell = self.cell(pos)
        cell.value = v

        if style is not None:
            self.style_cell(cell, style)

        if comment is not None and comment != "":
            self.set_cell_comment(cell, comment)

    def set_values(
        self, map: dict[str, int | float | str], style: CellStyle | None = None
    ) -> None:
        for k, v in map.items():
            self.set_value(CellPos.simple(k), v, style=style)

    def start_table(self, name_pos: NamePos | None, width: int) -> None:
        if name_pos is None:
            self.t_origin = self.t_cell
        else:
            self.t_origin = self.cell(name_pos)
        self.t_width = width
        self.t_ws = self.ws
        self.t_cell = self.t_origin

    def next_cell(self) -> None:
        if self.t_ws is None or self.t_origin is None or self.t_cell is None:
            return

        cell = self.t_cell
        if cell.column + 1 == self.t_origin.column + self.t_width:
            self.t_cell = t.cast(
                Cell, self.t_ws.cell(row=cell.row + 1, column=self.t_origin.column)
            )
        else:
            self.t_cell = t.cast(
                Cell, self.t_ws.cell(row=cell.row, column=cell.column + 1)
            )

    def skip_table_item(self, n: int = 1) -> None:
        for _ in range(n):
            self.next_cell()

    def add_table_item(
        self,
        value: float | int | str,
        style: CellStyle | None = None,
        comment: str | None = None,
    ):
        if self.t_ws is None or self.t_origin is None or self.t_cell is None:
            return

        self.t_cell.value = value

        if style is not None:
            self.style_cell(self.t_cell, style=style)

        if comment is not None and comment != "":
            self.set_cell_comment(self.t_cell, comment)

        self.next_cell()

    def get_table_item(self, none_to_null: bool = False) -> CellValue:
        if self.t_ws is None or self.t_origin is None or self.t_cell is None:
            return None

        v = self.t_cell.value

        match v:
            case float() | int() | str() | None:
                result = v
            case _:
                result = str(v)

        self.next_cell()

        if none_to_null and result is None:
            return ""

        return result

    def save(self, path: str) -> None:
        self.wb.save(path)

    def cal_table_width(self, pos: CellPos) -> int:
        self.start_table(pos, 1024)

        width = 0

        while True:
            v = self.get_table_item()
            if v == "" or v is None:
                break

            width += 1

        return width

    def cal_table_height(self, pos: CellPos) -> int:
        self.start_table(pos, 1)

        height = 0

        while True:
            v = self.get_table_item()
            if v is None or v == "":
                break

            height += 1

        return height

    def get_one_col(
        self,
        name_pos: str | CellPos,
        height: int | None = None,
    ) -> list[CellValue]:
        data: list[list[CellValue]] = self.get_table(name_pos, width=1, height=height)

        return [x[0] for x in data]

    def get_table(
        self,
        name_pos: str | CellPos,
        width: int | None = None,
        height: int | None = None,
    ) -> list[list[CellValue]]:
        pos = self._to_pos(name_pos)

        if width is None:
            width = self.cal_table_width(pos)
        if height is None:
            height = self.cal_table_height(pos)

        self.start_table(pos, width)

        return [
            [self.get_table_item(none_to_null=True) for _ in range(width)]
            for _ in range(height)
        ]


def cell2str(o: CellValue, default: str = "") -> str:
    match (o):
        case None:
            return default
        case str():
            return o.strip()
        case _:
            return str(o)


def cell2int(o: CellValue, default: int = 0) -> int:
    match (o):
        case None | "":
            return default
        case int():
            return o
        case float():
            return int(o + 0.5)
        case _:
            return int(str(o), 0)


def cell2float(o: CellValue, default: float = 0) -> float:
    match (o):
        case None:
            return default
        case float():
            return o
        case str() | int():
            return float(o)


def cell2bool(o: CellValue) -> bool:
    match (o):
        case None:
            return False
        case float():
            return o != 0.0
        case int():
            return o != 0
        case str():
            if o in ("t", "T", "true", "True", "y", "Y", "yes", "Yes"):
                return True
            return False


def cells2strs(lc: list[CellValue]) -> list[str]:
    return [cell2str(x) for x in lc]


def cells2ints(lc: list[CellValue]) -> list[int]:
    return [cell2int(x) for x in lc]


def cells2floats(lc: list[CellValue]) -> list[float]:
    return [cell2float(x) for x in lc]


TableRowT = t.TypeVar("TableRowT")


def create_named_tuple(
    rtype: type[TableRowT],
    data: c.Sequence[c.Sequence[CellValue]],
    indices: tuple[int, ...] | None = None,
    max_cols: int = 0,
) -> list[TableRowT]:
    result: list[TableRowT] = []
    origin_hints = t.cast(dict[str, type[object]], t.get_type_hints(rtype)).values()
    ctor = t.cast(c.Callable[..., TableRowT], rtype)

    if max_cols > 0:
        hints = list(origin_hints)

        if hints[-1] == tuple[str, ...]:
            for x in range(max_cols - len(hints)):
                hints.append(str)
    else:
        hints = origin_hints

    for x in data:
        tuple_data: list[str] = []
        values: list[float | int | str | bool | tuple[str, ...]] = []

        y: c.Iterable[CellValue]
        if indices is None:
            y = x
        else:
            y = (x[i] for i in indices)

        for stype, svalue in zip(hints, y):
            if stype == float:
                values.append(cell2float(svalue))
            elif stype == int:
                values.append(cell2int(svalue))
            elif stype == str:
                if len(tuple_data) == 0:
                    values.append(cell2str(svalue))
                else:
                    tuple_data.append(cell2str(svalue))
            elif stype == bool:
                values.append(cell2bool(svalue))
            elif stype == tuple[str, ...]:
                tuple_data.append(cell2str(svalue))

        if len(tuple_data) > 0:
            values.append(tuple(tuple_data))

        result.append(ctor(*values))

    return result
