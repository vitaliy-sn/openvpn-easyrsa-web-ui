FROM python:3.6

RUN python3.6 -m pip install flask uwsgi

RUN curl -sL https://nodejs.org/dist/v8.11.4/node-v8.11.4-linux-x64.tar.xz | tar xJC /usr/local

WORKDIR /app

COPY . /app

RUN export NPM_CONFIG_PREFIX=/root/.npm && \
    export PATH=$PATH:/usr/local/node-v8.11.4-linux-x64/bin && \
    cd /app/frontend && \
    npm install && \
    npm run build && \
    rm -rf /usr/local/node-v8.11.4-linux-x64 /app/frontend/node_modules /root/.npm

CMD uwsgi --uid 7000 --gid 7000 --http :5000  --processes 1 --master --die-on-term --enable-threads \
      --single-interpreter --vacuum --lazy-apps --wsgi-disable-file-wrapper \
      --harakiri 80 -b 32768 --file app.py --callable app --check-static /app/frontend
