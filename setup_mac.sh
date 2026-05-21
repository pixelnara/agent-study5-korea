#!/bin/bash
# ============================================================
# 글로벌 일일 브리핑 - 맥북 자동화 설정 스크립트
# 터미널에서 아래 명령어로 실행하세요:
#   chmod +x setup_mac.sh && ./setup_mac.sh
# ============================================================

set -e  # 오류 발생 시 즉시 중단

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON=$(which python3)
PLIST_NAME="com.dailybriefing.agent"
PLIST_PATH="$HOME/Library/LaunchAgents/$PLIST_NAME.plist"
LOG_DIR="$PROJECT_DIR/logs"

echo ""
echo "============================================"
echo "  글로벌 일일 브리핑 자동화 설정 시작"
echo "============================================"
echo ""

# 로그 폴더 생성
mkdir -p "$LOG_DIR"

# Python 확인
echo "✅ Python 경로: $PYTHON"
echo "✅ 프로젝트 경로: $PROJECT_DIR"

# 패키지 설치
echo ""
echo "📦 필요한 패키지 설치 중..."
pip3 install -r "$PROJECT_DIR/requirements.txt" --quiet
echo "✅ 패키지 설치 완료"

# .env 파일 확인
if [ ! -f "$PROJECT_DIR/.env" ]; then
    echo ""
    echo "⚠️  .env 파일이 없습니다!"
    echo "   .env.example 파일을 복사해서 .env 를 만들고"
    echo "   API 키를 입력한 후 다시 실행하세요."
    echo ""
    echo "   cp .env.example .env"
    echo "   그리고 .env 파일을 텍스트 에디터로 열어 값을 채우세요."
    exit 1
fi
echo "✅ .env 파일 확인됨"

# launchd plist 생성 (매일 오전 09:55 실행)
echo ""
echo "⏰ 자동 실행 스케줄 등록 중 (매일 오전 09:55)..."

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${PLIST_NAME}</string>

    <key>ProgramArguments</key>
    <array>
        <string>${PYTHON}</string>
        <string>${PROJECT_DIR}/main.py</string>
    </array>

    <key>WorkingDirectory</key>
    <string>${PROJECT_DIR}</string>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>55</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>${LOG_DIR}/briefing.log</string>

    <key>StandardErrorPath</key>
    <string>${LOG_DIR}/briefing_error.log</string>

    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/usr/bin:/bin:/opt/homebrew/bin</string>
    </dict>
</dict>
</plist>
EOF

# 기존 등록된 경우 해제 후 재등록
launchctl unload "$PLIST_PATH" 2>/dev/null || true
launchctl load "$PLIST_PATH"

echo "✅ 자동 실행 등록 완료!"
echo ""
echo "============================================"
echo "  설정 완료 요약"
echo "============================================"
echo "  실행 시간  : 매일 오전 09:55"
echo "  로그 파일  : $LOG_DIR/briefing.log"
echo "  오류 로그  : $LOG_DIR/briefing_error.log"
echo ""
echo "  지금 바로 테스트하려면:"
echo "  python3 main.py"
echo ""
echo "  자동 실행을 중단하려면:"
echo "  launchctl unload $PLIST_PATH"
echo "============================================"
