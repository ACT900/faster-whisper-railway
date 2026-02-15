FROM ghcr.io/speaches-ai/speaches:0.9.0-rc.3-cpu

COPY auth_wrapper.py /opt/auth/auth_wrapper.py
ENV PYTHONPATH="/opt/auth:${PYTHONPATH}"

CMD ["uvicorn", "--factory", "auth_wrapper:create_app", "--host", "0.0.0.0", "--port", "8000"]
