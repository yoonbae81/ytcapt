# YT Caption Downloader

온라인 비디오의 자동 생성 자막을 다운로드하고, 정제하며, 구조화합니다.

## 📝 개요

이 프로젝트는 비디오 플랫폼의 자동 생성 자막을 다운로드하고 처리하기 위한 명령줄 인터페이스(CLI)와 웹 애플리케이션 인터페이스([Bottle](https://bottlepy.org) 사용)를 모두 제공합니다. 핵심 기능은 조각난 타임스탬프 자막 라인을 일관성 있고 읽기 쉬운 문단으로 변환(정제)하는 것입니다.

## 핵심 아키텍처

프로젝트는 유연한 아키텍처를 유지합니다:

`ytcapt.py`: 자막을 가져오고, 캐싱하고, 정제하는 핵심 로직을 포함합니다. 독립 실행형 CLI 도구이자 app.py의 라이브러리 모듈로 작동합니다.

`app.py`: `ytcapt.py`의 로직을 가져와 사용자 친화적인 웹 인터페이스를 제공하는 경량 [Bottle](https://bottlepy.org) 애플리케이션입니다.

`refiners/`: 언어별 정제 규칙 패키지입니다 (현재 `refine_ko.py`와 기본 영어 로직만 제공).

## ✨ 주요 기능

- **Docker 배포**: 자동 업데이트 기능, 스마트 의존성 관리, 프로덕션 준비 설정을 갖춘 완전한 Docker 지원.

- **웹 인터페이스 (Bottle)**: 간단하고 반응형이며 자동 테마 적용되는 CSS 프레임워크([Pico](https://picocss.com))를 제공하여 사용이 편리합니다.

- **자막 정제**: 조각난 라인을 완전한 문장과 문단으로 병합하여 읽기나 분석에 적합한 텍스트를 생성합니다.

- **타겟 다운로드**: 거의 모든 비디오에서 사용 가능한 자동 생성 자막만을 엄격하게 타겟팅하여 높은 호환성을 보장하고 추출 성공 가능성을 극대화합니다.

- **오류 처리**: 특히 "HTTP 429: Too Many Requests"에 대해 사용자 친화적인 오류 메시지를 제공하며, 이는 비디오 플랫폼의 지역/IP 제한 문제를 나타냅니다.

- **캐싱**: 비디오 ID를 기반으로 다운로드한 텍스트 파일(자막 및 제목)을 7일간 캐싱하여 불필요한 네트워크 요청과 처리 시간을 줄입니다.

- **다운로드 헤더**: 다운로드한 .txt 파일의 처음 두 줄에 원본 비디오 제목과 URL을 포함하여 출처 추적이 용이합니다.

- **강력한 파일 이름 처리**: 비디오 제목을 정제하여 공백을 유지하면서 파일 시스템에 안전한 깔끔한 다운로드 이름을 생성합니다.

## 🛠️ 설치 및 설정

### 옵션 1: Portainer Stack (프로덕션 권장)

Portainer를 사용하여 웹 UI에서 쉽게 배포하고 관리할 수 있습니다.

#### 사전 준비

**Portainer 설치**
- Portainer가 서버에 설치되어 있어야 합니다
- https://docs.portainer.io/start/install 참조

#### 배포 단계

1. **Portainer 웹 UI 접속**
   - 브라우저에서 Portainer에 로그인

2. **Stacks 메뉴로 이동**
   - 좌측 메뉴에서 `Stacks` 클릭
   - `+ Add stack` 버튼 클릭

3. **Stack 설정**
   - **Name**: `ytcapt` 입력
   - **Build method**: `Repository` 선택

4. **Repository 설정**
   - **Repository URL**: `https://github.com/yoonbae81/ytcapt`
   - **Repository reference**: `refs/heads/main`
   - **Compose path**: `docker-compose.yml`
   - **Authentication**: 공개 저장소이므로 불필요

5. **환경 변수 (선택사항)**
   
   Environment variables 섹션에서 추가 가능:
   ```
   PRODUCTION_MODE=true
   ```

6. **Deploy the stack**
   - 하단의 `Deploy the stack` 버튼 클릭
   - Portainer가 자동으로:
     1. GitHub에서 코드 clone
     2. Dockerfile로 이미지 빌드 (1-2분 소요)
     3. 컨테이너 실행

7. **빌드 진행 확인**
   - Stack 배포 후 `Logs` 탭에서 빌드 진행 상황 확인

#### 접속

브라우저에서 다음 URL로 접속:
```
http://서버IP:8001/ytcapt/
```

#### 환경 변수

| 변수명 | 기본값 | 설명 |
|--------|--------|------|
| `PRODUCTION_MODE` | `true` | 프로덕션 모드 활성화 (`false`로 설정 시 개발 모드) |

**참고:** 컨테이너 내부 포트는 8000으로 고정되어 있습니다. 외부 포트만 `ports` 매핑에서 변경 가능합니다.

#### 업데이트 방법

컨테이너를 재시작하면 자동으로 최신 코드를 pull합니다:

1. Portainer UI에서 `Containers` 메뉴로 이동
2. `ytcapt` 컨테이너 선택
3. `Restart` 버튼 클릭

#### 문제 해결

**컨테이너가 시작되지 않는 경우:**

1. **로그 확인**
   - Portainer에서 컨테이너 로그 확인

2. **포트 충돌 확인**
   ```bash
   sudo netstat -tulpn | grep 8001
   ```

3. **이미지 재빌드**
   - Portainer에서 Stack 삭제 후 재배포

### 옵션 2: Docker Compose (로컬 개발)

로컬 개발 환경에서 Docker Compose를 사용합니다.

**사전 요구사항:**
- Docker 및 Docker Compose 설치

**빠른 시작:**
```bash
git clone https://github.com/yoonbae81/ytcapt
cd ytcapt
docker-compose up -d
```

애플리케이션은 다음과 같이 동작합니다:
- 컨테이너 시작 시 GitHub에서 최신 코드를 자동으로 pull
- `requirements.txt`가 변경될 때만 의존성 설치
- 기본적으로 프로덕션 모드로 실행
- 컨테이너 내부는 8000번 포트, 외부 접속은 http://localhost:8001/ytcapt/

**Docker 명령어:**
```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 재시작 (최신 코드 pull)
docker-compose restart

# 서비스 중지
docker-compose down
```

### 옵션 3: 로컬 Python 설치

개발 또는 직접 Python 실행을 위한 방법입니다.

**사전 요구사항:**
- Python 3.9+ (Python 3.12+ 권장)

**참고:** 로컬 실행 시 기본 포트는 8000번입니다.

**설정:**
```bash
git clone https://github.com/yoonbae81/ytcapt
cd ytcapt
pip install -r requirements.txt
```

## ⚙️ 사용법

### A. 웹 애플리케이션 (권장)

웹 앱을 통해 브라우저에서 모든 기능에 쉽게 접근할 수 있습니다.

**1. 서버 실행:**

Docker 사용 (권장):
```bash
docker-compose up -d
```

또는 Python으로 직접 실행:
```bash
cd src
python app.py
```

커스텀 포트 사용:
```bash
python app.py --port 8080
```

프로덕션 모드로 실행:
```bash
python app.py --port 8000 --production
```

**2. 애플리케이션 접속:**

- Docker: http://localhost:8001/ytcapt/ (외부 포트)
- 로컬: http://localhost:8000/ytcapt/ (또는 설정한 포트)

**3. 사용 방법:**

- 비디오 URL을 입력합니다.
- 대상 언어를 선택합니다 (한국어 또는 영어).
- 앱이 정제된 텍스트를 표시합니다.
- 다운로드 버튼을 클릭하면 비디오 제목에서 파생된 안전한 파일명으로 콘텐츠가 저장됩니다.

### B. 명령줄 인터페이스 (CLI)

스크립트 자동화나 배치 처리를 위해 `ytcapt.py`를 직접 사용할 수 있습니다 (단일 비디오만 지원).

1. 기본 사용법 (한국어):
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX"
```

2. 언어 지정 (영어):
--lang 또는 -l 옵션을 사용합니다.
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX" -l en
```

3. 강제 다운로드 (캐시 무시):
--force-dl 또는 -f 옵션을 사용합니다.
```
python ytcapt.py "https://example.com/video?v=XXXXXXXXXXX" -f
```

## 📂 프로젝트 구조

```
/ytcapt
|
|-- Dockerfile             # Docker 이미지 설정
|-- docker-compose.yml     # Docker Compose / Portainer Stack 설정
|-- entrypoint.sh          # 자동 업데이트 기능이 있는 컨테이너 시작 스크립트
|-- requirements.txt       # Python 의존성
|
|-- src/
|   |-- app.py             # Bottle 웹 서버 애플리케이션
|   |-- ytcapt.py          # 핵심 로직 모듈 및 CLI 스크립트
|   |
|   |-- refiners/          # 언어별 정제 규칙 패키지
|   |   |-- __init__.py    # Python 패키지로 만들기
|   |   +-- refine_ko.py   # 한국어 문장 정제 규칙
|   |
|   +-- views/             # Bottle 템플릿 (Pico CSS 적용)
|       |-- home.tpl       # URL 및 언어 입력 폼
|       +-- result.tpl     # 정제된 텍스트 및 다운로드 링크 표시
```
