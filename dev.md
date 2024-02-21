# 开发
1. 设置开发环境:
```bash
export PYTHONPATH=$PYTHONPATH:/xxx/game-npc
```
2. 安装依赖：
```bash
pip install -r requirements-dev.txt
```

创建一个虚拟环境:
```bash
python3 -m venv python-env
source python-env/bin/activate
```


# 推送代码仓库
1. 推送代码到GitHub上。
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<username>/game-npc.git
git push -u origin master
```

2. 命令打包,发布你的包到PyPi：
```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

# 部署服务
1、启动后端:
```bash
export VOLC_ACCESSKEY=xxxxxx
export VOLC_SECRETKEY=xxxxxxxx
export ES_URL=xxxxxxxxx
```