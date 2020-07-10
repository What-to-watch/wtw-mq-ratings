FROM python:3.7-alpine
RUN apk add --no-cache gcc musl-dev linux-headers postgresql-libs postgresql-dev
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD ["python","-u","./subscriber.py"]