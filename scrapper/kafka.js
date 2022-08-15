const { Kafka } = require('kafkajs')

const kafka = new Kafka({
  clientId: 'my-app',
  brokers: [process.env.KAFKA_URL],
})

let producer;
const connection = (() => {

    const setter = async () => {
        /**
         * Try connecting to the databse
         */
        console.log('Connecting to KAfka')
        try {
            producer = kafka.producer()
            await producer.connect()
            console.log('Connected to KAfka');
        } catch (err) {
            console.error(err)
            throw err
        }

    }

    const getter = () => producer // return the reference to the database
    const close = () => producer.disconnect() // close the connection
    return {
        setter,
        getter,
        close
    }
})()


module.exports = {
 connection,
 kafka
}