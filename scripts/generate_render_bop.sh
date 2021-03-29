set -x
set -u
set -e

for i in {1..1000}
do
    echo "$i"
    CUDA_VISIBLE_DEVICES=$1 python run.py \
    examples/shapenet_with_cctex/config.yaml \
    $2 \
    ~/datasets/shapenet/ShapeNetCore.v2/ \
    /home/qiaog/datasets/cctextures_processed/ \
    $2 \
    resources/cctextures
done