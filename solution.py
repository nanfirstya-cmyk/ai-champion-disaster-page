# AI 챔피언 블루(중급) 종합과정 2회차 인증평가
# 과목3. 자동화 산출물 - 산출물 ② Python 자동화 도구
# 실행: python solution.py

import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

INPUT_FILE = Path("재난발생_현황.csv")
OUTPUT_FILE = Path("결과_요약.csv")


def read_rows(path):
    """UTF-8 BOM이 있는 CSV도 안정적으로 읽습니다."""
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def to_float(value):
    """빈 값/문자 오류는 None으로 반환하고, 숫자는 float로 변환합니다."""
    text = "" if value is None else str(value).strip()
    if text == "":
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def median_fill(rows, column_name):
    """
    결측치 처리 기준:
    - 평균 계산 대상 컬럼의 결측값을 제외하거나 0 처리하지 않습니다.
    - 해당 컬럼의 유효값 중앙값으로 대체합니다.
    """
    valid_values = []
    for row in rows:
        value = to_float(row.get(column_name))
        if value is not None:
            valid_values.append(value)

    median_value = statistics.median(valid_values) if valid_values else 0

    filled_values = []
    for row in rows:
        value = to_float(row.get(column_name))
        filled_values.append(value if value is not None else median_value)
    return filled_values


def average_rounded(values):
    return int(round(sum(values) / len(values))) if values else 0


def main():
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {INPUT_FILE}")

    rows = read_rows(INPUT_FILE)

    total_count = len(rows)
    casualty_count = sum(
        1 for row in rows
        if str(row.get("인명피해여부", "")).strip().upper() == "Y"
    )

    damage_values = median_fill(rows, "피해금액_만원")
    average_damage = average_rounded(damage_values)

    disaster_type_counts = Counter(
        row.get("재난유형", "").strip() or "미상"
        for row in rows
    )

    recovery_values = median_fill(rows, "복구기간_일")
    recovery_by_region = defaultdict(list)
    for row, recovery_days in zip(rows, recovery_values):
        region = row.get("발생지역", "").strip() or "미상"
        recovery_by_region[region].append(recovery_days)

    top3_recovery = sorted(
        (
            (region, average_rounded(values))
            for region, values in recovery_by_region.items()
        ),
        key=lambda item: (-item[1], item[0])
    )[:3]

    with OUTPUT_FILE.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["구분", "항목", "값", "단위"])
        writer.writerow(["요약", "총 재난 사건 수", total_count, "건"])
        writer.writerow(["요약", "인명피해 발생 사건 수", casualty_count, "건"])
        writer.writerow(["요약", "평균 피해금액", average_damage, "만원"])
        writer.writerow([])
        writer.writerow(["재난유형별 사건 수", "재난유형", "사건 수", "건"])
        for disaster_type, count in sorted(disaster_type_counts.items(), key=lambda item: (-item[1], item[0])):
            writer.writerow(["재난유형별 사건 수", disaster_type, count, "건"])
        writer.writerow([])
        writer.writerow(["지역별 평균 복구기간 상위 3", "지역", "평균 복구기간", "일"])
        for region, avg_days in top3_recovery:
            writer.writerow(["지역별 평균 복구기간 상위 3", region, avg_days, "일"])

    print(f"[OK] 재난 {total_count}건 분석 -> {OUTPUT_FILE}")
    print(f"총 사건: {total_count}건 / 인명피해: {casualty_count}건 / 평균 피해: {average_damage}만 원")


if __name__ == "__main__":
    main()
