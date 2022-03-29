#!/bin/bash

OUTPUT=$1
scrapy crawl netkeiba -a "user_id=${USER_ID}" -a "user_pass=${USER_PASS}" -o "/data/${OUTPUT}"
