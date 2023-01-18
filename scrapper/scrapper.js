const kafka = require('./kafka').kafka

const util = require('./utils');
const fs = require('fs');
const config = async (src) => {
  let base = src.replace(".com",".json")
  let path = "configs/" + base
  let conf = await fs.readFileSync(path, 'utf-8') 
  conf = JSON.parse(conf)
  return conf

}

function randomNumber(min, max) {
  return Math.random() * (max - min) + min
}


(async () => {
  
  const consumer = kafka.consumer({groupId: 'test'})
  await consumer.connect()
  await consumer.subscribe({topic: 'test-topic', fromBeginning: true})
  
  const { browser } = await util.launchBrowser()

  await consumer.run(
    {
      eachMessage: async ({topic, partition, message}) => {
        let page = await browser.newPage()
        let msg = JSON.parse(message.value.toString())
        let conf = await config(msg.source)
        await page.waitForTimeout(randomNumber(1,3)*3000)
        await page.goto(msg.url, {waitUntil: 'domcontentloaded'})
        await util.crawlArticle(msg, page, conf)
        console.log(msg)
       
        await page.close()
      }
    }
  )
   
})();
