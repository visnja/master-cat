const kafka = require('./kafka').kafka
const fs = require('fs');
const util = require('./utils');
const mongo = require('./mongo');
const rxjs = require('rxjs');
const {mergeMap, toArray} = require('rxjs/operators')

function randomNumber(min, max) {
  return Math.random() * (max - min) + min
}
const withBrowser = async (fn) => {
  const {browser} = await util.launchBrowser()
  try {
    return await fn(browser)
  } finally {
    await browser.close()
  }
}

const withPage = (browser) => async (fn) => {
  const page = await browser.newPage()
  await page.setViewport({ width: 1920, height: 1080 });
  await page.setRequestInterception(true);
  try {
    return await fn(page)
  } finally {
    await page.close()
  }
}


(async () => {
    
  const connection = mongo.connection
  await connection.setter()
  let conf = await fs.readFileSync(process.argv[2], 'utf-8') 
  conf = JSON.parse(conf)
  let articles = await mongo.getArticlesByWebsite(conf.name)
  articles = await articles.toArray()
  const results = await withBrowser((browser) => {
    return rxjs.from(articles).pipe(
      mergeMap(async (article) => {
        return withPage(browser)(async (page)=>{
          try {
            const url = article.url
            console.time(url)
            let msg = {}
            if (url){
              await util.navigateAndSleep(page,url)
              await page.waitForTimeout(randomNumber(1,2)*1000)
              await util.crawlArticle(msg, page, conf)
              await mongo.updateItem({...article,...msg})
            }
            console.timeEnd(url)
            return {...article,...msg}
          }catch(err){
            console.log(err)
            return {...article}
          }
        })
      },3), toArray()
    ).toPromise()
  })

  console.log(results)
  connection.close();
   
})();
