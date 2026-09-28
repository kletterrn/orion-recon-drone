param([string]$Name = 'Compile', [string]$Project = '', [string]$Output = '')
$taskRoot = Split-Path $PSScriptRoot -Parent
if (!$Project) { $Project = Join-Path $taskRoot 'ReconDrones.gproj' }
if (!$Output) { $Output = Join-Path $taskRoot 'BuildRC4' }
$profileDir = Join-Path $taskRoot ('RC4Checks/' + $Name + '-' + (Get-Date -Format 'HHmmss'))
$argsText = '-gproj "' + $Project + '" -addonsDir "C:/Users/david/Documents/My Games/ArmaReforgerWorkbench/addons" -profile "' + $profileDir + '" -wbModule=ResourceManager -packAddon -packAddonDir "' + $Output + '"'
$taskProcess = Start-Process -FilePath 'C:/Steam/steamapps/common/Arma Reforger Tools/Workbench/ArmaReforgerWorkbenchSteamDiag.exe' -ArgumentList $argsText -WorkingDirectory 'C:/Steam/steamapps/common/Arma Reforger' -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 10
$logs = Get-ChildItem -LiteralPath (Join-Path $profileDir 'logs') -Filter console.log -Recurse -ErrorAction SilentlyContinue
foreach ($log in $logs) {
 Write-Output $log.FullName
 Select-String -LiteralPath $log.FullName -Pattern 'SCRIPT    \(E\)|Module: Game;|Cannot|Packing|pack|FBX|error' | Select-Object -Last 18 | ForEach-Object { $_.Line }
}
Write-Output ('Process: ' + $taskProcess.Id)
if ($logs -and (Select-String -LiteralPath $logs[-1].FullName -Pattern 'Can.t compile')) { Stop-Process -Id $taskProcess.Id -ErrorAction SilentlyContinue }

