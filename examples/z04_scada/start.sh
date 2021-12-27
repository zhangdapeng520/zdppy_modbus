ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo Asia/Shanghai > /etc/timezone
cd /app

pip install whls/redis-4.0.2-py3-none-any.whl
pip install whls/aioredis-2.0.0-py3-none-any.whl
pip install whls/zdpapi_modbus-1.7.0-py3-none-any.whl

nohup python main.py 1 50 127.0.0.1 5011 & 
python main.py 51 100 127.0.0.1 5012
