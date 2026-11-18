#!/usr/bin/env python3
"""kiem_thu_quy_trinh.py — Kiểm thử quy trình dữ liệu của nhóm XSTK.

Chạy:  python kiem_thu_quy_trinh.py            (trong thư mục gốc repository)
       python kiem_thu_quy_trinh.py --raw "<đường dẫn Car details v3.csv>" --clean "<cleaned_cars.csv>"
Trên Kaggle: tải file này lên rồi chạy `!python kiem_thu_quy_trinh.py --raw ... --clean ...`.

Script **cài đặt lại độc lập** các quy tắc làm sạch (không import notebook 01) rồi so với
cleaned_cars.csv — nếu hai cách cho kết quả khác nhau thì một trong hai có lỗi.

Mỗi dòng kết quả có nhãn:
  PASS  — đạt;
  WARN  — không sai nhưng cần ghi cách xử lý trong báo cáo;
  FAIL  — sai, phải sửa trước khi nghiệm thu.
Mã thoát = 1 nếu có ít nhất một FAIL.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DEFAULT_RAW = ROOT / "data" / "raw" / "Car details v3.csv"
DEFAULT_CLEAN = ROOT / "data" / "processed" / "cleaned_cars.csv"
DEFAULT_META = ROOT / "data" / "processed" / "cleaned_cars_v1.0.json"

RAW_SHA256 = "788e7f7a5be161011789a0d4b64ea0879570348c943a414f4f99953f58d74048"
RAW_SHAPE = (8128, 13)
OWNER_ORDER = ["First Owner", "Second Owner", "Third Owner", "Fourth & Above Owner"]

results: list[tuple[str, str, str]] = []


def report(status: str, name: str, detail: str = "") -> None:
    results.append((status, name, detail))
    print(f"{status:<4}  {name}" + (f" — {detail}" if detail else ""))


def check(cond: bool, name: str, detail: str = "", warn: bool = False) -> bool:
    report("PASS" if cond else ("WARN" if warn else "FAIL"), name, detail)
    return bool(cond)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# ---------------------------------------------------------------- cài đặt độc lập
def first_number(s: str) -> float:
    m = re.search(r"\d+(?:\.\d+)?|\.\d+", s)
    return float(m.group()) if m else np.nan


def torque_to_nm(s) -> float:
    if not isinstance(s, str):
        return np.nan
    t = s.lower().replace(",", "")
    v = first_number(t)
    if np.isnan(v):
        return np.nan
    i_nm, i_kg = t.find("nm"), t.find("kgm")
    is_kgm = (i_kg >= 0 and (i_nm < 0 or i_kg < i_nm)) or (i_nm < 0 and i_kg < 0 and v < 60)
    if is_kgm and v > 60:
        is_kgm = False
    nm = v * 9.80665 if is_kgm else v
    return nm if nm <= 700 else np.nan


def reference_clean(raw: pd.DataFrame) -> pd.DataFrame:
    d = raw.drop_duplicates().copy()
    num = lambda col: d[col].map(lambda x: first_number(x) if isinstance(x, str) else np.nan)
    d["mileage_n"] = num("mileage").replace(0, np.nan)
    d["engine_n"] = num("engine")
    d["power_n"] = num("max_power").where(lambda x: x > 0)
    d = d.dropna(subset=["mileage_n", "engine_n", "power_n", "seats"])
    d = d[d["owner"] != "Test Drive Car"]
    age = 2020 - d["year"]
    d = d[(d["km_driven"] <= 500_000) & ~((d["km_driven"] < 1_000) & (age >= 2))]
    return d


# ---------------------------------------------------------------- các nhóm kiểm thử
def test_raw(raw_path: Path) -> pd.DataFrame | None:
    print("\n== 1. Dữ liệu gốc ==")
    if not check(raw_path.exists(), "Có file dữ liệu gốc", str(raw_path)):
        return None
    raw = pd.read_csv(raw_path)
    check(raw.shape == RAW_SHAPE, "Kích thước gốc 8.128 × 13", f"thực tế {raw.shape}")
    digest = sha256(raw_path)
    check(digest == RAW_SHA256, "SHA-256 khớp bản đã đăng ký", digest[:16] + "…",
          warn=True)  # bản Kaggle tải lại có thể khác ký tự xuống dòng
    check("car data.csv" not in raw_path.name, "Không dùng car data.csv (301 dòng, thiếu cột)")
    n_dup = int(raw.duplicated().sum())
    report("WARN" if n_dup else "PASS", "Dòng trùng lặp trong dữ liệu gốc",
           f"{n_dup:,} dòng — đã xoá ở bước 1, ghi trong nhật ký")
    vc = raw["seller_type"].value_counts()
    report("WARN", "Mức hiếm seller_type = Trustmark Dealer",
           f"{vc.get('Trustmark Dealer', 0)} xe trước xoá trùng — gộp vào Dealer (cờ is_trustmark)")
    report("WARN", "Mức hiếm owner = Test Drive Car",
           f"{(raw['owner'] == 'Test Drive Car').sum()} xe — loại, lý do ghi ở mục 2.7")
    return raw


def test_clean(raw: pd.DataFrame | None, clean_path: Path, meta_path: Path) -> pd.DataFrame | None:
    print("\n== 2. File sạch cleaned_cars.csv ==")
    if not check(clean_path.exists(), "Có file cleaned_cars.csv", str(clean_path)):
        return None
    c = pd.read_csv(clean_path)
    expected_cols = ["raw_index", "name", "brand", "model", "year", "car_age", "selling_price", "log_price",
                     "km_driven", "fuel", "fuel_group", "seller_type", "is_trustmark", "transmission",
                     "owner", "owner_rank", "mileage", "mileage_unit", "engine", "max_power", "torque_nm", "seats"]
    check(list(c.columns) == expected_cols, "Đủ 22 cột đúng thứ tự từ điển dữ liệu")

    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        check(meta.get("version") == "1.0", "Phiên bản dữ liệu v1.0", f"ngày đóng băng {meta.get('freeze_date')}")
        check(sha256(clean_path) == meta.get("cleaned_sha256"), "SHA-256 file sạch khớp bản đóng băng",
              "nếu FAIL: file đã bị sửa sau mốc 2 — phải báo cả nhóm và tăng phiên bản")
        check(list(c.shape) == meta.get("cleaned_shape"), "Số dòng/cột khớp bản đóng băng", f"{c.shape}")
    else:
        report("WARN", "Không thấy cleaned_cars_v1.0.json", "bỏ qua kiểm tra phiên bản")

    core = c.drop(columns="torque_nm")
    check(int(core.isna().sum().sum()) == 0, "Không còn NA ở các cột chính")
    n_tq = int(c["torque_nm"].isna().sum())
    report("WARN" if n_tq else "PASS", "torque_nm (biến phụ) có NA", f"{n_tq} ô — không dùng dropna() toàn bảng")
    check(c["raw_index"].is_unique, "raw_index không trùng (mỗi dòng sạch ↔ 1 dòng gốc)")
    km_ok = c["km_driven"].le(500_000).all() and not (c["km_driven"].lt(1_000) & c["car_age"].ge(2)).any()
    check(km_ok, "km_driven hợp lý (≤ 500.000; không có xe ≥ 2 tuổi chạy < 1.000 km)")
    check((c["mileage"] > 0).all() and (c["engine"] > 0).all() and (c["max_power"] > 0).all(),
          "mileage, engine, max_power dương")
    check(c["selling_price"].gt(0).all(), "selling_price dương")
    check(np.allclose(c["log_price"], np.log(c["selling_price"]), atol=1e-6), "log_price = ln(selling_price)")
    check((c["car_age"] == 2020 - c["year"]).all(), "car_age = 2020 − year")
    check(set(c["owner"]) == set(OWNER_ORDER), "owner chỉ còn 4 mức (đã bỏ Test Drive Car)")
    rank_ok = (c["owner"].map({k: i + 1 for i, k in enumerate(OWNER_ORDER)}) == c["owner_rank"]).all()
    check(rank_ok, "owner_rank khớp thứ bậc owner")
    check(set(c["seller_type"]) == {"Individual", "Dealer"}, "seller_type còn 2 mức (đã gộp Trustmark)")
    check(set(c["fuel"]) == {"Petrol", "Diesel", "CNG", "LPG"}, "fuel giữ 4 mức")
    check(set(c["fuel_group"]) == {"Petrol", "Diesel", "CNG/LPG"}, "fuel_group gộp CNG/LPG")
    unit_ok = (c["mileage_unit"].eq("km/kg") == c["fuel"].isin(["CNG", "LPG"])).all()
    check(unit_ok, "mileage_unit khớp nhiên liệu (kmpl: xăng/dầu; km/kg: CNG/LPG)")
    check(not c["brand"].isin(["Land", "Ashok"]).any(), "Tên hãng hai từ đã được sửa (Land Rover, Ashok Leyland)")

    if raw is not None:
        print("\n== 3. Đối chiếu với cài đặt độc lập ==")
        ref = reference_clean(raw)
        check(len(ref) == len(c), "Số dòng khớp cài đặt độc lập", f"độc lập {len(ref):,} / file {len(c):,}")
        check(set(ref.index) == set(c["raw_index"]), "Tập raw_index khớp cài đặt độc lập")
        r = ref.loc[c["raw_index"]]
        check((r["selling_price"].values == c["selling_price"].values).all(), "selling_price khớp dữ liệu gốc")
        check(np.allclose(r["mileage_n"].values, c["mileage"].values), "mileage khớp tách số độc lập")
        check(np.allclose(r["engine_n"].values, c["engine"].values), "engine khớp tách số độc lập")
        check(np.allclose(r["power_n"].values, c["max_power"].values), "max_power khớp tách số độc lập")
        tq = r["torque"].map(torque_to_nm).values
        same = np.isclose(tq, c["torque_nm"].values, atol=0.01) | (np.isnan(tq) & c["torque_nm"].isna().values)
        check(same.all(), "torque_nm khớp tách số độc lập", f"{(~same).sum()} ô lệch")
    return c


def test_analysis_warnings(c: pd.DataFrame) -> None:
    print("\n== 4. Cảnh báo cho phần phân tích (TV2, TV3, TV4) ==")
    small = c["fuel"].value_counts()
    report("WARN", "Nhóm nhiên liệu nhỏ", f"CNG = {small.get('CNG', 0)}, LPG = {small.get('LPG', 0)} → "
           "dùng fuel_group khi kiểm định, ghi cỡ mẫu khi tính KTC")
    report("WARN" if len(c) > 5000 else "PASS", "Cỡ mẫu > 5.000",
           f"n = {len(c):,}: Shapiro-Wilk gần như luôn bác bỏ → dùng Q-Q plot, độ lệch, độ nhọn; Welch t-test")
    skew = c["selling_price"].skew()
    report("WARN" if skew > 1 else "PASS", "selling_price lệch phải",
           f"skew = {skew:.2f} (log_price: {c['log_price'].skew():.2f}) → dùng log_price")
    r = c[["engine", "max_power"]].corr().iloc[0, 1]
    report("WARN" if r > 0.6 else "PASS", "engine và max_power tương quan mạnh", f"r = {r:.2f} → kiểm tra VIF")
    rare = (c["brand"].value_counts() < 10).sum()
    report("WARN", "Hãng xe có ít hơn 10 xe", f"{rare} hãng → gộp nhóm trước khi tạo dummy (TV4)")
    auto = c["transmission"].eq("Automatic").sum()
    report("PASS" if auto >= 30 else "WARN", "Đủ xe số tự động để kiểm định", f"{auto} xe")


def test_repo() -> None:
    print("\n== 5. Cấu trúc repository ==")
    for p in ["README.md", "requirements.txt", "data/raw", "data/processed", "notebooks/01_cleaning.ipynb",
              "docs/tu_dien_du_lieu.md", "docs/nhat_ky_lam_sach.md", "report"]:
        check((ROOT / p).exists(), f"Có {p}")
    for p in ["notebooks/02_eda.ipynb", "notebooks/03_hypothesis.ipynb", "notebooks/04_regression.ipynb"]:
        check((ROOT / p).exists(), f"Có {p}", "notebook của TV2–TV4", warn=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    ap.add_argument("--clean", type=Path, default=DEFAULT_CLEAN)
    ap.add_argument("--meta", type=Path, default=DEFAULT_META)
    ap.add_argument("--skip-repo", action="store_true", help="bỏ qua kiểm tra cấu trúc repo (khi chạy trên Kaggle)")
    args = ap.parse_args()

    raw = test_raw(args.raw)
    clean = test_clean(raw, args.clean, args.meta)
    if clean is not None:
        test_analysis_warnings(clean)
    if not args.skip_repo:
        test_repo()

    counts = pd.Series([s for s, _, _ in results]).value_counts()
    print(f"\nTỔNG KẾT: PASS = {counts.get('PASS', 0)}, WARN = {counts.get('WARN', 0)}, FAIL = {counts.get('FAIL', 0)}")
    return 1 if counts.get("FAIL", 0) else 0


if __name__ == "__main__":
    sys.exit(main())
