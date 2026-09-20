# 1991–2020 평년 재계산용 ASOS/AWS 자료 필요

A-4 평년값 검토는 1991–2020이라는 기간만 표기해서는 충분하지 않다. 각 기상요소의 관측소·이용가능 기간·집계식·결측 처리를 재현할 수 있어야 한다. 현재 이 폴더에는 장기 관측기록이나 재계산 평년표가 없다.

## 공식 입수 경로와 제약

- ASOS 파일셋: <https://data.kma.go.kr/data/grnd/selectAsosList.do?pgmNo=36>
- ASOS 자료 조회: <https://data.kma.go.kr/data/grnd/selectAsosRltmList.do>
- AWS 자료 조회: <https://data.kma.go.kr/data/grnd/selectAwsRltmList.do>

ASOS 파일셋 안내에 따르면 ASOS 자료는 1904년부터 지점·요소별로 제공되며, 긴 기간의 자료는 파일셋 경로를 이용할 수 있다. AWS는 관측소 개설·이설·관측요소 변경 이력이 있을 수 있으므로 1991–2020 전체를 기계적으로 합치면 안 된다.

## 두 가지 허용 경로

| 경로 | 필요한 원자료 | 저장 파일 예시 | 주의사항 |
|---|---|---|---|
| 장기 원시계열 재계산 | 일/월/시간 ASOS/AWS 파일셋 | `asos_aws_1991_2020_raw.*` | station history·QC·요소별 유효기간을 문서화 |
| 공식 평년 통계 활용 | 공식 평년 통계표 및 출처 | `official_normals_1991_2020.*` | 산식·공간보간과의 접속 규칙을 명시 |

## 권장 배치

```text
meteorology/climatology_1991_2020/
├── asos_aws_1991_2020_raw.*
├── stations_1991_2020.csv
├── climatology_calculation.md
├── provenance_normals_1991_2020.json
└── SOURCE_REQUIRED.md
```

평년은 평균·백분위·최대·건조일수 등 어떤 통계량인지 요소별로 명시하고, 사건기상과 동일한 단위·시간대·관측소 집합을 사용하는지 확인한다.
