curl -X POST \
-H "Content-Type: application/json" \
-d '{"adversary_id":"4975696e-1d41-11eb-adc1-0242ac120002", "planner_id":"aaa7c857-37a0-4c4a-85f7-4e9f7f30e31a", "extension":".tar.gz"}' \
http://0.0.0.0:8888/plugin/standalone/download --output standalone.tar.gz
