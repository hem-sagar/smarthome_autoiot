$python = "C:\Users\hemsa\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
$workdir = Split-Path -Parent $MyInvocation.MyCommand.Path

$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $python
$psi.Arguments = "-m streamlit run dashboard.py --server.headless true --server.port 8501"
$psi.WorkingDirectory = $workdir
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true

$process = New-Object System.Diagnostics.Process
$process.StartInfo = $psi
$null = $process.Start()
