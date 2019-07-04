nomad job run -output vmck.nomad > vmck.json # convert hcl to json file for upload on server TODO: custom nomand and json filename
curl -vX POST http://10.66.60.1:4646/v1/jobs -d @vmck.json # HTTP request to nomad to start the job TODO: custom json filename
echo ""
