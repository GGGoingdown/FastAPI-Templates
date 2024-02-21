#!/bin/bash

# 檢查 .env 文件是否存在
if [ ! -f ".env" ]; then
    # 如果 .env 文件不存在，則從 .env.test 複製
    cp .env.test .env
fi


# 檢查文件中是否含有 APP_ENVIRONMENT=testing
grep -q 'APP_ENVIRONMENT=testing' .env
if [ $? -eq 0 ]; then
    # 如果存在，則將 APP_ENVIRONMENT 的值改為 development
    sed -i 's/APP_ENVIRONMENT=testing/APP_ENVIRONMENT=development/' .env
else
    # 如果不存在，可能需要添加或忽略
    echo "APP_ENVIRONMENT=testing not found in .env, no changes made."
fi


# 檢查文件中是否含有 PG_HOST=localhost
grep -q 'PG_HOST=localhost' .env
if [ $? -eq 0 ]; then
    # 如果存在，則將 PG_HOST 的值改為 db
    sed -i 's/PG_HOST=localhost/PG_HOST=db/' .env
else
    # 如果不存在，可能需要添加或忽略
    echo "PG_HOST=localhost not found in .env, no changes made."
fi


# 檢查文件中是否含有 REDIS_HOST=localhost
grep -q 'REDIS_HOST=localhost' .env
if [ $? -eq 0 ]; then
    # 如果存在，則將 REDIS_HOST 的值改為 cache
    sed -i 's/REDIS_HOST=localhost/REDIS_HOST=cache/' .env
else
    # 如果不存在，可能需要添加或忽略
    echo "REDIS_HOST=localhost not found in .env, no changes made."
fi
