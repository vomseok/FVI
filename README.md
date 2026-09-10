# FVI 논문 최종 수정본 및 심사 근거자료

이 저장소는 도시생태현황도 기반 산불취약성·WUI 분석 논문의 최종 수정본과 3인 재심사 대응자료를 보관합니다.

## 주요 문서

- `manuscript/Paper1_Comparison_Final_3Review_Revised.docx`: 재심사 결과 반영 최종 Word 원고
- `manuscript/Paper1_Comparison_Final_3Review_Revised.md`: 편집 가능한 Markdown 원고
- `manuscript/Supplementary_Material.docx`: 보충자료
- `review/Response_to_Three_Reviewers.docx`: 3인 심사위원 의견별 수정 대응표
- `review/Response_to_Three_Reviewers.md`: 수정 대응표 원문
- `review/Three_Reviewer_Reassessment.md`: 재심사 종합 의견
- `review/Reviewer_Comparison.md`: 심사위원별 판정 및 쟁점 비교
- `review/Revision_Summary.md`: 주요 수정사항 요약
- `review/Final_QC_Report.txt`: 최종 문서 품질검수 결과

## 근거자료 및 검토 기록

- `evidence/external_review_sources.md`: WUI 정의, Natural Breaks 및 투고규정 검토 근거
- `evidence/methodology_review_notes.md`: 연구설계·방법론·수치 일관성 검토 기록
- `evidence/content_review_notes.md`: 결과·고찰·결론·인용 검토 기록
- `evidence/visual_review_notes.txt`: 원고 시각 검토 기록
- `evidence/figure_qc_notes.md`: 최종 그림 품질검수 기록
- `evidence/resource_audit.md`: 재분석 가능 자산과 한계 기록

## 그림 및 도표

최종 원고에 사용된 교정 그림은 `figures/`에 저장합니다. 원자료의 저작권과 공개 가능 범위를 확인한 뒤 외부 공개가 제한되는 GIS 원자료는 저장소에 포함하지 않습니다.

## 재현성 주의사항

원 FVI 격자·중간인자 래스터·원 벡터 GIS가 현재 작업 세션에 모두 남아 있지 않아, 최종 수정본에는 경험적 가중치·연료점수 및 30 m·경계 허용대 재분석의 확정 수치를 임의로 추가하지 않았습니다. 원자료를 복구하면 해당 민감도 분석을 재실행해야 합니다. 저장소의 `evidence/resource_audit.md`와 `review/Response_to_Three_Reviewers.md`에 이 제한을 명시했습니다.
