# 🧮 LLM API Cost Calculator

> 다양한 LLM API의 사용 비용을 미리 계산하고 비교할 수 있는 스마트한 비용 계산기

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 📌 개요

PDF, Excel, 이미지 등 다양한 파일을 업로드하면 자동으로 토큰 수를 계산하고, 여러 LLM 모델의 예상 API 비용을 한눈에 비교할 수 있는 웹 애플리케이션입니다.

### ✨ 주요 기능

- 🎯 **다양한 파일 지원**: PDF, Excel, Word, 이미지, 텍스트 등
- 🔢 **정확한 토큰 계산**: tiktoken 및 파일별 최적화된 계산 방식
- 💰 **실시간 비용 비교**: 20+ LLM 모델의 비용을 한번에 비교
- 📊 **시각화**: 차트와 테이블로 직관적인 비교
- 🔄 **자동 가격 업데이트**: 최신 API 가격 정보 자동 반영
- 📥 **결과 내보내기**: Excel, CSV, PDF 형식으로 다운로드

## 🚀 빠른 시작

### 사전 요구사항

- Python 3.11+
- UV (Python 패키지 매니저)

### 설치

```bash
# 저장소 클론
git clone https://github.com/dexelop/api_cost.git
cd api_cost

# UV로 의존성 설치
uv sync

# 환경 변수 설정
cp .env.example .env
```

### 실행

```bash
# Streamlit 앱 실행
uv run streamlit run app.py
```

브라우저에서 `http://localhost:8501` 접속

## 🏗️ 프로젝트 구조

```
api_cost/
├── app.py                    # Streamlit 메인 앱
├── requirements.txt          # 의존성 목록
├── pyproject.toml           # UV 프로젝트 설정
├── config/
│   ├── models.yaml          # LLM 모델 정보 & 가격
│   └── settings.py          # 앱 설정
├── src/
│   ├── tokenizers/          # 토큰 계산 모듈
│   ├── processors/          # 파일 처리 모듈
│   ├── pricing/             # 가격 관리 모듈
│   └── ui/                  # UI 컴포넌트
├── data/                    # 데이터 저장
└── docs/
    └── PRD.md              # 제품 요구사항 문서
```

## 📊 지원 LLM 모델

### OpenAI
- GPT-4o, GPT-4o-mini
- GPT-4 Turbo, GPT-3.5 Turbo
- o1-preview, o1-mini

### Anthropic
- Claude 3 Opus
- Claude 3.5 Sonnet
- Claude 3 Haiku

### Google
- Gemini 1.5 Pro
- Gemini 1.5 Flash
- Gemini 1.0 Pro

### Perplexity
- Llama 3.1 Sonar (Large/Small/Huge)

### Mistral
- Mistral Large/Medium/Small

## 📁 지원 파일 형식

| 카테고리 | 지원 형식 |
|---------|----------|
| 문서 | PDF, DOCX, TXT, MD |
| 데이터 | XLSX, CSV, JSON |
| 이미지 | PNG, JPG, JPEG, GIF, WEBP |
| 코드 | PY, JS, TS, JAVA, CPP, GO, etc. |

## 🎯 사용 예시

1. **파일 업로드**: 드래그앤드롭 또는 파일 선택
2. **모델 선택**: 비교하고 싶은 LLM 모델들 선택
3. **결과 확인**: 토큰 수와 예상 비용 즉시 확인
4. **내보내기**: 필요 시 Excel/PDF로 다운로드

## 🛠️ 개발 가이드

### 로컬 개발

```bash
# 개발 모드 실행
uv run streamlit run app.py --server.runOnSave true

# 테스트 실행
uv run pytest tests/

# 코드 포맷팅
uv run black src/ tests/
uv run isort src/ tests/
```

### 새로운 LLM 모델 추가

`config/models.yaml`에 모델 정보 추가:

```yaml
providers:
  your_provider:
    name: "Your Provider"
    models:
      your_model:
        name: "Your Model"
        input_price: 0.001  # per 1K tokens
        output_price: 0.002
        context_window: 128000
```

## 📈 로드맵

- [x] MVP - 기본 파일 업로드 및 비용 계산
- [x] 다양한 파일 형식 지원
- [ ] 배치 처리 최적화
- [ ] API 키를 통한 실제 잔액 조회
- [ ] 사용 이력 추적 및 분석
- [ ] REST API 제공

## 🤝 기여하기

기여는 언제나 환영합니다! 다음 절차를 따라주세요:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 문의

- GitHub Issues: [문제 보고](https://github.com/dexelop/api_cost/issues)
- Email: your.email@example.com

## 🙏 감사의 말

- [OpenAI](https://openai.com/) - tiktoken 라이브러리
- [Streamlit](https://streamlit.io/) - 웹 프레임워크
- 모든 오픈소스 컨트리뷰터들

---

Made with ❤️ by [dexelop](https://github.com/dexelop)
