#MongoDB 드라이버 추가
python3 -m pip install 'pymongo[srv]'
Ubuntu 메모리 정리 명령어
쓰레기통 비우는 명령어

rm -rf ~/.local/share/Trash/files/\* # 혹은 경로에 따라서, rm -rf ~/.local/share/Trash/*

사용하지 않는 패키지 제거

sudo apt-get autoremove

캐시 제거

sync && echo 3 > /proc/sys/vm/drop_caches # 위의 코드가 permission error 나는 경우 sudo sh -c "echo 1 > /proc/sys/vm/drop_caches"

사용전 후 비교

df -h 
