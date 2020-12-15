set -x
set -u
set -e

for i in {1..3000}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=2 python run.py \
    examples/shapenet_with_scenenet/config.yaml \
    ~/datasets/generated \
    ~/datasets/shapenet/ShapeNetCore.v2/ \
    ~/datasets/mscoco/train2017 \
    resources/cctextures
done
