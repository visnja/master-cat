FROM node:11-alpine

#RUN rm /bin/sh && ln -s /bin/bash /bin/sh

ENV CHROME_BIN="/usr/bin/chromium-browser" \
    NODE_ENV="production"

RUN set -x \
    && apk update \
    && apk upgrade \
    && apk add --no-cache \
    dumb-init \
    udev \
    ttf-freefont \
    chromium \
    && npm install puppeteer-core@1.10.0 --silent \
      \
      # Cleanup
      && apk del --no-cache make gcc g++ python binutils-gold gnupg libstdc++ \
      && rm -rf /usr/include \
      && rm -rf /var/cache/apk/* /root/.node-gyp /usr/share/man /tmp/* \
      && echo

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true

COPY package.json /package.json

RUN npm install

COPY hosts.txt  /hosts.txt
VOLUME /configs
COPY ./*.js /

ENV KAFKA_URL "kafka:9092"
ENV MONGO_URL "mongodb://mongodb:27017/crawler"
ENV CONTINUOUS_MODE_ENABLED true
ENV DOCKER true

ENTRYPOINT ["/usr/bin/dumb-init", "--","node","index.js"]
CMD ["configs/reuters.json"]