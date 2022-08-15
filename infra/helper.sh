clusterID=$(docker exec `docker ps -aqf "name=namenode"` bash -c "cat /hadoop/dfs/name/current/VERSION | grep -oP 'clusterID=\K([A-Z-a-z0-9-]*)'")
echo $clusterID
sed -i "s/clusterID=.*/clusterID=$clusterID/" datanode1/current/VERSION && cat datanode1/current/VERSION
sed -i "s/clusterID=.*/clusterID=$clusterID/" datanode2/current/VERSION && cat datanode2/current/VERSION
sed -i "s/clusterID=.*/clusterID=$clusterID/" datanode3/current/VERSION && cat datanode3/current/VERSION