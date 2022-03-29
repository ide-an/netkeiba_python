#!/bin/bash

OUTPUT=$1
echo  "user_id=${USER_ID}"  "user_pass=${USER_PASS}"  "/data/${OUTPUT}"
scrapy crawl netkeiba -a "user_id=${USER_ID}" -a "user_pass=${USER_PASS}" -o "/data/${OUTPUT}"
