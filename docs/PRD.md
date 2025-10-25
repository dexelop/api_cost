# 📋 Product Requirements Document (PRD)
# LLM API Cost Calculator

## 📌 프로젝트 개요

### 제품명
LLM API Cost Calculator

### 버전
v1.0.0

### 작성일
2025-10-25

### 목적
다양한 LLM(Large Language Model) API의 사용 비용을 사전에 예측하고 비교할 수 있는 웹 기반 계산기 도구

### 대상 사용자
- AI/ML 개발자
- 프로덕트 매니저
- 스타트업 및 기업의 의사결정자
- LLM API 비용 최적화가 필요한 모든 사용자

---

## 🎯 핵심 가치 제안

1. **비용 투명성**: 파일 업로드만으로 즉시 예상 API 비용 확인
2. **다중 모델 비교**: 여러 LLM 제공업체와 모델을 한눈에 비교
3. **정확한 토큰 계산**: 파일 타입별 최적화된 토큰 계산 방식
4. **실시간 가격 업데이트**: 최신 가격 정보 자동 반영

---

## 📊 기능 요구사항

### 1. 파일 업로드 (P0 - 필수)

#### 1.1 지원 파일 형식
- 문서: PDF, DOCX, TXT, MD
- 데이터: XLSX, CSV, JSON
- 이미지: PNG, JPG, JPEG, GIF, WEBP
- 코드: PY, JS, TS, JAVA, CPP, etc.

#### 1.2 업로드 방식
- ✅ 드래그앤드롭 지원
- ✅ 파일 선택 버튼
- ✅ 다중 파일 동시 업로드 (최대 10개)
- ✅ 클립보드 붙여넣기 (텍스트)

#### 1.3 파일 크기 제한
- 단일 파일: 최대 50MB
- 전체 업로드: 최대 200MB

### 2. 토큰 계산 (P0 - 필수)

#### 2.1 계산 방식
- **정확 모드**: tiktoken 라이브러리 사용 (OpenAI 호환)
- **빠른 모드**: 문자 수 기반 근사치
- **하이브리드 모드**: 파일 타입별 최적 방식 자동 선택

#### 2.2 파일별 처리
| 파일 타입 | 처리 방식 | 정확도 |
|---------|---------|--------|
| TXT/MD | tiktoken 직접 적용 | 100% |
| PDF | 텍스트 추출 → tiktoken | 95% |
| DOCX | 텍스트 추출 → tiktoken | 95% |
| 이미지 | 해상도 기반 토큰 추정 | 85% |
| Excel | 셀 데이터 추출 → 근사치 | 90% |
| 코드 | 언어별 토크나이저 | 95% |

### 3. LLM 모델 관리 (P0 - 필수)

#### 3.1 지원 제공업체
- **OpenAI**: GPT-4o, GPT-4o-mini, GPT-4-turbo, GPT-3.5-turbo, o1-preview, o1-mini
- **Anthropic**: Claude 3 Opus, Claude 3.5 Sonnet, Claude 3 Haiku
- **Google**: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini 1.0 Pro
- **Perplexity**: Llama 3.1 Sonar (Large/Small/Huge)
- **Mistral**: Mistral Large, Medium, Small
- **Cohere**: Command R+, Command R
- **Meta**: Llama 3.1 (405B/70B/8B)

#### 3.2 모델 정보 표시
- 모델명 및 버전
- 입력/출력 토큰당 가격
- 컨텍스트 윈도우 크기
- 특수 기능 (비전, 검색, 함수 호출 등)
- 지역별 가격 차이

### 4. 비용 계산 및 비교 (P0 - 필수)

#### 4.1 계산 항목
- 입력 토큰 비용
- 예상 출력 토큰 비용 (사용자 설정 가능한 비율)
- 총 예상 비용
- 배치 처리 시 절감액

#### 4.2 비교 기능
- 테이블 형태 비교
- 차트 시각화 (막대, 파이)
- 비용 순 정렬
- 성능 대비 비용 효율성 지표

### 5. 미리보기 (P1 - 중요)

#### 5.1 파일 내용 미리보기
- 텍스트 파일: 첫 1000자 표시
- PDF/DOCX: 첫 페이지 텍스트
- 이미지: 썸네일 표시
- Excel: 첫 10행 표시

#### 5.2 토큰 분석 미리보기
- 토큰화된 텍스트 시각화
- 토큰 수 실시간 표시
- 특수 토큰 하이라이트

### 6. 결과 내보내기 (P1 - 중요)

#### 6.1 내보내기 형식
- Excel (.xlsx) - 상세 비교표
- CSV - 데이터 분석용
- PDF - 보고서 형식
- JSON - API 연동용

#### 6.2 내보내기 내용
- 업로드된 파일 정보
- 토큰 계산 상세
- 모든 선택된 모델의 비용
- 추천 모델 및 근거
- 생성 일시 및 메타데이터

### 7. 가격 업데이트 시스템 (P1 - 중요)

#### 7.1 업데이트 방식
- 자동: 24시간마다 크롤링
- 수동: 관리자 대시보드에서 업데이트
- API: 제공업체 API 활용 (가능한 경우)

#### 7.2 가격 이력 관리
- 과거 가격 이력 저장
- 가격 변동 추이 그래프
- 가격 변경 알림

### 8. 사용자 경험 (P2 - 선택)

#### 8.1 프리셋
- 자주 사용하는 모델 조합 저장
- 업계별 추천 프리셋

#### 8.2 고급 설정
- 커스텀 토크나이저 설정
- 출력 토큰 비율 조정
- 배치 크기 최적화

#### 8.3 사용 이력
- 최근 분석 기록
- 즐겨찾기 기능
- 세션 저장/불러오기

---

## 🔧 기술 요구사항

### 프론트엔드
- **프레임워크**: Streamlit 1.30+
- **UI 컴포넌트**: streamlit-dropzone, streamlit-aggrid
- **차트**: Plotly 5.0+
- **스타일**: Streamlit 테마 시스템

### 백엔드
- **언어**: Python 3.11+
- **패키지 관리**: UV
- **토큰 계산**: tiktoken, transformers
- **파일 처리**: PyPDF2, python-docx, openpyxl, Pillow
- **웹 스크래핑**: BeautifulSoup4, requests
- **비동기 처리**: asyncio, aiohttp

### 데이터 저장
- **설정**: YAML 파일
- **캐시**: JSON 파일
- **임시 파일**: tempfile 디렉토리

### 배포
- **로컬**: Streamlit 직접 실행
- **클라우드**: Streamlit Cloud, Heroku, AWS EC2
- **Docker**: 컨테이너화 지원

---

## 📈 성능 요구사항

### 응답 시간
- 파일 업로드: < 2초
- 토큰 계산: < 5초 (10MB 파일 기준)
- 비용 계산: < 1초
- UI 렌더링: < 500ms

### 동시성
- 동시 사용자: 최대 100명
- 동시 파일 처리: 최대 10개

### 정확도
- 토큰 계산 정확도: 95% 이상
- 가격 정보 최신성: 24시간 이내

---

## 🚀 개발 로드맵

### Phase 1 - MVP (2주)
- ✅ 기본 파일 업로드
- ✅ 주요 LLM 모델 5개
- ✅ 텍스트 파일 토큰 계산
- ✅ 비용 비교 테이블

### Phase 2 - 확장 (2주)
- ✅ 모든 파일 타입 지원
- ✅ 20+ LLM 모델
- ✅ 미리보기 기능
- ✅ 내보내기 기능

### Phase 3 - 고도화 (2주)
- ✅ 자동 가격 업데이트
- ✅ 사용자 프리셋
- ✅ 고급 분석 기능
- ✅ API 제공

---

## 📋 검수 기준

### 기능 검수
- [ ] 모든 파일 타입 정상 업로드
- [ ] 토큰 계산 정확도 95% 이상
- [ ] 가격 계산 정확도 100%
- [ ] 내보내기 기능 정상 작동

### 성능 검수
- [ ] 응답 시간 목표 달성
- [ ] 메모리 사용량 < 500MB
- [ ] CPU 사용률 < 50%

### 사용성 검수
- [ ] 직관적인 UI/UX
- [ ] 모바일 반응형 지원
- [ ] 크로스 브라우저 호환성

---

## 🎯 성공 지표

### 정량적 지표
- MAU (월간 활성 사용자): 1,000명
- 일일 파일 처리량: 500개
- 평균 세션 시간: 5분
- 사용자 만족도: 4.5/5.0

### 정성적 지표
- 비용 예측 정확도에 대한 긍정적 피드백
- 다양한 모델 비교 기능의 유용성
- UI의 직관성과 사용 편의성

---

## 📝 참고 자료

### API 문서
- [OpenAI Pricing](https://openai.com/pricing)
- [Anthropic API](https://docs.anthropic.com/claude/reference/getting-started-with-the-api)
- [Google AI Studio](https://ai.google.dev/pricing)
- [Perplexity API](https://docs.perplexity.ai)

### 토큰 계산
- [Tiktoken Library](https://github.com/openai/tiktoken)
- [Tokenizer Playground](https://platform.openai.com/tokenizer)

### 관련 도구
- [OpenAI Pricing Calculator](https://openai.com/pricing#language-models)
- [Anthropic Token Counter](https://console.anthropic.com/tokenizer)