// URL at which MongoDB service is running
let MONGO_URL = String(process.env.MONGO_URL);


// A Client to MongoDB
let MongoClient = require('mongodb').MongoClient;


// Make a connection to MongoDB Service

const client = new MongoClient(MONGO_URL, {
  useUnifiedTopology: true,
  useNewUrlParser: true,
});
let db;
const connection = (() => {

  const setter = async () => {
    /**
     * Try connecting to the databse
     */
    console.log('Connecting to MongoDB')
    try {
      db = await client.connect()
      db = db.db()
      console.log('Connected to MongoDB');
    } catch (err) {
      console.error(err)
      throw err
    }

  }

  const getter = () => db // return the reference to the database
  const close = () => client.close() // close the connection
  return {
    setter,
    getter,
    close
  }
})()

async function saveItems(items) {
  if (db) {
    let saved = await db.collection('contents').find({ url: { $in: items.map(u => u.url) } });
    saved = await saved.toArray();
    if (saved.length === items.length) {
      console.log('Already saved all items')
      return null;
    }
    items = items.filter(item => !saved.some(x => x.url === item.url))
    items.forEach(article => {
      article.visited = false;
      article.created_at = new Date()
    })
    console.log(items.length, 'to save')
    if (items.length === 0) {
      if (!process.env.CONTINUOUS_MODE_ENABLED) {
        return null

      } else {
        throw new Error('Stopping criteria')
      }

    }
    await db.collection('contents').insertMany(items, {})
    return items
  }
  return items

}

async function updateItem(item) {
  await db.collection('contents').updateOne({ _id: item._id }, { $set: item })
}

async function getNonVisitedArticlesByWebsite(website) {
  return db.collection('contents').find({ visited: false, source: website })
}
async function getArticlesByWebsite(website) {
  return db.collection('contents').find({ source: website, body: { $exists: false }, url: { $exists: true } })
}

module.exports = {
  connection,
  saveItems,
  getNonVisitedArticlesByWebsite,
  updateItem,
  getArticlesByWebsite
}