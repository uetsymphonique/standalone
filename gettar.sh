curl -X POST \
-H "Content-Type: application/json" \
-d '{"adversary_id":"23ee980e-f0c5-4e88-a02c-56aa862b2c76", "planner_id":"aaa7c857-37a0-4c4a-85f7-4e9f7f30e31a", "extension":".tar.gz", "platform":"linux", "obfuscator":"base64", "source_id":"ed32b9c3-9593-4c33-b0db-e2007315096b"}' \
http://0.0.0.0:8888/plugin/standalone/download --output standalone.tar.gz
