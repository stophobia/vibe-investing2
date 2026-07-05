#!/usr/bin/env bash
# toss-qlib-middleware 환경설정 스크립트.
# TOSS_CLIENT_ID/SECRET 등 자격증명을 대화형으로 입력받아 .env를 생성하고
# (권한 600), 원하면 실제 토큰 발급까지 즉시 테스트한다.
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_FILE=".env"

if [[ -f "$ENV_FILE" ]]; then
  read -r -p ".env 파일이 이미 있습니다. 덮어쓸까요? [y/N] " overwrite
  if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
    echo "취소했습니다. 기존 .env를 유지합니다."
    exit 0
  fi
fi

echo "== toss-qlib-middleware 환경설정 =="
echo "Client ID/Secret은 토스증권 WTS 로그인 후 설정 > Open API 메뉴에서 발급받습니다."
echo "(발급 전이라면 https://developers.tossinvest.com/docs 참고)"
echo

read -r -p "TOSS_CLIENT_ID: " TOSS_CLIENT_ID
read -r -s -p "TOSS_CLIENT_SECRET (입력값은 화면에 표시되지 않습니다): " TOSS_CLIENT_SECRET
echo
read -r -p "TOSS_BASE_URL [https://openapi.tossinvest.com]: " TOSS_BASE_URL_INPUT
TOSS_BASE_URL=${TOSS_BASE_URL_INPUT:-https://openapi.tossinvest.com}
read -r -p "REDIS_URL [redis://127.0.0.1:6379]: " REDIS_URL_INPUT
REDIS_URL=${REDIS_URL_INPUT:-redis://127.0.0.1:6379}
read -r -p "PORT [4000]: " PORT_INPUT
PORT=${PORT_INPUT:-4000}
read -r -p "QLIB_CSV_EXPORT_DIR [./csv_kr]: " QLIB_DIR_INPUT
QLIB_CSV_EXPORT_DIR=${QLIB_DIR_INPUT:-./csv_kr}

cat > "$ENV_FILE" <<EOF
PORT=${PORT}

# 토스증권 WTS > 설정 > Open API 에서 발급받은 값
TOSS_CLIENT_ID=${TOSS_CLIENT_ID}
TOSS_CLIENT_SECRET=${TOSS_CLIENT_SECRET}
TOSS_BASE_URL=${TOSS_BASE_URL}
TOSS_TOKEN_PATH=/oauth2/token
TOSS_CANDLES_PATH=/api/v1/candles
TOSS_PRICES_PATH=/api/v1/prices

REDIS_URL=${REDIS_URL}

# 토큰 유효기간 24시간, refresh token 없음 — 선제 재발급 안전마진(초)
TOKEN_SAFETY_MARGIN_SEC=3600
CANDLE_TTL_HISTORICAL_SEC=86400
CANDLE_TTL_TODAY_SEC=30
PRICE_TTL_SEC=5
INSTRUMENTS_TTL_SEC=86400

QLIB_CSV_EXPORT_DIR=${QLIB_CSV_EXPORT_DIR}
EOF

chmod 600 "$ENV_FILE"
echo
echo ".env 생성 완료 (권한 600 — 소유자만 읽기/쓰기 가능)."

if [[ -n "$TOSS_CLIENT_ID" && -n "$TOSS_CLIENT_SECRET" ]]; then
  echo
  read -r -p "지금 자격증명으로 토큰 발급을 테스트해볼까요? [Y/n] " test_now
  if [[ ! "$test_now" =~ ^[Nn]$ ]]; then
    id_file=$(mktemp)
    secret_file=$(mktemp)
    resp_file=$(mktemp)
    trap 'rm -f "$id_file" "$secret_file" "$resp_file"' EXIT
    chmod 600 "$id_file" "$secret_file" "$resp_file"
    # ps 등에 시크릿이 노출되지 않도록 curl --data-urlencode name@file 형태로 전달한다.
    printf '%s' "$TOSS_CLIENT_ID" > "$id_file"
    printf '%s' "$TOSS_CLIENT_SECRET" > "$secret_file"

    echo "토큰 발급 테스트 중 (POST ${TOSS_BASE_URL}/oauth2/token)..."
    status=$(curl -sS -o "$resp_file" -w '%{http_code}' -X POST "${TOSS_BASE_URL}/oauth2/token" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      --data-urlencode "grant_type=client_credentials" \
      --data-urlencode "client_id@${id_file}" \
      --data-urlencode "client_secret@${secret_file}") || status="000"

    if [[ "$status" == "200" ]] && grep -q "access_token" "$resp_file"; then
      echo "성공: 토큰 발급이 정상적으로 됐습니다."
    else
      echo "실패 (HTTP ${status}). TOSS_CLIENT_ID/SECRET 또는 TOSS_BASE_URL을 다시 확인하세요."
      echo "응답 본문: $(cat "$resp_file")"
    fi
  fi
fi

echo
echo "다음 단계:"
echo "  npm install"
echo "  npm test"
echo "  npm run dev      # http://localhost:${PORT}"
