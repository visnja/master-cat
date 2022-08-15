const fs = require('fs');

const util = require('./utils');
const mongo = require('./mongo');
const kafka = require('./kafka');


(async () => {
    
    const connection = mongo.connection
    const kafka_conn = kafka.connection
    await connection.setter()
    await kafka_conn.setter()
    try {
      let conf = await fs.readFileSync(process.argv[2], 'utf-8') 
      conf = JSON.parse(conf)
      await Promise.all(util.processSections(conf.sections, conf))
    } catch(error){
      console.log('error',error)
    }
   
    connection.close();
    kafka_conn.close();
   
})();
