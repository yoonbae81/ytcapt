# YT Caption Downloader (ytcapt)

자동 생성된 유튜브 자막을 다운로드하고, 읽기 쉬운 문장으로 정제하여 저장하는 도구입니다.

## 📝 개요

이 프로젝트는 유튜브 비디오의 자동 생성 자막을 처리하기 위한 명령줄 인터페이스(CLI)와 웹 애플리케이션 인터페이스를 모두 제공합니다. 조각난 자막 라인을 일관성 있는 문단으로 변환하는 것이 핵심 기능입니다.

## ✨ 주요 기능

- **웹 인터페이스**: [Bottle](https://bottlepy.org)과 [Pico CSS](https://picocss.com)를 사용한 가볍고 깔끔한 웹 UI.
- **자막 정제**: 조각난 라인을 완전한 문장과 문단으로 병합.
- **캐싱**: 다운로드한 데이터를 7일간 캐싱하여 효율성 향상.
- **다국어 지원**: 한국어 정제 규칙 및 기본 영어 지원.
- **표준화된 구조**: Scripter 표준 프로젝트 구조 및 배포 방식 적용.

## 🛠️ 설치 및 설정

### 사전 요구사항

- Python 3.12 이상
- pip

### 설정 (Setup)

```bash
# 저장소 클론
git clone https://github.com/yoonbae81/ytcapt.git
cd ytcapt

# 환경 설정 스크립트 실행 (venv 생성 및 의존성 설치)
./scripts/setup-env.sh

# 환경 변수 설정
cp .env.example .env
# 필요한 경우 .env 파일 수정
```

## ⚙️ 사용법

### 1. 명령줄 인터페이스 (CLI)

```bash
# 기본 사용법 (한국어)
./scripts/run.sh "https://www.youtube.com/watch?v=XXXXXXXXXXX"

# 언어 지정 (영어)
./scripts/run.sh "https://www.youtube.com/watch?v=XXXXXXXXXXX" -l en
```

### 2. 웹 애플리케이션

```bash
# 웹 서버 실행
./scripts/run.sh

# 메인 서비스로 설치 (Linux/systemd)
./scripts/install-systemd.sh
```

접속: `http://localhost:9822/ytcapt/`

## 📂 프로젝트 구조

```
ytcapt/
├── src/                # Python 소스 코드
│   ├── app.py          # 웹 애플리케이션 엔트리포인트
│   ├── ytcapt.py       # 핵심 로직 및 CLI 모듈
│   ├── main.py         # Reporting 기능이 통합된 CLI 래퍼
│   ├── refiners/       # 언어별 정제 규칙
│   └── views/          # 웹 템플릿
├── tests/              # 테스트 코드
├── scripts/            # 실행 및 배포 스크립트
│   ├── setup-env.sh    # 환경 설정
│   ├── install-systemd.sh # 서비스 설치
│   ├── deploy.sh       # 배포
│   └── run.sh          # 실행
├── requirements.txt    # 의존성 목록
├── .env.example        # 환경 변수 템플릿
└── README.md           # 프로젝트 문서
```

## 🧪 테스트

```bash
# 모든 테스트 실행
python3 -m unittest discover tests
```

## 📄 라이선스

MIT License
