set -x
set -u
set -e

for i in {1..3000}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=0 python run.py \
    examples/shapenet_with_scenenet/config.yaml \
    ~/datasets/render/shapenet/ \
    ~/datasets/shapenet/ShapeNetCore.v2/ \
    ~/datasets/mscoco/train2017 \
    resources/objs.txt \
    resources/cctextures
done
