# KFFDRS/FWI 비교검증 자료

A-9 비교검증은 FVI와 같은 사건창·공간범위·평가표본에서 비교 가능한 **수치 격자**가 필요하다. 현재 이 폴더에는 정량 비교를 수행할 수 있는 KFFDRS 또는 Canadian FWI GeoTIFF가 없다.

## 확인된 공개 참고 경로

- 국가산불위험예보시스템 과거자료검색: <https://forestfire.nifos.go.kr/sys/spd/srchPastDataList.do?searchType=obs>
- 산림청 공공저작물 이용정책: <https://www.forest.go.kr/kfsweb/kfi/kfs/cms/cmsView.do?mn=NKFS_07_07&cmsId=FC_000367>

2026-09-18에 위 공식 시스템의 2025-03-25 `분석실황` 및 `분석예보` ZIP 엔드포인트를 확인하였다. ZIP에는 시간별/3시간별 **PNG 지도**가 포함되어 있으며 PNG 크기는 481×524 px이다. 페이지상 지오참조·격자값·원 입력자료가 제공되지 않으므로 이는 출처 확인용 시각 참고자료일 뿐, ROC·AUC용 공간 래스터가 아니다. 파일에 표시된 KOGL 유형 또는 개별 이용조건이 명확하지 않아, 원 ZIP/PNG는 이 공개 Git 패키지에 재배포하지 않는다.

## 정량 비교에 허용되는 입력

| 선택지 | 조건 | 경로 예시 |
|---|---|---|
| 공식 KFFDRS 원 격자 | 사건일시, CRS, 해상도, 지수값, 라이선스가 명시된 raster/vector grid | `kffdrs_20250325_*.tif` |
| Canadian FWI 재산정 | 동일 기상입력·일 경계·초기화 규칙·코드·파라미터를 보존 | `fwi_20250325_*.tif` |
| KFFDRS 재현 계산 | 원 논문/공식 정의와 입력자료가 명시되고 independent check 가능 | `kffdrs_recomputed_*.tif` |

모든 후보는 FVI 30 m grid와 **동일 표본**으로 resample/align한 뒤 비교해야 한다. 시간별 KFFDRS는 사건창의 어떤 시각을 대표하는지 사전에 고정하며, 서로 다른 날짜·공간해상도의 지도를 임의로 비교하지 않는다.

## 공개 참고 PNG의 안전한 재취득

`download_kffdrs_reference_images.sh`는 공식 ZIP을 사용자 로컬에 내려받아 검토하는 보조 스크립트다. 다운로드·재배포 전에는 해당 화면의 개별 이용조건과 KOGL 표시를 다시 확인한다.
