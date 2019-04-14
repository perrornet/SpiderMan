FROM perrorone/spiderman
LABEL Name=spiderman Version=0.0.1

WORKDIR /SpiderMan
ADD . /SpiderMan
EXPOSE 8080
RUN /root/anaconda3/envs/spderman/bin/python setup.py install
CMD ["/root/anaconda3/envs/spderman/bin/SpiderMan", "init"]
