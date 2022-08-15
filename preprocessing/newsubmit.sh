#!/bin/bash

export SPARK_MASTER_URL=spark://${SPARK_MASTER_NAME}:${SPARK_MASTER_PORT}


/wait-for-step.sh
/execute-step.sh


if [ ! -z "${SPARK_APPLICATION_PYTHON_LOCATION}" ]; then
    echo "Submit application ${SPARK_APPLICATION_PYTHON_LOCATION} to Spark master ${SPARK_MASTER_URL}"
    echo "Passing arguments ${SPARK_APPLICATION_ARGS}"
         /spark/bin/spark-submit \
        --master ${SPARK_MASTER_URL} \
        --archives /app/spark_env.tar.gz#environment \
        ${SPARK_SUBMIT_ARGS} \
        ${SPARK_APPLICATION_PYTHON_LOCATION} ${SPARK_APPLICATION_ARGS}
else
    echo "Not recognized application."
fi


/finish-step.sh