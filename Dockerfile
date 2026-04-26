FROM apache/airflow:2.8.4

USER airflow

# تثبيت dbt ومكتبات الاتصال بقاعدة البيانات والـ API
RUN pip install --no-cache-dir \
    dbt-core==1.8.2 \
    dbt-postgres==1.8.2 \
    requests \
    psycopg2-binary

# إضافة مسار dbt إلى الـ PATH
ENV PATH="${PATH}:/home/airflow/.local/bin"


