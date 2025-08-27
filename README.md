# 📊 재무제표 시각화 분석툴

한국의 전자공시시스템 OpenDart API를 활용한 웹 기반 재무제표 시각화 및 AI 분석 도구입니다.

## ✨ 주요 기능

- 🔍 **기업 검색**: 20,000+ 한국 기업 데이터베이스에서 빠른 검색
- 📈 **재무제표 시각화**: 손익계산서, 재무상태표 데이터를 직관적으로 표시
- 🤖 **AI 재무분석**: Google Gemini AI를 활용한 재무 상태 분석 및 인사이트
- 📱 **반응형 웹UI**: 모바일과 데스크톱 모든 환경에서 최적화된 사용자 경험
- 📊 **주요 재무지표**: 부채비율, 영업이익률, 순이익률 등 핵심 지표 자동 계산

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하세요:

```bash
# 필수: OpenDart API 키
OPENDART_API_KEY=your_opendart_api_key_here

# 선택사항: AI 분석 기능 (Gemini API 키)
GEMINI_API_KEY=your_gemini_api_key_here
```

#### API 키 발급 방법
- **OpenDart API**: [OpenDart 홈페이지](https://opendart.fss.or.kr/)에서 무료 발급
- **Gemini API**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 무료 발급

### 3. 데이터베이스 초기화

```bash
python database_setup.py
```

### 4. 웹 서버 실행

```bash
python app.py
```

웹 브라우저에서 `http://localhost:5000`으로 접속하세요.

## 📁 프로젝트 구조

```
financial-analyzer/
├── 🌐 웹 애플리케이션
│   ├── app.py                     # Flask 메인 서버
│   ├── templates/
│   │   └── index.html            # 메인 웹페이지
│   └── static/
│       ├── css/style.css         # 스타일시트
│       └── js/app.js             # 프론트엔드 JavaScript
│
├── 🔧 핵심 모듈
│   ├── database_setup.py         # 기업 데이터베이스 관리
│   ├── opendart_example.py       # OpenDart API 클래스
│   ├── ai_financial_analyzer.py  # AI 분석 엔진
│   └── company_search.py         # 기업 검색 유틸리티
│
├── 📊 데이터
│   ├── companies.db              # SQLite 기업 데이터베이스
│   ├── corp_codes.json          # 기업 코드 JSON
│   └── corp_codes.xml           # 기업 코드 원본 XML
│
├── ⚙️ 설정
│   ├── requirements.txt          # Python 의존성
│   ├── .env                     # 환경 변수 (생성 필요)
│   ├── .gitignore              # Git 제외 파일
│   └── README.md               # 프로젝트 문서
│
└── 🛠️ 유틸리티
    └── convert_to_json.py       # XML to JSON 변환기
```

## 🖥️ 사용법

### 웹 인터페이스
1. `http://localhost:5000`에 접속
2. 검색창에 기업명 입력 (예: "삼성전자", "LG전자")
3. 검색 결과에서 원하는 기업 선택
4. 재무제표 데이터 및 시각화 확인
5. AI 분석 버튼 클릭으로 심층 분석 보고서 생성

### API 엔드포인트
- `GET /api/search?q={기업명}`: 기업 검색
- `GET /api/company/{corp_code}`: 기업 정보 조회
- `GET /api/financial/{corp_code}?year={연도}`: 재무제표 조회
- `GET /api/ai-analysis/{corp_code}?year={연도}`: AI 분석 보고서
- `GET /api/stats`: 데이터베이스 통계

### 명령행 도구
```bash
# 기업 검색
python company_search.py "삼성전자"

# 데이터베이스 재구성
python database_setup.py

# OpenDart API 테스트
python opendart_example.py
```

## 📊 제공 데이터

### 기업 정보 (20,000+ 기업)
- **기본 정보**: 회사명, 영문명, 고유번호, 종목코드
- **업종 분류**: 한국표준산업분류 기준
- **상장 정보**: 상장여부, 시장구분 (KOSPI/KOSDAQ)

### 재무제표 데이터
#### 재무상태표 (Balance Sheet)
- 자산총계, 유동자산, 비유동자산
- 부채총계, 유동부채, 비유동부채
- 자본총계, 자본금, 이익잉여금

#### 손익계산서 (Income Statement)
- 매출액, 매출원가, 매출총이익
- 영업이익, 영업외수익/비용
- 법인세차감전 순이익, 당기순이익

### AI 분석 리포트
- **재무건전성 평가**: 부채비율, 유동비율 등 안전성 지표
- **수익성 분석**: 영업이익률, 순이익률, ROE, ROA
- **성장성 평가**: 매출액 증가율, 이익 증가율
- **투자 인사이트**: AI 기반 투자 관점 및 위험 요소 분석

## 🔧 기술 스택

- **백엔드**: Python 3.8+, Flask, SQLite
- **프론트엔드**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Google Gemini API
- **데이터 소스**: 금융감독원 OpenDart API
- **시각화**: Chart.js, Custom CSS

## 🔒 보안 및 개인정보

- ✅ API 키는 환경변수로 안전하게 관리
- ✅ 개인정보 수집하지 않음
- ✅ 공개 재무정보만 활용
- ✅ HTTPS 지원 (배포시)

## 🛠️ 문제 해결

### 일반적인 문제
```bash
# 의존성 설치 오류
pip install --upgrade pip
pip install -r requirements.txt

# 데이터베이스 초기화 오류
python database_setup.py

# 포트 충돌 (5000번 포트 사용중)
python app.py --port 8000
```

### API 관련 오류
| 오류 메시지 | 해결 방법 |
|------------|----------|
| `OPENDART_API_KEY not found` | `.env` 파일에 API 키 추가 |
| `조회된 데이터가 없습니다` | 기업명, 연도 확인 |
| `AI 분석 기능이 비활성화` | `GEMINI_API_KEY` 환경변수 설정 |

## 🤝 기여하기

1. 이 저장소를 Fork 하세요
2. 새로운 기능 브랜치를 만드세요 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋하세요 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시하세요 (`git push origin feature/amazing-feature`)
5. Pull Request를 만드세요

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 `LICENSE` 파일을 참조하세요.

## 🙏 감사의 말

- [금융감독원](https://www.fss.or.kr/) - OpenDart API 제공
- [Google](https://ai.google.dev/) - Gemini AI API 제공
- 오픈소스 커뮤니티의 모든 기여자들

## 📞 연락처

프로젝트에 대한 질문이나 제안사항이 있으시면 이슈를 생성해주세요.

---

⭐ 이 프로젝트가 도움이 되셨다면 스타를 눌러주세요!
