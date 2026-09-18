# FVI 원자료 데이터 사전 및 반입 검증 기준

이 문서는 원자료의 파일명·최소 메타데이터·검증 기준을 고정한다. 자료가 있더라도 이 기준을 만족하지 않으면 FVI 재분석에 사용하지 않는다.

## 공통 공간 기준

| 항목 | 기준 | 확인 방법 |
|---|---|---|
| 좌표계 | EPSG:5186 (Korea 2000 / Central Belt 2010) | GeoTIFF/GPKG CRS metadata |
| 기준 해상도 | 30 m × 30 m | transform의 x/y pixel size |
| 분석영역·원점 | 세 인자와 burn label이 완전히 동일 | CRS, width, height, transform 비교 |
| 노데이터 | GeoTIFF에서 명시; 유효 셀만 연산 | `nodata`, mask, valid-cell count |
| 값 범위 | FVI 세 구성인자는 0–100 | valid-cell min/max |
| 시간 기준 | 사건기상은 KST/UTC를 명시하고 하나로 통일 | 시간대 필드 및 처리로그 |

## 입수·생성 대상

| ID | 표준 경로/파일명 | 원자료 또는 산출물 | 필수 메타데이터 | 허용 상태 |
|---|---|---|---|---|
| DEM-01 | `dem/srtm_1arcsec/N36E128.hgt.gz` | SRTM HGT 원자료 | source URL, SHA-256, tile, vertical unit | 포함됨 |
| DEM-02 | `dem/srtm_1arcsec/N36E129.hgt.gz` | SRTM HGT 원자료 | source URL, SHA-256, tile, vertical unit | 포함됨 |
| LC-01 | `landcover/moe_landcover_medium_YYYY_*` | 환경부 중분류 토지피복 도엽 | 제작연도, 도엽, 분류코드, 이용조건, 취득일 | 원본 이용조건 확인 후 |
| MET-EVT-01 | `meteorology/event_2025/asos_aws_event_2025.csv` | 사건시점 ASOS/AWS 관측 | station ID, KST/UTC, 요소, QC flag, 결측 처리 | 원본·메타데이터 함께 |
| MET-NRM-01 | `meteorology/climatology_1991_2020/asos_aws_1991_2020.*` | 장기 ASOS/AWS 기록 또는 요소별 평년 원자료 | 기간, station history, aggregation, QC | 원본·메타데이터 함께 |
| BURN-01 | `burn_perimeter/burn_perimeter.gpkg` | 실제 산불 소실지 polygon | 출처, 사건일, 소실 정의, 작성일, CRS, license | 검증 가능한 공식/원격탐사 산출물 |
| DER-TOP-01 | `derived_inputs/30m_epsg5186/topography.tif` | 정규화 지형인자 | source inputs, derivation rule, normalization rule, SHA-256 | 0–100, 공동격자 |
| DER-MET-01 | `derived_inputs/30m_epsg5186/meteorology.tif` | 정규화 기상인자 | event window, stations, interpolation, normalization | 0–100, 공동격자 |
| DER-FUEL-01 | `derived_inputs/30m_epsg5186/fuel.tif` | 정규화 연료인자 | land-cover version, score map, rasterization rule | 0–100, 공동격자 |
| DER-FVI-01 | `derived_inputs/30m_epsg5186/scenario_01_fvi.tif` | 기본 FVI | scenario ID, input SHA-256, execution log | 0–100, 공동격자 |
| DER-LBL-01 | `derived_inputs/30m_epsg5186/burn_label_30m.tif` | 0/1 burn label | source BURN-01, rasterization rule, SHA-256 | 0/1, 공동격자 |
| CMP-01 | `comparison_kffdrs_fwi/kffdrs_or_fwi_*.tif` | 정량 비교용 KFFDRS/FWI 격자 | index definition, time, CRS, resolution, source, license | FVI와 동일 표본으로 정합 |

## 반입 전 품질검사

1. **원본성:** 공급기관·다운로드 URL·취득일·원 파일명과 SHA-256을 기록한다.
2. **공간정합:** 세 인자와 burn label은 CRS·transform·width·height가 모두 일치해야 한다. 스크립트가 불일치 시 중단하는 것이 정상 동작이다.
3. **값 검증:** 인자 GeoTIFF에는 0–100 밖의 값이 없어야 하며, label에는 0과 1이 모두 있어야 한다.
4. **시간정합:** 2025년 사건창은 발화·확산·진화 시점과 KST/UTC를 명시하고, KFFDRS/FWI·기상자료가 같은 사건창을 대표하는지 확인한다.
5. **경계 검증:** GPKG geometry의 self-intersection, empty geometry, 중복 feature를 검사하고, `burned-area-definition`을 명시한다.
6. **재배포 검증:** 개인정보·관측소 보안제한·자료신청 조건·KOGL 유형을 확인하고, 허용되지 않으면 데이터 파일이 아닌 provenance 및 입수 지침만 저장소에 넣는다.

## 결과 해석의 금지사항

- 뉴스 기사·잠정 면적을 이용해 만든 추정 polygon을 `burn_perimeter.gpkg`라는 **실제 피해경계**로 대체하지 않는다.
- 지오참조가 없는 KFFDRS 지도 PNG를 GeoTIFF처럼 재투영하여 ROC 수치를 만들지 않는다.
- 결측된 ASOS/AWS·토지피복·피해경계를 합성 또는 추정해 `completed` 결과를 생성하지 않는다.
