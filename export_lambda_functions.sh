#!/bin/bash
set -e

REPO_DIR="$HOME/AWS-Security-Automation-Project/lambda-functions"

FUNCTIONS=(
"positive-feedback-del-sg-20251106"
"dvwa-alerts-to-ws-20251107"
"sg-open-ssh-ec2-20251105"
"security-alerts-lambda-20251105"
"login-cloudtarail-tamper-20251105"
"impossible-travel-login-20251105"
"security-unusual-region-lambda-20251106"
"accesskey-unusual-geoasn-20251105"
"Config-Rules-Compliance-Change-20251106"
"dvwa-remediation-20251114"
"accesskey-created-alert-20251105"
"Authorize-ssh22-00-20251106"
)

echo "=== Lambda Export 시작 ==="
mkdir -p "$REPO_DIR"

for FN in "${FUNCTIONS[@]}"; do
    echo ""
    echo "[처리 중] $FN"

    URL=$(aws lambda get-function --function-name "$FN" --query 'Code.Location' --output text)

    TARGET_DIR="$REPO_DIR/$FN"
    mkdir -p "$TARGET_DIR"

    echo "다운로드 중..."
    curl -s -o "$TARGET_DIR/function.zip" "$URL"

    unzip -o "$TARGET_DIR/function.zip" -d "$TARGET_DIR" > /dev/null
    rm "$TARGET_DIR/function.zip"

    echo "완료: $FN"
done

echo ""
echo "=== 전체 Lambda Export 완료! ==="
