ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
echo Asia/Shanghai > /etc/timezone
cd /app

pip install whls/redis-4.0.2-py3-none-any.whl
pip install whls/aioredis-2.0.0-py3-none-any.whl
pip install whls/zdpapi_modbus-1.6.0-py3-none-any.whl

nohup python main.py 5011 50 & 
python main.py 5012 50