# Use an official Python runtime as a parent image
FROM python:3.12.2

ADD asr_api.py .
ADD requirements.txt .

# Install needed dependencies in requirements.txt
RUN pip install -r requirements.txt

EXPOSE 8001

# Run the API service when the container launches
CMD ["python", "./asr_api.py"]
