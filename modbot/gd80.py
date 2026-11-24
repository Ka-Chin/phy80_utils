register_map: list[dict[str, int | float | str | list[int]]] = [
    # address, type, value
    {"address": 40013, "type": "FLOAT32", "value": 100.123},  # 警報点１
    {"address": 40015, "type": "FLOAT32", "value": 200.456},  # 警報点2
    {
        "address": 40017,
        "type": "UINT16",
        "value": [0, 0],
    },  # 警報ステータス、故障ステータス
    {"address": 40019, "type": "FLOAT32", "value": 1.123},  # フルスケール
    {"address": 40023, "type": "UINT16", "value": [0, 16]},  # ステータス、濃度値
    {"address": 40027, "type": "UINT16", "value": [0x260C, 0x0102, 0x0304]},
    {"address": 40039, "type": "UINT16", "value": 1},  # 機器情報
    {"address": 40040, "type": "UINT16", "value": [0] * 22},
    {
        "address": 40062,
        "type": "STRING",
        "value": "20261201020304",
        "length": 14,
    },  # 最終調整日時
    {"address": 40069, "type": "STRING", "value": "1234", "length": 20},  # シリアル番号
    {"address": 40079, "type": "STRING", "value": "CO2", "length": 10},  # ガス名
    {"address": 40084, "type": "STRING", "value": "CO2", "length": 20},  # TAG番号
    {
        "address": 40094,
        "type": "STRING",
        "value": "CO2 SENSOR",
        "length": 20,
    },  # 装置名称
    {"address": 40104, "type": "STRING", "value": "Garage", "length": 20},  # 測定場所
    {
        "address": 40114,
        "type": "STRING",
        "value": "CLI 123",
        "length": 10,
    },  # 顧客コード
    {
        "address": 40119,
        "type": "STRING",
        "value": "3456",
        "length": 20,
    },  # センサシリアル番号
    {"address": 40129, "type": "STRING", "value": "GD81", "length": 10},  # センサ型式
    {"address": 40134, "type": "UINT16", "value": [0] * 11},  # ユニット種別
    {"address": 40135, "type": "UINT16", "value": [0x11] * 8},  # エラーフラグ
    {"address": 40145, "type": "UINT16", "value": [0] * 3},  # MAC Addr
    {"address": 40148, "type": "UINT16", "value": [0] * 2},  # IP Addr
    {"address": 40150, "type": "UINT16", "value": [0] * 2},  # Subnet mask
]
