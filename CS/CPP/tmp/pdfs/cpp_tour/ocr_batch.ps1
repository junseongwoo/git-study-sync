param(
    [string]$ImageDirectory,
    [string]$OutputDirectory,
    [int]$StartPage = 1,
    [int]$EndPage = 786
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
[Windows.Storage.StorageFile, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.FileAccessMode, Windows.Storage, ContentType=WindowsRuntime] | Out-Null
[Windows.Storage.Streams.IRandomAccessStream, Windows.Storage.Streams, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Graphics.Imaging.SoftwareBitmap, Windows.Graphics.Imaging, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Media.Ocr.OcrResult, Windows.Foundation, ContentType=WindowsRuntime] | Out-Null
[Windows.Globalization.Language, Windows.Globalization, ContentType=WindowsRuntime] | Out-Null
$script:AsTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.IsGenericMethod -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1'
} | Select-Object -First 1
function Await-Operation($Operation, [Type]$ResultType) {
    $task = $script:AsTask.MakeGenericMethod($ResultType).Invoke($null, @($Operation))
    $task.Wait()
    return $task.Result
}
New-Item -ItemType Directory -Path $OutputDirectory -Force | Out-Null
$jsonDir = Join-Path $OutputDirectory 'lines'
New-Item -ItemType Directory -Path $jsonDir -Force | Out-Null
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage([Windows.Globalization.Language]::new('ko'))
$timer = [Diagnostics.Stopwatch]::StartNew()
$utf8 = [Text.UTF8Encoding]::new($false)
$success = 0
for ($page = $StartPage; $page -le $EndPage; $page++) {
    $stem = '{0:D4}' -f $page
    $sourcePath = Join-Path $ImageDirectory ($stem + '.jpg')
    $textPath = Join-Path $OutputDirectory ($stem + '.txt')
    $jsonPath = Join-Path $jsonDir ($stem + '.json')
    if ((Test-Path -LiteralPath $textPath) -and (Test-Path -LiteralPath $jsonPath)) { $success++; continue }
    $bitmap = $null
    $stream = $null
    try {
        $file = Await-Operation ([Windows.Storage.StorageFile]::GetFileFromPathAsync($sourcePath)) ([Windows.Storage.StorageFile])
        $stream = Await-Operation ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
        $decoder = Await-Operation ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
        $bitmap = Await-Operation ($decoder.GetSoftwareBitmapAsync()) ([Windows.Graphics.Imaging.SoftwareBitmap])
        $result = Await-Operation ($engine.RecognizeAsync($bitmap)) ([Windows.Media.Ocr.OcrResult])
        $lineRecords = @()
        foreach ($line in $result.Lines) {
            $wordRecords = @()
            foreach ($word in $line.Words) {
                $rect = $word.BoundingRect
                $wordRecords += [ordered]@{ text = $word.Text; x = $rect.X; y = $rect.Y; width = $rect.Width; height = $rect.Height }
            }
            $lineRecords += [ordered]@{ text = $line.Text; words = $wordRecords }
        }
        $record = [ordered]@{ page = $page; width = $bitmap.PixelWidth; height = $bitmap.PixelHeight; text_angle = $result.TextAngle; lines = $lineRecords }
        $text = ($lineRecords | ForEach-Object { $_.text }) -join "`n"
        [IO.File]::WriteAllText($textPath, $text, $utf8)
        [IO.File]::WriteAllText($jsonPath, ($record | ConvertTo-Json -Depth 8 -Compress), $utf8)
        $success++
    } catch {
        [IO.File]::AppendAllText((Join-Path $OutputDirectory ('errors_' + $StartPage + '.log')), ($stem + ': ' + $_.Exception.Message + "`n"), $utf8)
    } finally {
        if ($null -ne $bitmap) { $bitmap.Dispose() }
        if ($null -ne $stream) { $stream.Dispose() }
    }
    if (($page - $StartPage + 1) % 20 -eq 0) { Write-Output ("{0}-{1}: page {2}, {3:N1}s" -f $StartPage,$EndPage,$page,$timer.Elapsed.TotalSeconds) }
}
Write-Output ("COMPLETE {0}-{1}: {2} pages, {3:N1}s" -f $StartPage,$EndPage,$success,$timer.Elapsed.TotalSeconds)
