FROM python:3
ADD receiveSubscribe.py /
ADD requirements.txt /
RUN pip install -r requirements.txt
CMD ["python", "./receiveSubscribe.py"]
