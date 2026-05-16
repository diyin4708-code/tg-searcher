# WeChat Auto Reply — 模拟点击版
# 通过 PowerShell 操控 Windows 微信桌面端

$wechatTitle = "微信"
$checkInterval = 5  # 每5秒检查一次
$deepseekKey = "sk-096ac189c99840b8ad2d697be34e6131"

Write-Host "🚀 微信自动回复启动"
Write-Host "   检查间隔: ${checkInterval}s"

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

# 加载 Win32 API
$signature = @'
[DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
[DllImport("user32.dll")] public static extern IntPtr FindWindow(string lpClassName, string lpWindowName);
[DllImport("user32.dll")] public static extern void keybd_event(byte bVk, byte bScan, uint dwFlags, UIntPtr dwExtraInfo);
[DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
public struct RECT { public int Left, Top, Right, Bottom; }
'@
Add-Type -MemberDefinition $signature -Name Win32 -Namespace API

function Focus-WeChat {
    $hwnd = [API.Win32]::FindWindow($null, $wechatTitle)
    if ($hwnd -eq [IntPtr]::Zero) {
        Write-Host "❌ 微信未运行"
        return $false
    }
    [API.Win32]::SetForegroundWindow($hwnd)
    Start-Sleep -Milliseconds 300
    return $true
}

function Click-Position($x, $y) {
    [System.Windows.Forms.Cursor]::Position = New-Object System.Drawing.Point($x, $y)
    Start-Sleep -Milliseconds 100
    # 模拟鼠标点击
    [API.Win32]::mouse_event(0x0002, 0, 0, 0, 0) # left down
    Start-Sleep -Milliseconds 50
    [API.Win32]::mouse_event(0x0004, 0, 0, 0, 0) # left up
    Start-Sleep -Milliseconds 200
}

function Send-Text($text) {
    # 模拟键盘输入
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait($text)
}

function Press-Enter {
    [API.Win32]::keybd_event(0x0D, 0, 0, [UIntPtr]::Zero)
    Start-Sleep -Milliseconds 50
    [API.Win32]::keybd_event(0x0D, 0, 2, [UIntPtr]::Zero)
}

function Copy-ChatText {
    # Ctrl+A 全选 → Ctrl+C 复制
    [System.Windows.Forms.SendKeys]::SendWait("^a")
    Start-Sleep -Milliseconds 200
    [System.Windows.Forms.SendKeys]::SendWait("^c")
    Start-Sleep -Milliseconds 300
    return [System.Windows.Forms.Clipboard]::GetText()
}

function Get-DeepSeekReply($message) {
    $body = @{
        model = "deepseek-v4-pro"
        messages = @(
            @{role = "system"; content = "你是微信自动回复助手。简洁、友好、中文回复。不超过100字。"}
            @{role = "user"; content = $message}
        )
        max_tokens = 200
    } | ConvertTo-Json -Depth 3

    try {
        $response = Invoke-RestMethod -Uri "https://api.deepseek.com/v1/chat/completions" `
            -Method Post -Body $body -ContentType "application/json" `
            -Headers @{Authorization = "Bearer $deepseekKey"} `
            -TimeoutSec 15
        return $response.choices[0].message.content
    } catch {
        return "收到，稍后回复你~"
    }
}

function Click-LatestChat {
    # 微信聊天列表第一个对话大概在 (200, 150) 位置
    # 需要根据你的屏幕分辨率调整
    Click-Position 200 120
}

# ═══ 主循环 ═══
Write-Host "✅ 按 Ctrl+C 停止`n"

while ($true) {
    if (-not (Focus-WeChat)) {
        Start-Sleep -Seconds $checkInterval
        continue
    }
    
    # 点击最新聊天
    Click-LatestChat
    Start-Sleep -Milliseconds 500
    
    # 复制最后一条消息
    $msg = Copy-ChatText
    if ($msg -and $msg.Length -gt 2) {
        $lastLine = ($msg -split "`n")[-1].Trim()
        if ($lastLine -and $lastLine.Length -gt 2) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] 收到: $lastLine" -ForegroundColor Cyan
            
            # 获取 AI 回复
            $reply = Get-DeepSeekReply $lastLine
            Write-Host "        回复: $reply" -ForegroundColor Green
            
            # 点击输入框 (微信底部输入区域)
            Click-Position 300 750
            
            # 输入并发送
            Send-Text $reply
            Start-Sleep -Milliseconds 300
            Press-Enter
            Start-Sleep -Milliseconds 500
        }
    }
    
    Start-Sleep -Seconds $checkInterval
}
