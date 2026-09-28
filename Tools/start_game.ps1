param(
 [Parameter(Mandatory=$true)][string]$GameDirectory,
 [Parameter(Mandatory=$true)][string]$DependencyDirectory,
 [Parameter(Mandatory=$true)][string]$AddonDirectory,
 [Parameter(Mandatory=$true)][string]$ProfileDirectory
)
$ErrorActionPreference = 'Stop'
$gameExe = Join-Path $GameDirectory 'ArmaReforgerSteamDiag.exe'
$addonProject = Join-Path $AddonDirectory 'ReconDrones.gproj'
if (!(Test-Path -LiteralPath $gameExe) -or !(Test-Path -LiteralPath $addonProject)) { throw 'Check the game and packed addon directories.' }
& $gameExe -gproj $addonProject -addons '9B5D39DA127A49B5' -addonsDir $DependencyDirectory -profile $ProfileDirectory -server 'Worlds/ORD/ORD_Runway.ent' -window
