# 2025년 3월 사건기상 ASOS/AWS 원관측 필요

FVI 기상인자는 2025년 3월 산불 사건창을 대표하는 실제 기상관측으로 산정해야 한다. 이 폴더에는 현재 ASOS/AWS 원관측 파일이 없다.

## 공식 입수 경로

- 기상자료개방포털 ASOS 자료: <https://data.kma.go.kr/data/grnd/selectAsosRltmList.do>
- 기상자료개방포털 AWS 자료: <https://data.kma.go.kr/data/grnd/selectAwsRltmList.do>
- ASOS 파일셋 안내: <https://data.kma.go.kr/data/grnd/selectAsosList.do?pgmNo=36>

ASOS 파일셋 안내상 시간 자료는 1회 최대 1년 조회가 가능하고, 시간·분 자료에는 일부 요소의 QC flag(0 정상, 1 오류, 9 결측)가 제공된다. 다운로드 화면의 로그인·자료이용 조건은 취득자가 확인한다.

## 최소 요구사항

| 항목 | 요구사항 |
|---|---|
| 사건창 | 발화·주요 확산·진화 시각을 포함한 명시적 KST 구간; UTC 변환 여부도 기록 |
| 관측소 | 분석영역과 주변부의 ASOS 및 필요 시 AWS. station ID·위경도·고도·운영상태 포함 |
| 관측요소 | 기온, 상대습도, 풍속, 풍향, 강수량 및 원고의 기상지수 산식에 필요한 모든 요소 |
| 품질 | 원 QC flag 보존, 오류·결측 제외/보정 규칙 기록 |
| 공간화 | 보간법, 사용 관측소, 탐색반경, 표고보정 유무, 시간집계 규칙 명시 |

## 권장 배치

```text
meteorology/event_2025/
├── asos_aws_event_2025.csv
├── stations_event_2025.csv
├── provenance_event_2025.json
└── SOURCE_REQUIRED.md
```

`asos_aws_event_2025.csv`는 수정한 가공값이 아니라, 가능한 한 다운로드 원자료와 동일한 열을 유지한다. 원자료 재배포가 허용되지 않는 경우에는 보안 저장소에 보관하고 이 폴더에는 출처·체크섬·추출조건만 남긴다.
