export MONGO_URL=mongodb://localhost:27017/crawler
export KAFKA_URL=localhost:19092
export CONTINUOUS_MODE_ENABLED=1

node index.js configs/cnbc.json
node index.js configs/dailyfx.json
node index.js configs/forex.json
node index.js configs/forexcrunch.json
node index.js configs/fxempire.json
node index.js configs/investing.json
node index.js configs/marketpulse.json
node index.js configs/marketwatch.json
node index.js configs/reuters.json


node crawler.js configs/cnbc.json
node crawler.js configs/dailyfx.json
node crawler.js configs/forex.json
node crawler.js configs/forexcrunch.json
node crawler.js configs/fxempire.json
node crawler.js configs/investing.json
node crawler.js configs/marketpulse.json
node crawler.js configs/marketwatch.json
node crawler.js configs/reuters.json
node crawler.js configs/fxstreet.json

# node scrapper.js