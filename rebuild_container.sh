#!/bin/bash
imageName=single
containerName=single

docker build -t $imageName -f single_tile_tagging/Dockerfile-single-tile  ./single_tile_tagging/

echo Delete old container...
docker rm -f $containerName

echo Run new container...
docker run --network=vgac-network --name $containerName $imageName