
const needle = require('needle');

const rulesURL = 'https://api.twitter.com/2/tweets/search/stream/rules';
const streamURL = 'https://api.twitter.com/2/tweets/search/stream';
const streamURL2 = 'https://api.twitter.com/2/tweets/sample/stream';
var token

async function getAllRules() {

    const response = await needle('get', rulesURL, {
        headers: {
            "authorization": `Bearer ${token}`
        }
    })

    if (response.statusCode !== 200) {
        console.log("Error:", response.statusMessage, response.statusCode)
        throw new Error(response.body);
    }

    return (response.body);
}

async function deleteAllRules(rules) {

    if (!Array.isArray(rules.data)) {
        return null;
    }

    const ids = rules.data.map(rule => rule.id);

    const data = {
        "delete": {
            "ids": ids
        }
    }

    const response = await needle('post', rulesURL, data, {
        headers: {
            "content-type": "application/json",
            "authorization": `Bearer ${token}`
        }
    })

    if (response.statusCode !== 200) {
        throw new Error(response.body);
    }

    return (response.body);

}

async function setRules(rules) {

    const data = {
        "add": rules
    }

    const response = await needle('post', rulesURL, data, {
        headers: {
            "content-type": "application/json",
            "authorization": `Bearer ${token}`
        }
    })

    if (response.statusCode !== 201) {
        throw new Error(response.body);
    }

    return (response.body);

}

function streamConnect(retryAttempt) {

    const stream = needle.get(streamURL, {
        headers: {
            "User-Agent": "v2FilterStreamJS",
            "Authorization": `Bearer ${token}`
        },
        timeout: 20000
    });

    stream.on('data', data => {
        try {
            const json = JSON.parse(data);
            console.log(json);
            // A successful connection resets retry count.
            retryAttempt = 0;
        } catch (e) {
            if (data.detail === "This stream is currently at the maximum allowed connection limit.") {
                console.log(data.detail)
                process.exit(1)
            } else {
                // Keep alive signal received. Do nothing.
            }
        }
    }).on('err', error => {
        if (error.code !== 'ECONNRESET') {
            console.log(error.code);
            process.exit(1);
        } else {
            // This reconnection logic will attempt to reconnect when a disconnection is detected.
            // To avoid rate limits, this logic implements exponential backoff, so the wait time
            // will increase if the client cannot reconnect to the stream. 
            setTimeout(() => {
                console.warn("A connection error occurred. Reconnecting...")
                streamConnect(++retryAttempt);
            }, 2 ** retryAttempt)
        }
    });

    return stream;

}


(async () => {
  const TOKEN = process.env.BEARER_TOKEN
  const USER_NAME = 'business'
  let endpointURL = `https://api.twitter.com/2/users/by/username/${USER_NAME}`
  
  token = TOKEN

  const res = await needle('get', endpointURL, {}, {
    headers: {
        "User-Agent": "v2UserLookupJS",
        "authorization": `Bearer ${token}`
    }
  })

  const user_id = res.body.data.id

  const rules = [
    {
      'value': 'USD -is:retweet lang:en is:verified context:166.*',
      'tag': 'usd'
    },
    {
      'value': 'EUR -is:retweet lang:en is:verified context:166.*',
      'tag': 'eur'
    },
    {
      'value': 'RUB -is:retweet lang:en is:verified context:166.*',
      'tag': 'rub'
    },
    {
      'value': 'AUD -is:retweet lang:en is:verified context:166.*',
      'tag': 'aud'
    },
    {
      'value': 'MXN -is:retweet lang:en is:verified context:166.*',
      'tag': 'mxn'
    },
    {
      'value': 'CAD -is:retweet lang:en is:verified context:166.*',
      'tag': 'cad'
    }
  ];

  let currentRules;

    try {
        // Gets the complete list of rules currently applied to the stream
        currentRules = await getAllRules();

        // Delete all rules. Comment the line below if you want to keep your existing rules.
        await deleteAllRules(currentRules);

        // Add rules to the stream. Comment the line below if you don't want to add new rules.
        await setRules(rules);

    } catch (e) {
        console.error(e);
        process.exit(1);
    }

    // Listen to the stream.
    streamConnect(0);
   
})();
