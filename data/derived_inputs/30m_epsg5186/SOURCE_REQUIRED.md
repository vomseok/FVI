# FVI 정규화 인자·기본 FVI 격자 배치 규약

이 폴더는 원자료를 전처리한 뒤 FVI 코드에 직접 전달할 GeoTIFF를 위한 위치이다. 현재 실제 GeoTIFF는 없다. 빈 파일·합성 데이터·추정값을 넣어서는 안 된다.

## 필수 파일

```text
derived_inputs/30m_epsg5186/
├── topography.tif
├── meteorology.tif
├── fuel.tif
├── burn_label_30m.tif
├── scenario_01_fvi.tif
├── provenance_derived_inputs.json
└── SOURCE_REQUIRED.md
```

## 코드 수준 검증 규칙

| 파일 | 값/형식 | 코드가 검사하는 내용 |
|---|---|---|
| `topography.tif`, `meteorology.tif`, `fuel.tif` | float GeoTIFF, 0–100 | 세 파일의 CRS·transform·height·width 완전 일치, 유효값 0–100 |
| `burn_label_30m.tif` | uint8 0/1 GeoTIFF | 인자 raster와 완전 정합, burned/unburned가 모두 존재 |
| `scenario_01_fvi.tif` | float GeoTIFF | `validation.py`의 30 m 기준 입력 |

### 10 m 검증의 정확한 의미

현재 `validation.py`의 10 m 결과는 독립 10 m 입력을 새로 계산하는 것이 아니라, 30 m FVI를 bilinear resampling한 **해상도 민감도 시험**이다. 독립 10 m DEM·토지피복·기상격자를 확보해 다시 계산하는 연구 설계와 동일시하면 안 된다.

각 실제 GeoTIFF는 최소·최대·평균·nodata·valid-cell count, source SHA-256, 산출 코드 버전, 정규화 식을 `provenance_derived_inputs.json`에 기록한다.
