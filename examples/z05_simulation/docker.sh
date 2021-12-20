mypwd=$(pwd)
# project="${mypwd}/v1"
# api="${project}/api"

docker run -itd --restart=always --privileged=true --name hz_lagrange_simulation --volume $mypwd:/app -v /var/run/docker.sock:/var/run/docker.sock base_python37:0.9 sh -c "/bin/bash /app/start.sh"