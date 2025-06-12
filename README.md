# 테스트

```sh
curl -X POST http://localhost:8001/extract/nlp -H "Content-Type: application/json" -d "{\"text\": \"숨이 차고 가슴이 답답한 느낌이 계속돼요. 특히 계단 오를 때는 더 심해요.\"}"

curl -X POST http://localhost:8001/extract/hybrid -H "Content-Type: application/json" -d "{\"text\": \"숨이 차고 가슴이 답답한 느낌이 계속돼요. 특히 계단 오를 때는 더 심해요.\"}"

curl -X POST http://localhost:8001/extract/llm -H "Content-Type: application/json" -d "{\"text\": \"숨이 차고 가슴이 답답한 느낌이 계속돼요. 특히 계단 오를 때는 더 심해요.\"}"

```


# 실행 방법
```sh
# 1 예측, 추출 서버 실행
cd ai, extract

# 최초 1회
py -3.9 -m venv venv

# 이후부터
source venv/Scripts/activate

pip install -r requirements.txt

py server.py

# 1-1 빠른 실행
cd ai, extract

./start.sh


# 2 웹 실행
cd web

npm install

npm start

# 3 삭제

pip freeze > requirements.txt

# 3-1 삭제
pip freeze > uninstall.txt
pip uninstall -y -r uninstall.txt
```
