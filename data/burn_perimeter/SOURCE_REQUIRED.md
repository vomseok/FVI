# 실제 소실지 피해경계 필요

FVI의 ROC/PR, 30 m–10 m 격자 민감도, 0/30/60/90 m 경계 허용오차는 **실제 2025년 3월 산불 소실지 polygon** 없이는 실행할 수 없다. 현재 이 폴더에는 검증 가능한 피해경계가 없다.

## 허용 출처 우선순위

1. 산림청·국립산림과학원·지자체가 사건 종료 후 확정한 공간 경계와 원 메타데이터
2. 공공기관이 배포한 검증 완료 burn severity/burn scar polygon
3. Sentinel-2/Landsat 등 원격탐사 기반 산출물 중 센서·영상일자·전처리·임계값·검증 절차가 모두 공개된 자료

잠정 피해면적 보도, 수치만 있는 표, 기사 지도를 손으로 추적한 polygon은 **실제 피해경계로 사용할 수 없다.** 분석용 대체경계가 불가피하면 `provisional`로 명시하고 정량 검증에는 사용하지 않는다.

## 최소 메타데이터

| 필드 | 요구 내용 |
|---|---|
| `source_agency` / `source_url` | 공급기관과 원 배포 위치 |
| `event_name` / `event_date_range` | 사건 식별자와 시·종료일시 |
| `burned_area_definition` | 산림피해, 화선영향구역, dNBR 임계값 등 경계의 정확한 의미 |
| `created_date` / `method` | 작성일·센서·판독/검증 방법 |
| `crs` / `area_ha` | 원 CRS와 원본 기준 면적 |
| `license` / `redistribution_allowed` | 재사용·GitHub 공개 가능 여부 |

## 권장 배치

```text
burn_perimeter/
├── burn_perimeter.gpkg
├── burn_perimeter_metadata.pdf  # 공급기관 원 메타데이터가 있는 경우
├── provenance_burn_perimeter.json
└── SOURCE_REQUIRED.md
```

`validation.py`는 GPKG를 EPSG:5186으로 변환한 뒤 기준 FVI grid에서 rasterize한다. GIS 파일 반입 전에는 geometry validity, empty feature, 중복 feature, polygon 면적을 검사한다.
