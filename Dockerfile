FROM python:3.12.12-slim@sha256:f3fa41d74a768c2fce8016b98c191ae8c1bacd8f1152870a3f9f87d350920b7c AS build
WORKDIR /build
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY app/ /build/app/
RUN python -m compileall -q /build/app
FROM python:3.12.12-slim@sha256:f3fa41d74a768c2fce8016b98c191ae8c1bacd8f1152870a3f9f87d350920b7c AS runtime
WORKDIR /app
RUN mkdir -p /data /app/logs && chown -R 10001:10001 /data /app/logs && chmod 700 /app/logs
COPY --from=build /build/app/ /app/
USER 10001:10001
ENV PORT=8080 BIND_HOST=0.0.0.0 DB_PATH=/data/notes.db
EXPOSE 8080
CMD ["python3", "app.py"]
