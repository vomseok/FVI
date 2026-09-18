# FVI 재분석 원자료 패키지

이 디렉터리는 **2025년 3월 경상북도 대형산불**을 대상으로 한 Fire Vulnerability Index (FVI) 재분석의 입력자료·출처·입수 조건을 한 곳에 관리한다. 목표는 가중치·연료점수 민감도, 30 m–10 m 격자 민감도, 피해경계 허용오차, KFFDRS/FWI 비교를 **동일한 공간·시간 기준의 실제 자료로 재실행**할 수 있게 하는 것이다.

> **현재 실행 상태: 불완전 입력 패키지.** 공개 이용과 재배포 조건이 확인된 SRTM DEM 두 타일만 물리적으로 포함되어 있다. 정규화 인자, FVI, 실제 피해경계, KMA 관측자료, 분석용 KFFDRS/FWI 격자는 아직 확보·검증되지 않았으므로 `results/`의 기존 `not_executed` 파일을 실제 결과로 바꾸면 안 된다.

## 현재 상태

| 요청 자료군 | 패키지 위치 | 상태 | 재분석에 대한 의미 |
|---|---|---|---|
| 지형 원자료 | `dem/srtm_1arcsec/` | **included** | HGT 원자료 두 타일. EPSG:5186/30 m 정합과 지형인자 정규화가 필요하다. |
| 환경부 중분류 토지피복도 | `landcover/` | **requires_user_download** | 로그인·자료신청·이용조건 확인 후 확보해야 연료인자를 생성할 수 있다. |
| 2025 사건기상 ASOS/AWS | `meteorology/event_2025/` | **requires_user_download** | KMA 원 관측·QC 플래그·관측소 메타데이터가 필요하다. |
| 1991–2020 평년 ASOS/AWS | `meteorology/climatology_1991_2020/` | **requires_user_download** | 평년 재계산용 장기 시계열 또는 공식 평년값이 필요하다. |
| 실제 소실지 경계 | `burn_perimeter/` | **required_not_available** | 실제 화재사건·소실 정의가 확인된 polygon 없이는 ROC·경계 허용오차를 실행할 수 없다. |
| KFFDRS/FWI 비교자료 | `comparison_kffdrs_fwi/` | **source_access_documented** | 공공 과거지도 ZIP은 지오참조 PNG이므로 정량 비교에는 불충분하다. 원 격자 또는 동일 입력 재산정값이 필요하다. |
| 0–100 FVI 구성·결과 래스터 | `derived_inputs/30m_epsg5186/` | **required_not_available** | 분석 스크립트가 요구하는 공동격자 GeoTIFF의 배치 위치이다. |

## 포함 DEM

`dem/srtm_1arcsec/N36E128.hgt.gz` 및 `N36E129.hgt.gz`는 AWS Open Data `elevation-tiles-prod`의 SRTM 1 arc-second HGT 타일이다. 두 파일은 gzip 무결성과 SHA-256을 확인하였다. 원 HGT는 WGS84 지리좌표이며, **정규화된 지형인자 래스터가 아니다.** 분석 전 압축해제, 모자이크, EPSG:5186 재투영, 30 m 공통격자 정렬, 고도·경사·사면향 산정 및 0–100 정규화가 필요하다.

- 원 URL: `https://s3.amazonaws.com/elevation-tiles-prod/skadi/N36/N36E128.hgt.gz`
- 원 URL: `https://s3.amazonaws.com/elevation-tiles-prod/skadi/N36/N36E129.hgt.gz`
- 출처·표시: SRTM data courtesy of the U.S. Geological Survey. AWS Terrain Tiles의 원자료·표시지침은 `data_availability_manifest.json`에 기록하였다.

## 분석 실행에 필요한 정확한 파일 규약

`analysis_code/`의 현재 구현은 자동 보정·추정을 하지 않는다. 아래 파일이 모두 실재하고 정합되어야 한다.

| 파일 | 필수 사양 | 사용하는 코드 |
|---|---|---|
| `derived_inputs/30m_epsg5186/topography.tif` | GeoTIFF, 0–100, EPSG:5186, 30 m | `fvi_calculation.py`, `sensitivity_analysis.py` |
| `derived_inputs/30m_epsg5186/meteorology.tif` | GeoTIFF, 0–100, 동일 extent/transform | `fvi_calculation.py`, `sensitivity_analysis.py` |
| `derived_inputs/30m_epsg5186/fuel.tif` | GeoTIFF, 0–100, 동일 extent/transform | `fvi_calculation.py`, `sensitivity_analysis.py` |
| `derived_inputs/30m_epsg5186/scenario_01_fvi.tif` | GeoTIFF, 기본 시나리오 FVI, 30 m | `validation.py` |
| `derived_inputs/30m_epsg5186/burn_label_30m.tif` | 0/1 GeoTIFF, 세 인자와 완전히 정합 | `sensitivity_analysis.py` |
| `burn_perimeter/burn_perimeter.gpkg` | 실제 소실지 polygon, 유효 geometry, 출처·작성일·라이선스 | `validation.py` |

## 재배포 및 대용량 관리

자료신청형·로그인형·제한공개 원자료는 허가와 이용조건이 확인되기 전에는 GitHub에 올리지 않는다. `data/.gitignore`는 대용량·제한 자료의 실수 커밋을 방지한다. 허가된 대형 래스터·시계열은 일반 GitHub 업로드 대신 Git LFS, Zenodo/기관 저장소 DOI, 또는 접근통제 객체저장소 중 이용조건에 맞는 방법을 사용한다. 저장소에는 체크섬, 원 출처, 취득일, 처리이력만 남긴다.

## 재실행 순서

1. 각 `SOURCE_REQUIRED.md`에 따라 합법적으로 원자료를 취득하고 `provenance_*.json`을 작성한다.
2. 모든 공간자료를 EPSG:5186 및 하나의 30 m grid origin/extent로 정합한다.
3. `topography.tif`, `meteorology.tif`, `fuel.tif`을 0–100 범위로 생성하고 유효 셀·결측 처리를 기록한다.
4. `analysis_code/fvi_calculation.py`로 `scenario_01_fvi.tif`을 계산한다.
5. `analysis_code/sensitivity_analysis.py`로 가중치와 연료점수 민감도, `validation.py`로 격자·경계 검증을 실행한다.
6. 입력 파일 SHA-256, 실행일, 패키지 버전, 소프트웨어 버전과 함께 기존 `not_executed` 결과 파일을 실제 결과로 교체한다.

세부 파일 사양과 반입 전 품질검사는 [DATA_DICTIONARY.md](DATA_DICTIONARY.md), 자산별 상태는 [data_availability_manifest.json](data_availability_manifest.json)을 따른다.
