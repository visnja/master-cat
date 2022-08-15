const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
const AdblockerPlugin = require('puppeteer-extra-plugin-adblocker');
puppeteer.use(StealthPlugin());
puppeteer.use(AdblockerPlugin())

const rxjs = require('rxjs');
const { mergeMap, toArray } = require('rxjs/operators')
const url = require('url');
const fs = require('fs')
const kafka = require('./kafka')
const mongo = require('./mongo');

const SLEEP_MS = Number.parseInt(process.env.SLEEP_MS) || 5000;
const MAX_PAGES = Number.parseInt(process.env.MAX_PAGES) || 100;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getAttributeValue(handler, config, item) {
  try {
    if (!config.selector) {
      let val = await handler.getProperty(config.attribute)
      if (!item[config.name]) {
        item[config.name] = await val.jsonValue()
      }
    }
    waitForSelector(handler, config.selector)

    let handle = await handler.$(config.selector)
    if (handle) {
      const value = await handle.getProperty(config.attribute);

      if (!item[config.name]) {
        item[config.name] = await value.jsonValue()
      }
      if (!item[config.name]) {
        item[config.name] = await handler.$eval(config.selector, (node, config) => node.getAttribute(config.attribute), config);
      }
      await handle.dispose();
    }

  } catch (err) {
    if (err.message) {
      console.debug(err.message)
    }
    return;
  }

}

async function getSelectorValue(handler, config, item) {
  try {
    if (config.multiple) {
      item[config.name] = await handler.$$eval(config.selector, node => {
        return node.map(p => p.innerText);
      });
      return
    }
    if (!config.selector) {
      if (!item[config.name]) {
        item[config.name] = await handler.evaluate(node => node.innerText);
      }
      return
    }
    if (!item[config.name]) {
      try {
        item[config.name] = await handler.$eval(config.selector, node => node.innerText);
      } catch (err) {
        console.debug('Issue getting value: ', err.message)
      }
    }
  } catch (err) {
    console.debug(err)
    return;
  }

}

async function processConfig(config, page, item) {
  typeof config.selector == 'object' ? await processArticles(config, page, item) : null
  Array.isArray(config) ? await processArrayConfig(config, page, item) : null
  config.attribute && config.name ? await getAttributeValue(page, config, item) : null
  config.name ? await getSelectorValue(page, config, item) : null
}

async function waitForSelector(page, selector) {
  typeof page.waitForSelector === 'function' ? await page.waitForSelector(selector) : await sleep(SLEEP_MS)
}

async function processArticles(config, handle, item) {

  console.debug('Querying for', config.selector.parent)

  waitForSelector(handle, config.selector.parent)
  let holder = await handle.$(config.selector.parent)

  if (!holder) {
    holder = handle;
  }
  let articles = await holder.$$(config.selector.child)

  item.children = []
  await Promise.all(articles.map(async (article) => {
    let child = {}
    await processConfig(config.content, article, child)
    if (child.children) {
      item.children = child.children.concat(item.children)
    }
    delete child.children
    item.children.push(child)

  }))
}

async function processArrayConfig(config, page, item) {
  await Promise.all(
    config.map(async conf => {
      await processConfig(conf, page, item);
    })
  );
}

async function crawlPage(page, section) {
  console.debug('Started crawling')
  let articles = section.articles
  let items = []
  await Promise.all(articles.map(async conf => {
    let item = {}
    await processConfig(conf, page, item);
    items = item.children ? items.concat(item.children) : items
  }));
  return items
}

async function navigateAndSleep(page, url) {
  for (let i = 0; i < 5; i++) {
    try {
      await page.goto(url, { waitUntil: 'domcontentloaded' })
      break;
    } catch (e) {
      console.debug("retry no", i)
      continue;
    }
  }
}

async function navigateNextPageAndSleep(page, config) {
  try {
    console.debug('Navigating next page')
    if (!config.next_page) {
      let u = new url.URL(page.url());
      let reg = new RegExp(config.pattern)
      let _num = Number.parseInt(reg.exec(u.href)[1])
      u.href = u.href.replace(_num, ++_num)
      await navigateAndSleep(page, u.href)
      return true
    }

    if (typeof config.next_page === 'object' && config.next_page.type === 'url') {
      let u = new url.URL(page.url());

      if (!u.searchParams.get(config.next_page.key)) {
        u.search = `${config.next_page.key}=${config.next_page.value}`;
      } else {
        let val = Number.parseInt(u.searchParams.get(config.next_page.key))
        u.searchParams.set(config.next_page.key, ++val)
      }

      await navigateAndSleep(page, u.href)

      return true;
    }

    if (config.next_page.selector) {
      await page.waitForSelector(config.next_page.selector, { visible: true, timeout: 10000 })
      let next = await page.$(config.next_page.selector)
      await next.click()
    }

  } catch (err) {
    console.error('Navigation error', err.message)
    return false
  }
  await page.waitForTimeout(SLEEP_MS)
  return true

}

function processSections(sections, config) {
  console.debug('Processing sections')
  return sections.map(async section => {
    await processUrls(section.paths.map(path => config.host + path), config, section)
  })
}

async function launchBrowser() {
  const options = {
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--window-size=1920x1200',
      '--disable-dev-shm-usage',
      '--ignore-certificate-errors',
      '--shm-size=3gb']
  }

  if (process.env.DOCKER) {
    options.executablePath = process.env.CHROME_BIN || null
    options.headless = true
  }
  return { browser: await puppeteer.launch(options) }
}

function scrollToBottom(page) {
  return () => {
    try {
      page.evaluate(() => window.scrollTo(0, document.body.scrollHeight)).then(() => {
        console.debug('Scrolled to bottom')
      })
    } catch (err) {
      console.error('Scroll to bottom ERROR: ', err)
    }
  }

}

var hostFile = fs.readFileSync('./hosts.txt', 'utf8').split('\n');

var hosts = {};
for (var i = 0; i < hostFile.length; i++) {
  var frags = hostFile[i].split(' ');
  if (frags.length > 1 && frags[0] === '0.0.0.0') {
    hosts[frags[1].trim()] = true;
  }
}


function processUrls(urls, conf, section) {

  return withBrowser((browser) => {
    return rxjs.from(urls).pipe(
      mergeMap(async (url) => {
        return withPage(browser)(async page => {
          await navigateAndSleep(page, url.includes("#PAGE_INDEX#") ? url.replace("#PAGE_INDEX#", "1") : url)

          conf.initial_sleep ? await page.waitForTimeout(5 * SLEEP_MS) : await page.waitForTimeout(SLEEP_MS)

          let total = []
          for (let i = 0; i < MAX_PAGES; i++) {
            try {
              let items = [];

              if (section.infinite_scroll) {
                await page.hover(section.infinite_scroll.selector);
                await page.waitForSelector(section.infinite_scroll.selector);
              }
              items = await crawlPage(page, section);
              console.debug('Found ', items.length, 'items at ', page.url())
              items.forEach(item => item.source = conf.name)
              producer = kafka.connection.getter()

              items.forEach((item) => {
                producer.send({
                  topic: 'test-topic',
                  messages: [
                    { value: JSON.stringify(item) },
                  ]
                })
              })

              let saved = await mongo.saveItems(items)

              if (!saved) {
                console.debug("All items are visited")
                break
              } else {
                total = total.concat(saved)
              }

              let res = await navigateNextPageAndSleep(page, conf, section);
              if (conf.initial_sleep) {
                await page.waitForTimeout(3 * SLEEP_MS);
              }

              if (!res) {
                console.debug('Stopped at page: ', i)
                break
              }
            } catch (err) {
              console.debug(err.message)
              break;
            }
          }
        })
      }, 3), toArray()
    ).toPromise()
  })
}

async function crawlArticle(article, page, config) {
  await processArrayConfig(config.content, page, article);
}


const withBrowser = async (fn) => {
  const { browser } = await launchBrowser()
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
  const scroller = scrollToBottom(page)
  page.on('domcontentloaded', scroller)
  try {
    return await fn(page)
  } finally {
    await page.close()
    page.off('domcontentloaded', scroller)
  }
}

module.exports = {
  processSections,
  processConfig,
  launchBrowser,
  getAttributeValue,
  crawlArticle,
  navigateAndSleep
}