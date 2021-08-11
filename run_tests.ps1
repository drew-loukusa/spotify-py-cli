if ($args.Count -gt 0){
    $env:USE_DUMMY_WRAPPER='False'
}
else{
    $env:USE_DUMMY_WRAPPER='True'
}
pytest.exe

exit $LASTEXITCODE