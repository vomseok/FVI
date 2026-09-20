#!/usr/bin/env bash
# Download public KFFDRS reference MAP images for manual provenance review only.
# Output PNGs are not georeferenced and MUST NOT be used for quantitative FVI ROC/AUC validation.
# Confirm current copyright/KOGL conditions on the official portal before redistributing any output.
set -euo pipefail

OUT_DIR=${1:-./kffdrs_reference_not_for_analysis}
START_DATE=${2:-2025-03-22}
END_DATE=${3:-2025-03-28}
TYPE=${4:-obs}  # obs = hourly analysis-current; fct = 3-hour five-day forecast

mkdir -p "$OUT_DIR"
current="$START_DATE"
while [[ "$current" < "$END_DATE" || "$current" == "$END_DATE" ]]; do
  dotted=${current//-/\.}
  stem="kffdrs_${TYPE}_${current}"
  curl --fail --location --silent --show-error \
    --request POST 'https://forestfire.nifos.go.kr/sys/spd/pastDataZip.do' \
    --data-urlencode "searchType=${TYPE}" \
    --data-urlencode "searchDate=${dotted}" \
    --data-urlencode 'searchHour=11' \
    --output "${OUT_DIR}/${stem}.zip"
  sha256sum "${OUT_DIR}/${stem}.zip" >> "${OUT_DIR}/SHA256SUMS.txt"
  current=$(date -I -d "$current + 1 day")
done

echo "Downloaded source ZIPs to ${OUT_DIR}. Retain source URL, retrieval date, and license review with any use."
