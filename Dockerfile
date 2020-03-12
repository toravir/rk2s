FROM swaggerapi/swagger-codegen-cli:latest as swaggerBuild
RUN java -jar /opt/swagger-codegen-cli/swagger-codegen-cli.jar generate -i https://developers.strava.com/swagger/swagger.json -l python -o /genpy

FROM python:2.7
WORKDIR /apis/
COPY --from=swaggerBuild /genpy .
RUN pip install -r requirements.txt
RUN python setup.py install
RUN pip install requests 
COPY rk2s.py /rk2s.py
ENTRYPOINT ["python", "/rk2s.py"]
