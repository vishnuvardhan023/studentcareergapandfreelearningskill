$ProgressPreference = 'SilentlyContinue'
$url = 'https://github.com/cli/cli/releases/latest/download/gh_2.103.3_windows_amd64.msi'
$dest = Join-Path $env:TEMP 'gh_windows_amd64.msi'
Invoke-WebRequest -Uri $url -OutFile $dest
Start-Process msiexec.exe -ArgumentList '/i', $dest, '/quiet', '/norestart' -Wait -NoNewWindow
$env:Path += ';C:\Program Files\GitHub CLI'
gh --version
