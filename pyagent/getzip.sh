curl -X POST \
-H "Content-Type: application/json" \
-d '{"adversary_id":"1d3ed5ab-cfd8-4e42-9cda-ab375e9b75d6", "planner_id":"aaa7c857-37a0-4c4a-85f7-4e9f7f30e31a", "extension":".zip"}' \
http://0.0.0.0:8888/plugin/standalone/download --output standalone.zip
