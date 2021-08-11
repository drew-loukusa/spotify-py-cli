if ($args.Count -gt 0){
    $env:USE_DUMMY_WRAPPER='True'
}
else{
    $env:USE_DUMMY_WRAPPER='False'
}
pytest.exe

exit $LASTEXITCODE