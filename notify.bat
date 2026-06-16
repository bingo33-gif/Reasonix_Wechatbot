@echo off
chcp 65001 >/dev/null 2>&1
:: ============================================
::  R仔微信通知助手 v1.0
::  用法: notify "你的消息"
::  示例: notify "数据处理完成！"
:: ============================================

if "%~1"=="" (
    echo.
    echo ⚠️  用法: notify "通知内容"
    echo 示例: notify "任务完成啦！"
    echo.
    exit /b 1
)

echo 📤 正在发送通知...
npx weixin-mcp send o9cq80wFPVODhOqJalj3cj8lfHUU@im.wechat "%~1" 2>&1

if %errorlevel% equ 0 (
    echo ✅ 通知已发送到微信！
) else (
    echo ❌ 发送失败，请检查 weixin-mcp 是否运行：npx weixin-mcp status
)
